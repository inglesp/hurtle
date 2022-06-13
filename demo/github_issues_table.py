import os
from datetime import datetime

from github import Github
from github.GithubException import UnknownObjectException


class GitHubIssuesTable:
    schema = ["number", "title", "state", "created_at", "updated_at"]

    def __init__(self, organisation, repo):
        client = Github(os.environ["GITHUB_TOKEN"])
        self.repo = client.get_repo(f"{organisation}/{repo}")

    def select(self, state=None, updated_at__ge=None):
        kwargs = {}
        if state is None:
            kwargs["state"] = "all"
        else:
            kwargs["state"] = state

        if updated_at__ge is not None:
            kwargs["since"] = datetime.fromisoformat(updated_at__ge)

        for issue in self.repo.get_issues(**kwargs):
            yield as_database_row(issue)

    def select_one_by_number(self, number):
        try:
            issue = self.repo.get_issue(number)
            yield as_database_row(issue)
        except UnknownObjectException:
            pass


def as_database_row(issue):
    return [
        issue.number,
        issue.title,
        issue.state,
        str(issue.created_at),
        str(issue.updated_at),
    ]
