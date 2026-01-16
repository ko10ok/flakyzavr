import re
from typing import Type
from typing import Union

from jira import JIRA
from vedro.core import Dispatcher
from vedro.core import Plugin
from vedro.core import PluginConfig
from vedro.core import ScenarioResult
from vedro.core import VirtualScenario
from vedro.events import ScenarioFailedEvent
from vedro.events import ScenarioPassedEvent

from flakyzavr._jira_stdout import JiraUnavailable
from flakyzavr._jira_stdout import LazyJiraTrier
from flakyzavr._messages import RU_REPORTING_LANG
from flakyzavr._messages import ReportingLangSet
from flakyzavr._traceback import render_error
from flakyzavr._traceback import render_tb

__all__ = ("Flakyzavr", "FlakyzavrPlugin",)


class FlakyzavrPlugin(Plugin):
    def __init__(self, config: Type["Flakyzavr"]) -> None:
        super().__init__(config)
        self._report_enabled = config.report_enabled

        self._jira_server = config.jira_server
        self._jira_token = config.jira_token
        self._jira_project = config.jira_project
        self._jira_labels = config.jira_labels
        self._jira_components = config.jira_components
        self._jira: JIRA | LazyJiraTrier | None = None
        self._report_project_name = config.report_project_name
        self._job_path = config.job_path
        self._job_id = config.job_id
        self._job_full_path = config.job_path.format(job_id=config.job_id)
        self._dry_run = config.dry_run
        self._jira_search_statuses = config.jira_search_statuses
        self._exceptions = config.exceptions
        self._jira_search_forbidden_symbols = config.jira_search_forbidden_symbols
        self._jira_flaky_label = config.jira_flaky_label
        self._reporting_language = config.reporting_language
        self._jira_additional_data = config.jira_additional_data
        self._jira_issue_type_id = config.jira_issue_type_id

    def subscribe(self, dispatcher: Dispatcher) -> None:
        if self._report_enabled:
            dispatcher.listen(ScenarioFailedEvent, self.on_scenario_failed)

    def _make_new_issue_summary_for_test(self, test_name: str, priority: str) -> str:
        return self._reporting_language.NEW_ISSUE_SUMMARY.format(
            project_name=self._report_project_name,
            test_name=test_name,
            priority=priority,
        )

    def _get_scenario_priority(self, scenario: VirtualScenario) -> str:
        template = getattr(scenario._orig_scenario, "__vedro__template__", None)

        labels = getattr(template, "__vedro__allure_labels__", ())
        labels += getattr(scenario._orig_scenario, "__vedro__allure_labels__", ())

        for label in labels:
            if label.name == 'priority':
                return label.value

        return 'NOT_SET_PRIORITY'

    def _make_new_issue_description_for_test(self, scenario_result: ScenarioResult) -> str:
        test_name = scenario_result.scenario.subject
        test_file = str(scenario_result.scenario.rel_path)
        priority = self._get_scenario_priority(scenario_result.scenario)
        fail_error = scenario_result._step_results[-1].exc_info.value
        fail_traceback = scenario_result._step_results[-1].exc_info.traceback
        description = self._reporting_language.NEW_ISSUE_TEXT.format(
            test_name=test_name,
            test_file=test_file,
            priority=priority,
            traceback=render_tb(fail_traceback, test_file=test_file),
            error=render_error(fail_error),
            job_link=self._job_full_path
        )
        return description

    def _make_jira_comment(self, scenario_result: ScenarioResult) -> str:
        test_name = scenario_result.scenario.subject
        priority = self._get_scenario_priority(scenario_result.scenario)
        fail_error = scenario_result._step_results[-1].exc_info.value
        fail_traceback = scenario_result._step_results[-1].exc_info.traceback
        return self._reporting_language.NEW_COMMENT_TEXT.format(
            test_name=test_name,
            priority=priority,
            job_link=self._job_full_path,
            traceback=render_tb(fail_traceback, test_file=str(scenario_result.scenario.rel_path)),
            error=render_error(fail_error),
        )

    def on_scenario_failed(self, event: Union[ScenarioPassedEvent, ScenarioFailedEvent]) -> None:
        self._jira = LazyJiraTrier(
            self._jira_server,
            token=self._jira_token,
            dry_run=self._dry_run
        )

        fail_error = str(event.scenario_result._step_results[-1].exc_info.value)
        for exception_error in self._exceptions:
            if re.search(exception_error, fail_error):
                event.scenario_result.add_extra_details(self._reporting_language.FILTERED_OUT_BY_EXCEPTION_REGEXP)
                return

        test_name = event.scenario_result.scenario.subject
        test_file = str(event.scenario_result.scenario.rel_path)

        statuses = ",".join([f'"{status}"' for status in self._jira_search_statuses])
        search_prompt = (
            f'project = {self._jira_project} '
            f'and description ~ "\\"{test_file}\\"" '
            f'and status in ({statuses}) '
            f'and labels = {self._jira_flaky_label} '
            'ORDER BY created'
        )

        found_issues = self._jira.search_issues(jql_str=search_prompt)
        if isinstance(found_issues, JiraUnavailable):
            event.scenario_result.add_extra_details(
                self._reporting_language.SKIP_CREATING_ISSUE_DUE_TO_JIRA_SEARCH_UNAVAILABILITY.format(
                    jira_server=self._jira_server
                )
            )
            return

        if found_issues:
            issue = found_issues[0]  # type: ignore
            comment = self._make_jira_comment(event.scenario_result)
            result = self._jira.add_comment(issue, comment)
            if isinstance(result, JiraUnavailable):
                event.scenario_result.add_extra_details(
                    self._reporting_language.SKIP_CREATING_COMMENT_IN_EXISTING_ISSUE_DUE_TO_JIRA_UNAVAILABILITY.format(
                        jira_server=self._jira_server
                    )
                )
                return

            event.scenario_result.add_extra_details(
                self._reporting_language.ISSUE_ALREADY_EXISTS.format(jira_server=self._jira_server, issue_key=issue.key)
            )
            return

        priority = self._get_scenario_priority(event.scenario_result.scenario)
        issue_name = self._make_new_issue_summary_for_test(test_name, priority)
        issue_description = self._make_new_issue_description_for_test(event.scenario_result)
        jira_labels = self._jira_labels
        if self._jira_flaky_label not in self._jira_labels:
            jira_labels += [self._jira_flaky_label]
        created_ticket_fields = {
                'project': {'key': self._jira_project},
                'summary': issue_name,
                'description': issue_description,
                'issuetype': {'id': self._jira_issue_type_id},
                'components': [{'name': component} for component in self._jira_components],
                'labels': jira_labels,
            }
        if self._jira_additional_data:
            created_ticket_fields.update(self._jira_additional_data)
        result_issue = self._jira.create_issue(fields=created_ticket_fields)
        if isinstance(result_issue, JiraUnavailable):
            event.scenario_result.add_extra_details(
                self._reporting_language.SKIP_CREATING_ISSUE_DUE_TO_JIRA_CREATE_UNAVAILABILITY.format(
                    jira_server=self._jira_server
                )
            )
            return

        event.scenario_result.add_extra_details(
            self._reporting_language.ISSUE_CREATED.format(jira_server=self._jira_server, issue_key=result_issue.key)
        )


class Flakyzavr(PluginConfig):
    plugin = FlakyzavrPlugin
    description = "Report failed tests to Jira"

    enabled = True
    report_enabled = False  # enable it when flaky run

    jira_server: str = 'https://NOT_SET'
    jira_token: str = 'NOT_SET'
    jira_project: str = 'NOT_SET'
    jira_components: list[str] = []
    jira_labels: list[str] = []
    jira_flaky_label: str = 'flaky'

    jira_search_statuses: list[str] = ['Взят в бэклог', 'Open', 'Reopened', 'In Progress',
                                       'Code Review', 'Resolved', 'Testing']
    jira_search_forbidden_symbols: list[str] = ['[', ']', '"']
    # additional data for created jira issue: {'field_id': 'value'}
    # Example: {'customfield_10000': 'test'}
    jira_additional_data: dict[str, str] = {}
    jira_issue_type_id: str = '3'
    report_project_name: str = 'NOT_SET'
    job_path = '{job_id}'
    job_id: str = 'NOT_SET'

    dry_run: bool = True

    exceptions: list[str] = [r'.*codec can\'t decode byte.*']

    reporting_language: ReportingLangSet = RU_REPORTING_LANG
