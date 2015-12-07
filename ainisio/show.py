from cliff.command import Command
import json

from .base import IssueHandler


class IssueShowerRaw(IssueHandler, Command):
    "show jira raw json"

    def take_action(self, parsed_args):
        issue = self.fetch_issue(parsed_args)
        print json.dumps(issue.raw, indent=2)


class ShowSprints(Command):
    "show jira raw"

    def take_action(self, parsed_args, board='24'):
        sprints = self.app.client.sprints(board)
        sprints = [s for s in sprints if s.state.lower() == 'open']
        print sprints
