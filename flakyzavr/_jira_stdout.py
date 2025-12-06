from collections import namedtuple
from json import JSONDecodeError as jsonJSONDecodeError
from typing import Any

from jira import JIRA
from jira import Issue
from jira import JIRAError
from requests import JSONDecodeError as requestsJSONDecodeError
from rtry import retry

MockIssue = namedtuple('MockIssue', ['key'])


class JiraAuthorizationError(BaseException):
    ...


class JiraUnavailable:
    ...


class LazyJiraTrier:
    def __init__(self, server, basic_auth, dry_run=False) -> None:
        self._server = server
        self._basic_auth = basic_auth
        self._jira = None
        self._dry_run = dry_run

    def connect(self) -> JIRA | JiraUnavailable:
        if not self._jira:
            try:
                self._jira = JIRA(self._server, basic_auth=self._basic_auth)
            except JIRAError as e:
                if e.status_code == 403:
                    raise JiraAuthorizationError from None
                self._jira = None
                return JiraUnavailable()
            except jsonJSONDecodeError:
                self._jira = None
                return JiraUnavailable()
            except requestsJSONDecodeError:
                self._jira = None
                return JiraUnavailable()

        return self._jira

    def search_issues(self, jql_str: str) -> list[Issue] | JiraUnavailable:
        if self._dry_run:
            print(f'Query: {jql_str}')
        res = retry(delay=1, attempts=3, until=lambda x: isinstance(x, JiraUnavailable), logger=print)(self.connect)()
        if isinstance(res, JiraUnavailable):
            return res

        try:
            return retry(
                delay=1,
                attempts=3,
                swallow=(JIRAError, jsonJSONDecodeError, requestsJSONDecodeError)
            )(self._jira.search_issues)(jql_str=jql_str)
        except JIRAError:
            return JiraUnavailable()
        except jsonJSONDecodeError:
            return JiraUnavailable()
        except requestsJSONDecodeError:
            return JiraUnavailable()

    def add_comment(self, issue: Issue, comment: str) -> None | JiraUnavailable:
        res = retry(delay=1, attempts=3, until=lambda x: isinstance(x, JiraUnavailable), logger=print)(self.connect)()
        if isinstance(res, JiraUnavailable):
            return res

        if self._dry_run:
            print(f'Comment to create: {comment} in {issue.key}')
            return None

        try:
            self._jira.add_comment(issue, comment)
        except JIRAError:
            return JiraUnavailable()
        except jsonJSONDecodeError:
            return JiraUnavailable()
        except requestsJSONDecodeError:
            return JiraUnavailable()

    def create_issue(self, fields: dict[str, Any]) -> Issue | MockIssue | JiraUnavailable:
        res = retry(delay=1, attempts=3, until=lambda x: isinstance(x, JiraUnavailable), logger=print)(self.connect)()
        if isinstance(res, JiraUnavailable):
            return res

        if self._dry_run:
            print(f'Issue to create: {fields}')
            return MockIssue(key='EXISTING_MOCKED_ISSUE')

        try:
            issue = self._jira.create_issue(fields=fields)
        except JIRAError:
            return JiraUnavailable()
        except jsonJSONDecodeError:
            return JiraUnavailable()
        except requestsJSONDecodeError:
            return JiraUnavailable()
        return issue

    def create_issue_link(self, inwardIssue: str, outwardIssue: str) -> None | JiraUnavailable:
        res = retry(delay=1, attempts=3, until=lambda x: isinstance(x, JiraUnavailable), logger=print)(self.connect)()
        if isinstance(res, JiraUnavailable):
            return res

        if self._dry_run:
            print(f'Link {inwardIssue} with {outwardIssue}')
            return None

        try:
            self._jira.create_issue_link(
                type='is linked with',
                inwardIssue=inwardIssue,
                outwardIssue=outwardIssue
            )
        except JIRAError:
            return JiraUnavailable()
        except jsonJSONDecodeError:
            return JiraUnavailable()
        except requestsJSONDecodeError:
            return JiraUnavailable()
