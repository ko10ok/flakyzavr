from typing import Any
from typing import Type
from typing import Union

from jira import JIRA
from jira import Issue
from vedro.core import Dispatcher
from vedro.core import Plugin
from vedro.core import PluginConfig
from vedro.core import ScenarioResult
from vedro.events import ScenarioFailedEvent
from vedro.events import ScenarioPassedEvent
from vedro.events import StartupEvent
from vedro.events import VirtualScenario  # type: ignore

__all__ = ("FailedJiraReporter", "FailedJiraReporterPlugin",)


class StdoutJira:
    def search_issues(self, prompt: str) -> list[Issue]:
        return []

    def add_comment(self, issue: Issue, comment: str) -> None:
        print(Issue, comment)

    def create_issue(self, fields: dict[str, Any]) -> None:
        print(fields)


class FailedJiraReporterPlugin(Plugin):
    def __init__(self, config: Type["FailedJiraReporter"]) -> None:
        super().__init__(config)
        self._report_enabled = config.report_enabled

        self._jira_server = config.jira_server
        self._jira_user = config.jira_user
        self._jira_password = config.jira_password
        self._jira_project = config.jira_project
        self._jira_tags = config.jira_tags
        self._jira: JIRA | StdoutJira = StdoutJira()
        self._report_project_name = config.report_project_name
        self._job_path = config.job_path
        self._job_id = config.job_id
        self._job_full_path = config.job_path.format(job_id=config.job_id)
        self._dry_run = config.dry_run
        self._priority_type = config.priority_type

    def subscribe(self, dispatcher: Dispatcher) -> None:
        if self._report_enabled:
            dispatcher \
                .listen(StartupEvent, self.on_startup) \
                .listen(ScenarioFailedEvent, self.on_scenario_failed)

    def on_startup(self, event: StartupEvent) -> None:
        if not self._dry_run:
            self._jira = JIRA(self._jira_server, basic_auth=(self._jira_user, self._jira_password))

    def _make_search_issue_for_test(self, test_name: str) -> str:
        return f'Флаки тест {test_name}'

    def _make_new_issue_summary_for_test(self, test_name: str, priority: str) -> str:
        return f'[{self._report_project_name}] Флаки тест {test_name} ({priority})'

    def _make_new_issue_description_for_test(self) -> str:
        return 'здесь могло бы быть тело вашего тикета'

    def _make_jira_comment(self, scenario_result: ScenarioResult, priority: str) -> str:
        return f'''
            Теста приоритета {priority}\n
            Падал в {self._job_full_path}:\n
            {{code:python}}
            {scenario_result}
            {{code}}
            '''

    def _get_scenario_priority(self, scenario: VirtualScenario) -> str:
        # TODO check self._priority_type tag
        # tags = getattr(scenario._orig_scenario, "tags", ())
        return 'NOT_SET'

    def on_scenario_failed(self, event: Union[ScenarioPassedEvent, ScenarioFailedEvent]) -> None:
        test_name = event.scenario_result.scenario.name
        test_priority = self._get_scenario_priority(event.scenario_result.scenario)
        search_prompt = (f'project = {self._jira_project} '
                         f'and text ~ "{self._make_search_issue_for_test(test_name)}" '
                         'ORDER BY created')

        found_issues = self._jira.search_issues(search_prompt)

        if found_issues:
            issue = found_issues[0]  # type: ignore
            comment = self._make_jira_comment(event.scenario_result, test_priority)
            self._jira.add_comment(issue, comment)
            return

        issue_name = self._make_new_issue_summary_for_test(test_name, test_priority)
        issue_description = self._make_new_issue_description_for_test()
        self._jira.create_issue(
            fields={
                'project': {'key': self._jira_project},
                'summary': issue_name,
                'description': issue_description
            }
        )


class FailedJiraReporter(PluginConfig):
    plugin = FailedJiraReporterPlugin
    description = "Report to jira about failed tests"

    enabled = True
    report_enabled = False

    jira_server: str = 'https://NOT_SET'
    jira_user: str = 'NOT_SET'
    jira_password: str = 'NOT_SET'
    jira_project: str = 'NOT_SET'

    jira_tags: list[str] = ['flaky', 'tech_debt_qa']

    report_project_name: str = 'NOT_SET'
    job_path = 'NOT_SET'
    job_id: str = 'NOT_SET'

    dry_run: bool = True

    priority_type: Any = None
