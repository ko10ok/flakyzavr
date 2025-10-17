from dataclasses import dataclass


@dataclass
class BaseReportingPhrases:
    FILTERED_OUT_BY_EXCEPTION_REGEXP: str = 'Флаки тикета не будет создно. Падение отфильтровано по списку исключений.'
    SKIP_CREATING_ISSUE_DUE_TO_JIRA_SEARCH_UNAVAILABILITY: str = (
        '{jira_server} не был доступен во время поиска тикетов. '
        'Пропускаем создание тикета для текущего теста'
    )
    SKIP_CREATING_ISSUE_DUE_TO_JIRA_CREATE_UNAVAILABILITY: str = (
        '{jira_server} не был доступен во время создания тикета. '
        'Пропускаем создание тикета для текущего теста'
    )
    SKIP_CREATING_COMMENT_IN_EXISTING_ISSUE_DUE_TO_JIRA_UNAVAILABILITY: str = (
        '{jira_server} не был доступен во время добавления комментария о флакующем тесте. '
        'Пропускаем создание коментария для текущего теста'
    )
    ISSUE_ALREADY_EXISTS: str = 'Флаки тикет уже есть {jira_server}/browse/{issue_key}'
    ISSUE_CREATED: str = 'Заведен новый флаки тикет {jira_server}/browse/{issue_key}'
    RELATED_ISSUES_FOUND: str = 'Есть связанные c этим файлом тикеты: {issues}'
    NEW_ISSUE_SUMMARY: str = '[{project_name}] Флаки тест {test_name} ({priority})'
    NEW_ISSUE_TEXT: str = (
        'h2. {{color:#172b4d}}Контекст{{color}}\n'
        'Флаки тест \n'
        '{{code:python}}\n'
        '{test_name}\n'
        '{{code}}\n'
        'Путь к файлу: \n'
        '{{code:python}}\n'
        '{test_file}\n'
        '{{code}}\n'
        'Приоритет теста - {priority}\n'
        '{{code:python}}\n'
        '{traceback}\n'
        '--------------------------------------------------------------------------------\n'
        '{error}\n'
        '{{code}}\n'
        '{job_link}\n'
        'h2. {{color:#172b4d}}Что нужно сделать{{color}}\n'
        '{{task}}Указать вес тикета{{task}}\n'
        '{{task}}Проверить приоритет (в тесте и тикете){{task}}\n'
        '{{task}}Проверить, нет ли похожих тикетов/дублей по такой же проблеме{{task}}\n'
        '{{task}}Заскипать vedro-flaky-steps плагином место падения{{task}}\n'
        '{{task}}Разобраться в причине падения и починить тест по необходимости{{task}}'
    )
    NEW_COMMENT_TEXT: str = (
        'Повторный флак\n'
        '{{code:python}}\n'
        '{test_name}\n'
        '{{code}}\n'
        'Приоритет теста - {priority}\n'
        '{job_link}\n'
        '{{code:python}}\n'
        '{traceback}\n'
        '--------------------------------------------------------------------------------\n'
        '{error}\n'
        '{{code}}\n'
    )


RU_REPORTING_LANG = BaseReportingPhrases()

EN_REPORTING_LANG = BaseReportingPhrases(
    FILTERED_OUT_BY_EXCEPTION_REGEXP='Issue for flaky test won\'t be created. Fail reason skipped by exception list.',
    SKIP_CREATING_ISSUE_DUE_TO_JIRA_SEARCH_UNAVAILABILITY=(
        '{jira_server} was unavailable while searching for issues. '
        'Skip creating issue for current test.'
    ),
    SKIP_CREATING_ISSUE_DUE_TO_JIRA_CREATE_UNAVAILABILITY=(
        '{jira_server} was unavailable while creating issue. '
        'Skip creating issue for current test.'
    ),
    SKIP_CREATING_COMMENT_IN_EXISTING_ISSUE_DUE_TO_JIRA_UNAVAILABILITY=(
        '{jira_server} was unavailable while adding new comment for failed test. '
        'Skip adding comment for current test.'
    ),
    ISSUE_ALREADY_EXISTS='Issue for current flaky test already exists: {jira_server}/browse/{issue_key}',
    ISSUE_CREATED='Issue for current flaky test created: {jira_server}/browse/{issue_key}',
    RELATED_ISSUES_FOUND='Found related issues by test file: {issues}',
    NEW_ISSUE_SUMMARY='[{project_name}] Flaky test: {test_name} ({priority})',
    NEW_ISSUE_TEXT=(
        'h2. {{color:#172b4d}}Context{{color}}\n'
        'Flaky test: \n'
        '{{code:python}}\n'
        '{test_name}\n'
        '{{code}}\n'
        'Test priority - {priority}\n'
        '{{code:python}}\n'
        '{traceback}\n'
        '--------------------------------------------------------------------------------\n'
        '{error}\n'
        '{{code}}\n'
        '{job_link}\n'
        'h2. {{color:#172b4d}}Steps to do:{{color}}\n'
        '{{task}}Check for similar/duplicate tickets with the same issue{{task}}\n'
        '{{task}}Skip flaky test in repo{{task}}\n'
        '{{task}}Fix fail cause{{task}}'
    ),
    NEW_COMMENT_TEXT=(
        'Repited test fail\n'
        'Test priority - {priority}\n'
        '{job_link}\n'
        '{{code:python}}\n'
        '{traceback}\n'
        '--------------------------------------------------------------------------------\n'
        '{error}\n'
        '{{code}}\n'
    )
)
