# vedro-jira-failed-reporter

Make report to jira when scenario fails


## Install & setup

Add config
```
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

            jira_search_statuses: list[str] = ['Взят в бэклог', 'Open', 'Reopened', 'In Progress']
            report_project_name: str = 'Chat'
            job_path = 'https://gitlab.com/chat-space/chat/-/jobs/{job_id}'
            job_id: str = '_job_id_'

            dry_run: bool = False

            exceptions: list[str] = []
```
