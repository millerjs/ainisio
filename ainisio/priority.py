from .base import IssueShower


class IssuePriorityUpdater(IssueShower):
    "Update jira issue status"

    def get_parser(self, prog_name):
        priorities = [r.name for r in self.app.client.priorities()]
        parser = super(IssuePriorityUpdater, self).get_parser(prog_name)
        parser.add_argument('-p', '--priority', choices=priorities)
        return parser

    def update_issue_priority(self, issue, parsed_args):
        priority = parsed_args.priority
        self.query_continue(
            'Update priority on issue {} ["{} ..."] to {}?'.format(
                issue.key, issue.fields.summary[:32], priority))

        issue.update(priority={'name': priority})
        print("updating issue priority to {}".format(priority))

    def take_action(self, parsed_args):
        issue = self.fetch_issue(parsed_args)
        self.update_issue_priority(issue, parsed_args)
        issue = self.fetch_issue(parsed_args)
        return self.parse_issue(issue, parsed_args)
