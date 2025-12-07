from typing import Dict

import jj
from jj.http import GET
from jj.http import POST
from jj.mock import Mocked
from jj.mock import mocked


def mocked_jira_server_info() -> Mocked:
    endpoint = '/rest/api/2/serverInfo'
    jira_status = 200
    jira_response = {
        'versionNumbers': [8, 13, 0],
    }
    return mocked(
        matcher=jj.match(GET, endpoint),
        response=jj.Response(status=jira_status, json=jira_response),
    )

def mocked_jira_fields() -> Mocked:
    endpoint = '/rest/api/2/field'
    jira_status = 200
    jira_response = {
        'fields': [],
    }
    return mocked(
        matcher=jj.match(GET, endpoint),
        response=jj.Response(status=jira_status, json=jira_response),
    )

def mocked_jira_search(jira_status: int = 200, jira_response: Dict = None) -> Mocked:
    endpoint = f'/rest/api/2/search'

    if jira_response is None:
        jira_response = {
            'issues': [],
            'total': 0,
        }

    return mocked(
        matcher=jj.match(GET, endpoint),
        response=jj.Response(status=jira_status, json=jira_response),
    )

def mocked_jira_create(key: str) -> Mocked:
    endpoint = f'/rest/api/2/issue'
    jira_status = 201
    jira_response = {
        'key': key,
    }
    return mocked(
        matcher=jj.match(POST, endpoint),
        response=jj.Response(status=jira_status, json=jira_response),
    )

def mocked_jira_get_issue(key: str) -> Mocked:
    endpoint = f'/rest/api/2/issue/{key}'
    jira_status = 200
    jira_response = {
        'key': key,
    }
    return mocked(
        matcher=jj.match(GET, endpoint),
        response=jj.Response(status=jira_status, json=jira_response),
    )
