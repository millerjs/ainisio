from .base import IssueShower


class IssueAddToSprint(IssueShower):
    "update jira issue status"

    def get_parser(self, prog_name):
        parser = super(IssueAddToSprint, self).get_parser(prog_name)
        parser.add_argument('-s', '--sprint', action='store',
                            default=self.app.config('JIRA_SPRINT'))
        return parser

    def take_action(self, parsed_args):
        issue = self.fetch_issue(parsed_args)
        if self.query_continue("Add to sprint {}?".format(parsed_args.sprint)):
            self.add_to_sprint(issue, parsed_args.sprint)
        issue = self.fetch_issue(parsed_args)
        return self.parse_issue(issue, parsed_args)
