import logging
from jira import JIRAError

from .base import IssueLister


class IssueSearch(IssueLister):
    "search jira issues"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(IssueSearch, self).get_parser(prog_name)
        parser.add_argument('query', nargs='*')
        parser.add_argument('-l', '--limit', action='store', type=int, default=32)
        parser.add_argument('-p', '--project', action='store')
        parser.add_argument('-au', '--any-user', action='store_true')
        parser.add_argument('-ao', '--any-order', action='store_true')
        parser.add_argument('-as', '--any-status', action='store_true')
        parser.add_argument('-asp', '--any-sprint', action='store_true')
        parser.add_argument('-dp', '--default-project', action='store_true')
        return parser

    def construct_query(self, parsed_args):
        query = []
        project = parsed_args.project or self.app.project

        # Opt in
        if parsed_args.default_project:
            query += ['project={}'.format(project)]

        # Opt out
        if not parsed_args.any_user:
            query += ['assignee=currentUser()']
        if not parsed_args.any_status:
            query += ['status in (Open, "In Progress")']
        if not parsed_args.any_sprint:
            query += ['sprint in openSprints()']
        return query

    def construct_query_string(self, parsed_args):
        # Parse args
        query = self.construct_query(parsed_args)
        if parsed_args.query:
            query += [' '.join(parsed_args.query)]
        query_string = ' and '.join(query)

        # Ordering
        if not parsed_args.any_order:
            query_string += ' order by priority, created desc'

        self.log.info("query string: '{}'".format(query_string))
        return query_string

    def query(self, query_string):
        try:
            fields = 'parent,priority,summary,comment,status,assignee'
            return self.app.client.search_issues(query_string, fields=fields)
        except JIRAError as e:
            raise RuntimeError(e.text)

    def take_action(self, parsed_args):
        # Search for issues
        query_string = self.construct_query_string(parsed_args)
        issues = self.query(query_string)
        self.app.log.info("Found {} issues".format(len(issues)))

        # Truncate list
        if parsed_args.limit:
            self.app.log.info("Showing {}/{} issues".format(
                min(parsed_args.limit, len(issues)), len(issues)))
            issues = issues[:parsed_args.limit]

        return self.generate_table(issues, parsed_args)


class IssueSearchRecent(IssueSearch):
    "search jira for recent issues"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(IssueSearchRecent, self).get_parser(prog_name)
        parser.add_argument('-d', '--duration', action='store')
        return parser

    def construct_query(self, parsed_args):
        parent = super(IssueSearchRecent, self)
        query = parent.construct_query(parsed_args)
        duration = parsed_args.duration or '8h'
        query += ['updated >= "-{}"'.format(duration)]
        return query
