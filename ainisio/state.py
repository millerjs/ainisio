from .base import IssueLister


class IssueCheckout(IssueLister):
    "checkout a jira issue"

    def get_parser(self, prog_name):
        parser = super(IssueLister, self).get_parser(prog_name)
        parser.add_argument('key',  nargs='?', default=self.app.current_issue)
        return parser

    def take_action(self, parsed_args):
        issue = self.fetch_issue(parsed_args)
        self.app.current_issue = issue.key
        self.app.log.info("Current issue is {}".format(self.app.current_issue))
        return self.generate_table([issue], parsed_args)
