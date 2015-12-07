from cliff.lister import Lister
from cliff.show import ShowOne
from collections import OrderedDict
from jira import JIRAError
from subprocess import call
from termcolor import colored
import logging
import os
import sys
import tempfile
import textwrap


class EmptyEditorError(RuntimeError):
    pass


class CanceledByUserError(RuntimeError):
    pass


class AinisioBase(object):
    log = logging.getLogger(__name__)

    symbols = {
        'me': u"\u2615",
        'open': colored(u"\u25cb", 'red'),
        'closed': colored(u"\u2713", 'green', attrs=['bold']),
        'in_progress': u"\u25b6",
        'current_issue': u"\u2605",
        'current_parent': u"\u2937",
        'priority_0': u"\u27f0",
        'priority_1': colored(u"\u2191", 'red'),
        'priority_2': colored(u"\u2191", 'green'),
        'priority_3': ".",
        'priority_4': " ",
    }

    def get_symbol(self, key):
        symbols = self.app.config('symbols', {})
        return symbols.get(key, self.symbols.get(key, '?'))

    def read_from_editor(self, initial_message="", prefix='', non_empty=True):
        EDITOR = os.environ.get('EDITOR', 'nano')
        with tempfile.NamedTemporaryFile(prefix=prefix, suffix=".tmp") as tmp:
            tmp.write(initial_message)
            tmp.flush()
            cmd = EDITOR.split(' ') + [tmp.name]
            self.log.info(cmd)
            call(cmd)
            tmp.seek(0)
            text = tmp.read()
            if text == initial_message:
                text = ''
            if non_empty and not text:
                raise EmptyEditorError(
                    'Abort due to empty or defuault editor message')
            return text

    def wrap_lines(self, text, width=80):
        return textwrap.fill(text, width=width, subsequent_indent='    ')

    def query_yes_no(self, question, default="yes"):
        """Ask a yes/no question via raw_input() and return their answer.

        "question" is a string that is presented to the user.
        "default" is the presumed answer if the user just hits <Enter>.
            It must be "yes" (the default), "no" or None (meaning
            an answer is required of the user).

        The "answer" return value is True for "yes" or False for "no".
        """
        valid = {"yes": True, "y": True, "ye": True,
                 "no": False, "n": False}
        if default is None:
            prompt = " [y/n] "
        elif default == "yes":
            prompt = " [Y/n] "
        elif default == "no":
            prompt = " [y/N] "
        else:
            raise ValueError("invalid default answer: '%s'" % default)

        while True:
            sys.stdout.write(question + prompt)
            choice = raw_input().lower()
            if default is not None and choice == '':
                return valid[default]
            elif choice in valid:
                return valid[choice]
            else:
                sys.stdout.write(
                    "Please respond with 'yes' or 'no' (or 'y' or 'n').\n")

    def query_continue(self, text, _raise=True):
        cont = self.query_yes_no(text)
        if not cont and _raise:
            raise CanceledByUserError('Canceled by user')
        else:
            return cont

    def sprint_by_name(self, client, name, board='24'):
        return [s for s in client.sprints(board) if s.name == name]

    def add_to_sprint(self, issue, sprint):
        assert sprint, 'No sprint or JIRA_SPRINT in env'
        sprint = self.sprint_by_name(self.app.client, sprint)[0]
        self.app.client.add_issues_to_sprint(sprint.id, [issue.id])


