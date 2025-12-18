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
            jira_user: str = 'username'
            jira_password: str = 'userpassword'
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

        self.helper_path = 'helper/helper_file.py'
        self.inner_traced_file = mocked_traced_file(
            filename=self.tests_dir / self.helper_path,
            file_content='\n'.join([
                f'inner_file_line {line_no}' for line_no in range(1, 20)
            ]),
            line_start=2,
            line_target=6,
        )
        self.scenario_traced_file = mocked_traced_file(
            filename=self.tests_dir / self.scenario_project_filename,
            file_content='\n'.join([
                f'scenario_file_line {line_no}' for line_no in range(1, 20)
            ]),
            line_start=10,
            line_target=13,
            next_traceback=self.inner_traced_file
        )
        self.context_path = 'contexts/helper_file.py'
        self.outer_traced_file = mocked_traced_file(
            filename=self.tests_dir / self.context_path,
            file_content='\n'.join([
                f'outer_file_line {line_no}' for line_no in range(1, 20)
            ]),
            line_start=15,
            line_target=18,
            next_traceback=self.scenario_traced_file
        )
        self.failed_scenario = mocked_failed_scenario_result(
            scenario_name=self.scenario_name,
            scenario_project_filename=self.scenario_project_filename,
            traced_file=self.outer_traced_file,
            tests_dir=self.tests_dir,
        )

    async def given_failed_scenario_event(self):
        self.event = ScenarioFailedEvent(scenario_result=self.failed_scenario.scenario_result)

    async def when_vedro_fires_plugin_handler(self):
        with (
            temp_file(self.inner_traced_file.filename, self.inner_traced_file.file_content),
            temp_file(self.scenario_traced_file.filename, self.scenario_traced_file.file_content),
            temp_file(self.outer_traced_file.filename, self.outer_traced_file.file_content),
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

        self.expected_auth_token = base64.b64encode(
            self.plugin_config.jira_user.encode() + b':' + self.plugin_config.jira_password.encode()).decode()

        self.expected_summary = (f'[{self.plugin_config.report_project_name}] Флаки тест {self.scenario_name} ('
                                 f'{IssuePriority.NOT_SET_PRIORITY})')

        self.expected_summary = issue_summary(
            test_name=self.scenario_name,
            project_name=self.plugin_config.report_project_name,
            priority=IssuePriority.NOT_SET_PRIORITY,
        )

        self.expected_labels = self.jira_labels + [self.jira_flaky_label]

        self.expected_traceback = '\n'.join([
            f'# {self.outer_traced_file.filename}:',
            f'>  {self.outer_traced_file.line_target}|outer_file_line {self.outer_traced_file.line_target}',
            '',
            f'# {self.scenario_traced_file.filename}:',
            '    9|scenario_file_line 9',   # -1 before
            '   10|scenario_file_line 10',  # self.scenario_traced_file.line_start
            '   11|scenario_file_line 11',
            '   12|scenario_file_line 12',
            '>  13|scenario_file_line 13',  # self.scenario_traced_file.line_target
            '   14|scenario_file_line 14',  # + 3 after
            '   15|scenario_file_line 15',
            '   16|scenario_file_line 16',
            '',
            f'# {self.inner_traced_file.filename}:',
            f'>   {self.inner_traced_file.line_target}|inner_file_line {self.inner_traced_file.line_target}',
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

        assert self.create_history == HistorySchema.len(1)
        assert self.create_history[0]['request'].body['fields']['description'].split('\n') == self.expected_description.split('\n')
