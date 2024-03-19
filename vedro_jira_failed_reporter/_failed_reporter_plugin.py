from copy import deepcopy
from typing import Type
from typing import Union

from jira import JIRA
from vedro.core import Dispatcher
from vedro.core import Plugin
from vedro.core import PluginConfig
from vedro.core import ScenarioResult
from vedro.events import ScenarioFailedEvent
from vedro.events import ScenarioPassedEvent
from vedro.events import VirtualScenario  # type: ignore

from vedro_jira_failed_reporter._jira_stdout import JiraUnavailable
from vedro_jira_failed_reporter._jira_stdout import LazyJiraTrier
from vedro_jira_failed_reporter._jira_stdout import StdoutJira
from vedro_jira_failed_reporter.traceback import render_error
from vedro_jira_failed_reporter.traceback import render_tb

__all__ = ("FailedJiraReporter", "FailedJiraReporterPlugin",)


class FailedJiraReporterPlugin(Plugin):
    def __init__(self, config: Type["FailedJiraReporter"]) -> None:
        super().__init__(config)
        self._report_enabled = config.report_enabled

        self._jira_server = config.jira_server
        self._jira_user = config.jira_user
        self._jira_password = config.jira_password
        self._jira_project = config.jira_project
        self._jira_labels = config.jira_labels
        self._jira_components = config.jira_components
        self._jira: JIRA | StdoutJira | LazyJiraTrier = StdoutJira()
        self._report_project_name = config.report_project_name
        self._job_path = config.job_path
        self._job_id = config.job_id
        self._job_full_path = config.job_path.format(job_id=config.job_id)
        self._dry_run = config.dry_run
        self._jira_search_statuses = config.jira_search_statuses
        self._exceptions = config.exceptions
        self._jira_search_forbidden_symbols = config.jira_search_forbidden_symbols

    def subscribe(self, dispatcher: Dispatcher) -> None:
        if self._report_enabled:
            dispatcher.listen(ScenarioFailedEvent, self.on_scenario_failed)

    def _make_search_issue_for_test(self, test_name: str) -> str:
        filtered_test_name = deepcopy(test_name)
        for char in self._jira_search_forbidden_symbols:
            filtered_test_name = filtered_test_name.replace(char, '.')
        return f'{filtered_test_name}'
        # return f'Флаки тест {test_name}'

    def _make_new_issue_summary_for_test(self, test_name: str, priority: str) -> str:
        return f'[{self._report_project_name}] Флаки тест {test_name} ({priority})'

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
        priority = self._get_scenario_priority(scenario_result.scenario)
        fail_error = scenario_result._step_results[-1].exc_info.value
        fail_traceback = scenario_result._step_results[-1].exc_info.traceback
        description = f'''
h2. {{color:#172b4d}}Контекст{{color}}
Флаки тест 
{{code:python}}
{test_name}
{{code}}
Приоритет теста - {priority}
{{code:python}}
{render_tb(fail_traceback)}
{'-' * 80}
{render_error(fail_error)}
{{code}}
h2. {{color:#172b4d}}Что нужно сделать{{color}}
{{task}}Заскипать vedro-flaky-steps плагином место падения{{task}}
{{task}}Разобраться в причине падения и починить тест по необходимости{{task}}
        '''
        return description

    def _make_jira_comment(self, scenario_result: ScenarioResult) -> str:
        test_name = scenario_result.scenario.subject
        priority = self._get_scenario_priority(scenario_result.scenario)
        fail_error = scenario_result._step_results[-1].exc_info.value
        fail_traceback = scenario_result._step_results[-1].exc_info.traceback
        return f'''
Повторный флак
Приоритет теста - {priority}
{self._job_full_path}
{{code:python}}
{render_tb(fail_traceback)}
{'-' * 80}
{render_error(fail_error)}
{{code}}
        '''

    def on_scenario_failed(self, event: Union[ScenarioPassedEvent, ScenarioFailedEvent]) -> None:
        self._jira = LazyJiraTrier(self._jira_server, basic_auth=(self._jira_user, self._jira_password))

        fail_error = str(event.scenario_result._step_results[-1].exc_info.value)
        import re
        for exception_error in self._exceptions:
            if re.search(exception_error, fail_error):
                event.scenario_result.add_extra_details(
                    f'Флаки тикета не будет создно. Падение отфильтровано по списку исключений.'
                )
                return

        test_name = event.scenario_result.scenario.subject

        statuses = ",".join([f'"{status}"' for status in self._jira_search_statuses])
        search_prompt = (
            f'project = {self._jira_project} '
            f'and text ~ "{self._make_search_issue_for_test(test_name)}" '
            f'and status in ({statuses}) '
            'ORDER BY created'
        )

        found_issues = self._jira.search_issues(jql_str=search_prompt)
        if isinstance(found_issues, JiraUnavailable):
            event.scenario_result.add_extra_details(
                f'{self._jira_server} не был доступен во время поиска тикетов. '
                f'Пропускаем создание тикета для текущего теста'
            )
            return

        if found_issues:
            issue = found_issues[0]  # type: ignore
            comment = self._make_jira_comment(event.scenario_result)
            result = self._jira.add_comment(issue, comment)
            if isinstance(result, JiraUnavailable):
                event.scenario_result.add_extra_details(
                    f'{self._jira_server} не был доступен во время добавления комментария о флакующем тесте. Пропускаем создание коментария для текущего теста'
                )
                return

            event.scenario_result.add_extra_details(
                f'Флаки тикет уже есть {self._jira_server}/browse/{issue.key}'
            )
            return

        priority = self._get_scenario_priority(event.scenario_result.scenario)
        issue_name = self._make_new_issue_summary_for_test(test_name, priority)
        issue_description = self._make_new_issue_description_for_test(event.scenario_result)
        result_issue = self._jira.create_issue(
            fields={
                'project': {'key': self._jira_project},
                'summary': issue_name,
                'description': issue_description,
                'issuetype': 'Task',
                'components': [{'name': component} for component in self._jira_components],
                'labels': self._jira_labels,
            }
        )
        if isinstance(result_issue, JiraUnavailable):
            event.scenario_result.add_extra_details(
                f'{self._jira_server} не был доступен во время мсоздания тикета на флак теста. '
                f'Пропускаем создание тикета для текущего теста'
            )
            return
        event.scenario_result.add_extra_details(
            f'Заведен новый флаки тикет {self._jira_server}/browse/{result_issue.key}'
        )


class FailedJiraReporter(PluginConfig):
    plugin = FailedJiraReporterPlugin
    description = "Report to jira about failed tests"

    enabled = True
    report_enabled = False  # enable it when flaky run

    jira_server: str = 'https://NOT_SET'
    jira_user: str = 'NOT_SET'
    jira_password: str = 'NOT_SET'
    jira_project: str = 'NOT_SET'
    jira_components: list[str] = []
    jira_labels: list[str] = []

    jira_search_statuses: list[str] = ['Взят в бэклог', 'Open', 'Reopened', 'In Progress']
    jira_search_forbidden_symbols: list[str] = ['[', ']', '"']
    report_project_name: str = 'NOT_SET'
    job_path = 'NOT_SET'
    job_id: str = 'NOT_SET'

    dry_run: bool = True

    exceptions: list[str] = [r'.*codec can\'t decode byte.*']
