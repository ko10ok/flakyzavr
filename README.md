# flakyzavr

Make report to jira when scenario fails


## Install & setup

Add config
```python
class Config(vedro.Config):

    class Plugins(vedro.Config.Plugins):
    
        class Flakyzavr(flakyzavr.Flakyzavr):
            enabled = True
            report_enabled = True

            jira_server = 'https://jira.com'
            jira_user = '***'
            jira_password = '***'
            jira_project = 'ProjewctName'
            jira_components = ['chat']
            jira_labels: list[str] = ['flaky', 'tech_debt_qa']
            jira_additional_data: dict[str, str] = {
                'customfield_****': 'FieldValue',
            }
            jira_issue_type_id: str = '3'
            jira_search_statuses: list[str] = ['Взят в бэклог', 'Open', 'Reopened', 'In Progress']
            report_project_name: str = 'Chat'
            job_path = 'https://gitlab.com/chat-space/chat/-/jobs/{job_id}'
            job_id: str = '_job_id_'

            dry_run: bool = False

            exceptions: list[str] = []
```

## Customize your report

```python
import flakyzavr
from flakyzavr import BaseReportingPhrases

class Config(vedro.Config):
    class Plugins(vedro.Config.Plugins):
        class Flakyzavr(flakyzavr.Flakyzavr):
            enabled = True
            reporting_phrases =  BaseReportingPhrases(
                NEW_ISSUE_TEXT = 'what a foolish blooper arised:\n'
                    'Test: "{test_name}" failed\n'
                    'File: {test_file}\n'
                    'Blooper: \n{{code:python3}}{traceback}{{code}}\n'
                    'Blooper details: {{code:python3}}{error}{{code}}'
                    'Link: {job_link}'
            )
```
