from vedro_jira_failed_reporter.version import get_version

from ._failed_reporter_plugin import FailedJiraReporter
from ._failed_reporter_plugin import FailedJiraReporterPlugin

__version__ = get_version()
__all__ = ("FailedJiraReporter", "FailedJiraReporterPlugin")
