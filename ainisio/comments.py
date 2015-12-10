from cliff.lister import Lister
from .base import IssueHandler


class IssueShowerComment(IssueHandler, Lister):
    "show jira issue's comments"

    def get_parser(self, prog_name):
        parser = super(IssueShowerComment, self).get_parser(prog_name)
        parser.add_argument('key',  nargs='?', default=self.app.current_issue)
        return parser

    def parse_issue(self, issue, parsed_args):
        comments = issue.fields.comment.comments
        keys = 'ID,Author,Comment'.split(',')
        vals = (
            (c.id, c.author, self.wrap_lines(str(c.body)))
            for c in comments
        )
        self.app.log.info("Found {} comments".format(len(comments)))
        return keys, vals

    def take_action(self, parsed_args):
        issue = self.fetch_issue(parsed_args)
        return self.parse_issue(issue, parsed_args)


class IssueCommenter(IssueShowerComment):
    "Show jira issue"

    def add_comment(self, issue, parsed_args):
        comment = self.read_from_editor(prefix='comment_').strip()
        self.query_continue(
            'Update comment to {}: """\n{}\n"""?'.format(
                issue.key, comment))
        self.app.client.add_comment(issue, comment)
        self.log.info('Adding comment: {}'.format(comment))

    def take_action(self, parsed_args):
        issue = self.fetch_issue(parsed_args)
        self.add_comment(issue, parsed_args)
        issue = self.fetch_issue(parsed_args)
        return self.parse_issue(issue, parsed_args)
