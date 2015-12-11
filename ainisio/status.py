from .base import IssueShower


class IssueStatusUpdater(IssueShower):
    "Update jira issue status"

    to_state = None

    def get_parser(self, prog_name):
        resolutions = [r.name for r in self.app.client.resolutions()]
        parser = super(IssueStatusUpdater, self).get_parser(prog_name)
        parser.add_argument('-r', '--resolution', choices=resolutions)
        return parser

    def update_issue_status(self, issue, to_state, parsed_args):
        self.query_continue(
            'Update status on issue {} ["{} ..."] to {}?'.format(
                issue.key, issue.fields.summary[:32], to_state))
        transitions = [
            t['id'] for t in self.app.client.transitions(issue)
            if t['to']['name'] == to_state
        ]
        assert transitions, 'Transition to {} not found'.format(to_state)
        assert len(transitions) < 2,\
            'More than one transition to {} not found'.format(to_state)

        fields = {}
        if parsed_args.resolution:
            fields['resolution'] = {'name': parsed_args.resolution}
        self.app.client.transition_issue(issue, transitions[0])
        print("updating issue status to {}".format(to_state))

    def take_action(self, parsed_args):
        issue = self.fetch_issue(parsed_args)
        self.update_issue_status(issue, self.to_state, parsed_args)
        issue = self.fetch_issue(parsed_args)
        return self.parse_issue(issue, parsed_args)


class IssueCloser(IssueStatusUpdater):
    to_state = 'Resolved'


class IssueStarter(IssueStatusUpdater):
    to_state = 'In Progress'


class IssueOpener(IssueStatusUpdater):
    to_state = 'Open'


class IssueArbitraryStatusUpdater(IssueStatusUpdater):
    "Update jira issue status"

    to_state = None

    def get_parser(self, prog_name):
        statuses = [s.name for s in self.app.client.statuses()]
        parser = super(IssueArbitraryStatusUpdater, self).get_parser(prog_name)
        parser.add_argument('-s', '--to-state', choices=statuses)
        return parser

    def update_issue_status(self, issue, _, parsed_args):
        super(IssueArbitraryStatusUpdater, self).update_issue_status(
            issue, parsed_args.to_state, parsed_args)
