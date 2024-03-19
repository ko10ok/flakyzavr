from collections import namedtuple
from json import JSONDecodeError as jsonJSONDecodeError
from typing import Any

from jira import JIRA
from jira import Issue
from jira import JIRAError
from requests import JSONDecodeError as requestsJSONDecodeError
from rtry import retry

MockIssue = namedtuple('MockIssue', ['key'])


class StdoutJira:
    def search_issues(self, prompt: str) -> list[MockIssue]:
        print(f'Searching: {prompt}')
        return []
        return [MockIssue(key='EXISTING_MOCKED_ISSUE')]

    def add_comment(self, issue: Issue, comment: str) -> None:
        print('add_comment: ', Issue, comment)

    def create_issue(self, fields: dict[str, Any]) -> MockIssue:
        print('create_issue:\n')
        print(fields['project'])
        print(fields['summary'])
        print(fields['description'])
        return MockIssue(key='NEW_MOCKED_ISSUE')


class JiraAuthorizationError(BaseException):
    ...


class JiraUnavailable:
    ...


class LazyJiraTrier:
    def __init__(self, server, basic_auth) -> None:
        self._server = server
        self._basic_auth = basic_auth
        self._jira = None

    # @retry(delay=1, attempts=3, swallow=JIRAError)
    def connect(self) -> JIRA | JiraUnavailable:
        if not self._jira:
            try:
                self._jira = JIRA(self._server, basic_auth=self._basic_auth)
            except JIRAError as e:
                if e.status_code == 403:
                    raise JiraAuthorizationError from None
                self._jira = None
                return JiraUnavailable()
            except jsonJSONDecodeError as e:
                self._jira = None
                return JiraUnavailable()
            except requestsJSONDecodeError as e:
                self._jira = None
                return JiraUnavailable()

        return self._jira

    # @retry(delay=1, attempts=3, swallow=JIRAError)
    def search_issues(self, jql_str: str) -> list[Issue] | JiraUnavailable:
        res = retry(delay=1, attempts=3, until=lambda x: isinstance(x, JiraUnavailable), logger=print)(self.connect)()
        if isinstance(res, JiraUnavailable):
            return res

        try:
            return retry(
                delay=1,
                attempts=3,
                swallow=(JIRAError, jsonJSONDecodeError, requestsJSONDecodeError)
            )(self._jira.search_issues)(jql_str=jql_str)
        except JIRAError as e:
            return JiraUnavailable()
        except jsonJSONDecodeError as e:
            return JiraUnavailable()
        except requestsJSONDecodeError as e:
            return JiraUnavailable()

    def add_comment(self, issue: Issue, comment: str) -> None | JiraUnavailable:
        res = retry(delay=1, attempts=3, until=lambda x: isinstance(x, JiraUnavailable), logger=print)(self.connect)()
        if isinstance(res, JiraUnavailable):
            return res
        try:
            self._jira.add_comment(issue, comment)
        except JIRAError as e:
            return JiraUnavailable()
        except jsonJSONDecodeError as e:
            return JiraUnavailable()
        except requestsJSONDecodeError as e:
            return JiraUnavailable()
        return

    def create_issue(self, fields: dict[str, Any]) -> Issue | JiraUnavailable:
        res = retry(delay=1, attempts=3, until=lambda x: isinstance(x, JiraUnavailable), logger=print)(self.connect)()
        if isinstance(res, JiraUnavailable):
            return res
        try:
            issue = self._jira.create_issue(fields=fields)
        except JIRAError as e:
            return JiraUnavailable()
        except jsonJSONDecodeError as e:
            return JiraUnavailable()
        except requestsJSONDecodeError as e:
            return JiraUnavailable()
        return issue