class IssueHandler(AinisioBase):
    log = logging.getLogger(__name__)

    def get_status(self, issue):
        name = issue.fields.status.name
        return {
            'Open': self.get_symbol('open'),
            'Closed': self.get_symbol('closed'),
            'Resolved': self.get_symbol('closed'),
            'In Progress': self.get_symbol('in_progress'),
        }.get(name, name[:4]) if name else ''

    def get_assignee(self, issue):
        assignee = issue.fields.assignee
        if not assignee:
            return ''
        elif assignee.name == self.app.user:
            return self.get_symbol('me')
        else:
            names = assignee.displayName.lower().split()
            return ''.join((a[:1] for a in names))

    def get_priority(self, issue):
        if not issue.fields.priority:
            return ''
        priority = issue.fields.priority.id
        priority = min(max(int(priority), 0), 5)
        return self.get_symbol('priority_{}'.format(priority))

    def get_field(self, field, issue):
        is_current_issue = issue.key == self.app.current_issue
        parent = getattr(issue.fields, 'parent', '')

        if field == 'assignee':
            return self.get_assignee(issue)
        if field == 'is_current_issue':
            if is_current_issue:
                return self.get_symbol('current_issue')
            if parent and parent.key == self.app.current_issue:
                return self.get_symbol('current_parent')
            return ''
        elif field == 'parent':
            return parent
        elif field == 'status':
            return self.get_status(issue)
        elif field == 'ncomments':
            count = len(issue.fields.comment.comments)
            return count if count else ''
        elif field == 'priority':
            return self.get_priority(issue)
        elif field in ['creator', 'author', 'reporter']:
            person = getattr(issue.fields, field, '')
            return person.displayName if person else ''
        elif field == 'key':
            return colored(issue.key, 'blue', attrs=['bold'])
        elif field in 'summary':
            summary = self.wrap_lines(issue.fields.summary)
            if is_current_issue:
                return colored(summary, 'green', attrs=['bold'])
            else:
                return colored(summary, 'grey', attrs=['bold'])
        else:
            return self.wrap_lines(str(getattr(issue.fields, field, '')))

    def get_issue_fields(self, fields, issue, app=None):
        vals = []
        for field in fields:
            try:
                vals += [self.get_field(field, issue)]
            except Exception as e:
                vals += ['']
                print("Error adding field '{}': {}".format(field, e))
        return vals

    def fetch_issue(self, parsed_args):
        if not parsed_args.key:
            raise RuntimeError("No key or current_issue")
        try:
            key = parsed_args.key.split('-')
            project = self.app.project if len(key) < 2 else key[0]
            key = '{}-{}'.format(project, key[-1])
            self.log.info('Getting issue {}'.format(key))
            return self.app.client.issue(key)
        except JIRAError as e:
            raise RuntimeError(e.text)


class IssueLister(IssueHandler, Lister):
    "show jira issues"

    fields = OrderedDict()
    fields['*'] = 'is_current_issue'
    fields['Key'] = 'key'
    fields['Pa'] = 'parent'
    fields['P'] = 'priority'
    fields['S'] = 'status'
    fields['C'] = 'ncomments'
    fields['To'] = 'assignee'
    fields['Summary'] = 'summary'

    def generate_table(self, issues, parsed_args):
        return (self.fields.keys(), (
            self.get_issue_fields(self.fields.values(), i, self.app)
            for i in issues
        ))


class IssueShower(IssueHandler, ShowOne):
    "show details of a jira issue"

    fields = OrderedDict()
    fields['key'] = 'key'
    fields['summary'] = 'summary'
    fields['status'] = 'status'
    fields['ncomments'] = 'ncomments'
    fields['assignee'] = 'assignee'
    fields['priority'] = 'priority'
    fields['parent'] = 'parent'
    fields['reporter'] = 'reporter'
    fields['creator'] = 'creator'
    fields['labels'] = 'labels'
    fields['created'] = 'created'
    fields['updated'] = 'updated'
    fields['description'] = 'description'

    def get_parser(self, prog_name):
        parser = super(IssueShower, self).get_parser(prog_name)
        parser.add_argument('key',  nargs='?', default=self.app.current_issue)
        return parser

    def parse_issue(self, issue, parsed_args):
        vals = self.get_issue_fields(self.fields.values(), issue, self.app)
        return self.fields.keys(), vals

    def take_action(self, parsed_args):
        issue = self.fetch_issue(parsed_args)
        return self.parse_issue(issue, parsed_args)
