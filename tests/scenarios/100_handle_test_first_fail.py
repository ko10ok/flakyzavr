import base64
from pathlib import Path
from time import monotonic_ns

import vedro
from d42 import fake
from flakyzavr import RU_REPORTING_LANG
from flakyzavr import Flakyzavr
from flakyzavr import FlakyzavrPlugin
from jj_d42 import HistorySchema
from vedro.events import ScenarioFailedEvent

from contexts.issue_summary import issue_summary
from contexts.mocks.mocked_failed_scenario_result import mocked_failed_scenario_result
from contexts.mocks.mocked_jira import mocked_jira_create
from contexts.mocks.mocked_jira import mocked_jira_fields
from contexts.mocks.mocked_jira import mocked_jira_get_issue
from contexts.mocks.mocked_jira import mocked_jira_search
from contexts.mocks.mocked_jira import mocked_jira_server_info
from contexts.mocks.mocked_python_traceback import mocked_traced_file
from helpers.temp_file import temp_file
from libs.issue_priority import IssuePriority
from schemas.scenario import ScenarioNameSchema


class Scenario(vedro.Scenario):

    async def given_plugin_initialized(self):
        self.jira_labels = ['new_flaky', 'qa_tech_debt']
        self.jira_flaky_label = 'flaky'

        class _Flakyzavr(Flakyzavr):
            enabled = True

            report_enabled = False  # enable it when flaky run

            jira_server: str = 'http://mock'
            jira_token: str = 'jira_token'
            jira_project: str = 'jira_project'
            jira_components: list[str] = ['world']
            jira_labels: list[str] = ['new_flaky', 'qa_tech_debt']  # extra labels
            jira_flaky_label: str = 'flaky'

            jira_additional_data: dict[str, str] = {}
            jira_issue_type_id: str = '3'
            report_project_name: str = 'SomeAppName'
            job_path = 'gitlab/{job_id}'
            job_id: str = '4'

            dry_run: bool = False

            exceptions: list[str] = [r'.*codec can\'t decode byte.*']

        self.plugin_config = _Flakyzavr
        self.plugin = FlakyzavrPlugin(config=self.plugin_config)

    async def given_failed_scenario(self):
        self.tests_dir = Path('/tmp/tests')

        self.scenario_name = fake(ScenarioNameSchema)
        self.scenario_project_filename = Path(f'scenarios/scenario_{monotonic_ns()}.py')
        self.scenario_path = f'{self.tests_dir}/{self.scenario_project_filename}'

        self.file_content = '\n'.join([
            f'line {line_no}' for line_no in range(1, 20)
        ])

        self.traced_file = mocked_traced_file(
            filename=self.tests_dir / self.scenario_project_filename,
            file_content=self.file_content,
            line_start=2,
            line_target=4,
        )
        self.failed_scenario = mocked_failed_scenario_result(
            scenario_name=self.scenario_name,
            scenario_project_filename=self.scenario_project_filename,
            traced_file=self.traced_file,
            tests_dir=self.tests_dir,
        )

    async def given_failed_scenario_event(self):
        self.event = ScenarioFailedEvent(scenario_result=self.failed_scenario.scenario_result)

    async def when_vedro_fires_plugin_handler(self):
        with (
            temp_file(self.failed_scenario.scenario.path, self.failed_scenario.traced_file.file_content),
            mocked_jira_server_info() as self.jira_server_info_mock,
            mocked_jira_fields() as self.jira_fields_mock,
            mocked_jira_search() as self.jira_search_mock,
            mocked_jira_create(key='WORKSPACE-123') as self.jira_create_mock,
            mocked_jira_get_issue(key='WORKSPACE-123') as self.jira_get_issue_mock,
        ):
            self.plugin.on_scenario_failed(self.event)

    async def then_it_should_call_jira_for_search(self):
        self.search_history = self.jira_search_mock.history

        self.expected_statuses = ','.join([f'"{status}"' for status in self.plugin_config.jira_search_statuses])
        assert self.search_history == HistorySchema % [
            {
                'request': {
                    "method": 'GET',
                    "path": '/rest/api/2/search',
                    "params": {
                        "jql": f'project = {self.plugin_config.jira_project} '
                               f'and description ~ "\\"{self.scenario_project_filename}\\"" '
                               f'and status in ({self.expected_statuses}) '
                               f'and labels = {self.plugin_config.jira_flaky_label} '
                               f'ORDER BY created',
                        'startAt': '0',
                        'validateQuery': 'True',
                        'fields': '*all',
                        'maxResults': '50',
                    },
                },
            }
        ]

    async def then_it_should_call_jira_for_create_new_issue(self):
        self.create_history = self.jira_create_mock.history

        self.expected_summary = issue_summary(
            test_name = self.scenario_name,
            project_name = self.plugin_config.report_project_name,
            priority = IssuePriority.NOT_SET_PRIORITY,
        )

        self.expected_labels = self.jira_labels + [self.jira_flaky_label]

        self.expected_traceback = '\n'.join([
            f'# {self.scenario_path}:',
            '    1|line 1\n'
            '    2|line 2\n'
            '    3|line 3\n'
            '>   4|line 4\n'
            '    5|line 5\n'
            '    6|line 6\n'
            '    7|line 7'
        ])

        self.expected_description = RU_REPORTING_LANG.NEW_ISSUE_TEXT.format(
            test_name=self.scenario_name,
            test_file=self.scenario_project_filename,
            priority=IssuePriority.NOT_SET_PRIORITY,
            traceback=self.expected_traceback,
            error=(
                self.failed_scenario.traced_file.error_type.__name__
                + self.failed_scenario.traced_file.error_description
            ),
            job_link=self.plugin_config.job_path.format(job_id=self.plugin_config.job_id),
        )

        assert self.create_history == HistorySchema % [
            {
                'request': {

                    "method": 'POST',
                    "path": '/rest/api/2/issue',
                    'headers': [
                        ...,
                        ['Authorization', f'Bearer {self.plugin_config.jira_token}'],
                        ...,
                    ],
                    "body": {
                        'fields': {
                            'project': {
                                'key': self.plugin_config.jira_project
                            },
                            'summary': self.expected_summary,
                            'description': self.expected_description,
                            'issuetype': {
                                'id': self.plugin_config.jira_issue_type_id
                            },
                            'components': [
                                {'name': component} for component in self.plugin_config.jira_components
                            ],
                            'labels': self.expected_labels,
                        },
                    },
                },
            }
        ]
