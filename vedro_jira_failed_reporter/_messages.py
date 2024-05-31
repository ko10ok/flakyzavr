from typing import NamedTuple


class ReportingLangSet(NamedTuple):
    FILTERED_OUT_BY_EXCEPTION_REGEXP: str
    SKIP_CREATING_ISSUE_DUE_TO_JIRA_SEARCH_UNAVAILABILITY: str
    SKIP_CREATING_ISSUE_DUE_TO_JIRA_CREATE_UNAVAILABILITY: str
    SKIP_CREATING_COMMENT_IN_EXISTING_ISSUE_DUE_TO_JIRA_UNAVAILABILITY: str
    ISSUE_ALREADY_EXISTS: str
    ISSUE_CREATED: str
    RELATED_ISSUES_FOUND: str
    NEW_ISSUE_SUMMARY: str
    NEW_ISSUE_TEXT: str
    NEW_COMMENT_TEXT: str


RU_REPORTING_LANG = ReportingLangSet(
    FILTERED_OUT_BY_EXCEPTION_REGEXP='Флаки тикета не будет создно. Падение отфильтровано по списку исключений.',
    SKIP_CREATING_ISSUE_DUE_TO_JIRA_SEARCH_UNAVAILABILITY=(
        '{jira_server} не был доступен во время поиска тикетов. '
        'Пропускаем создание тикета для текущего теста'
    ),
    SKIP_CREATING_ISSUE_DUE_TO_JIRA_CREATE_UNAVAILABILITY=(
        '{jira_server} не был доступен во время создания тикета. '
        'Пропускаем создание тикета для текущего теста'
    ),
    SKIP_CREATING_COMMENT_IN_EXISTING_ISSUE_DUE_TO_JIRA_UNAVAILABILITY=(
        '{jira_server} не был доступен во время добавления комментария о флакующем тесте. '
        'Пропускаем создание коментария для текущего теста'
    ),
    ISSUE_ALREADY_EXISTS='Флаки тикет уже есть {jira_server}/browse/{issue_key}',
    ISSUE_CREATED='Заведен новый флаки тикет {jira_server}/browse/{issue_key}',
    RELATED_ISSUES_FOUND='Есть связанные c этим файлом тикеты: {issues}',
    NEW_ISSUE_SUMMARY='[{project_name}] Флаки тест {test_name} ({priority})',
    NEW_ISSUE_TEXT=(
        'h2. {{color:#172b4d}}Контекст{{color}}\n'
        'Флаки тест \n'
        '{test_file}\n'
        '{{code:python}}\n'
        '{test_name}\n'
        '{{code}}\n'
        'Приоритет теста - {priority}\n'
        '{{code:python}}\n'
        '{traceback}\n'
        '--------------------------------------------------------------------------------\n'
        '{error}\n'
        '{{code}}\n'
        '{job_link}\n'
        'h2. {{color:#172b4d}}Что нужно сделать{{color}}\n'
        '{{task}}Заскипать vedro-flaky-steps плагином место падения{{task}}\n'
        '{{task}}Разобраться в причине падения и починить тест по необходимости{{task}}'
    ),
    NEW_COMMENT_TEXT=(
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
)

EN_REPORTING_LANG = ReportingLangSet(
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
