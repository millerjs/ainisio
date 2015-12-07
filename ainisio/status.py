from .base import IssueShower


class IssueStatusUpdater(IssueShower):
    "Update jira issue status"

    to_state = None

    def get_parser(self, prog_name):
        parser = super(IssueStatusUpdater, self).get_parser(prog_name)
        return parser

    def update_issue_status(self, issue, parsed_args):
        self.query_continue(
            'Update status on issue {} ["{} ..."] to {}?'.format(
                issue.key, issue.fields.summary[:32], self.to_state))
        transitions = [
            t['id'] for t in self.app.client.transitions(issue)
            if t['to']['name'] == self.to_state
        ]
        assert transitions, 'Transition to {} not found'.format(self.to_state)
        self.app.client.transition_issue(issue, transitions[0])
        print("updating issue status to {}".format(self.to_state))

    def take_action(self, parsed_args):
        issue = self.fetch_issue(parsed_args)
        self.update_issue_status(issue, parsed_args)
        issue = self.fetch_issue(parsed_args)
        return self.parse_issue(issue, parsed_args)


class IssueCloser(IssueStatusUpdater):
    to_state = 'Resolved'


class IssueStarter(IssueStatusUpdater):
    to_state = 'In Progress'


class IssueOpener(IssueStatusUpdater):
    to_state = 'Open'
