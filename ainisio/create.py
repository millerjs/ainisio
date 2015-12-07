import yaml


from .base import IssueShower
from .sprints import IssueAddToSprint


class IssueNew(IssueShower):
    "update jira issue status"

    issue_type = None

    def get_parser(self, prog_name):
        parser = super(IssueNew, self).get_parser(prog_name)
        parser.add_argument('-p', '--priority', action='store',
                            default='Major')
        parser.add_argument('--project', action='store',
                            default=self.app.project)
        parser.add_argument('-t', '--time-estimate', type=str, action='store',
                            default='2h')
        parser.add_argument('-a', '--assignee', type=str, action='store',
                            default=self.app.user)
        parser.add_argument('--author', type=str, action='store',
                            default=self.app.user)
        parser.add_argument('-sp', '--sprint', action='store',
                            default=self.app.config('JIRA_SPRINT'))
        return parser

    def create_issue(self, parsed_args, parent=None):

        # Get user input
        summary = self.read_from_editor(
            prefix='summary_')
        description = self.read_from_editor(
            prefix='description_',  non_empty=False)

        # Construct issue
        issue_dict = dict(
            project={'key': parsed_args.project},
            summary=summary,
            description=description,
            issuetype={'name': self.issue_type},
            timetracking={
                "originalEstimate": parsed_args.time_estimate,
                "remainingEstimate": parsed_args.time_estimate,
            },
            assignee={'name': parsed_args.assignee},
            priority={'name': parsed_args.priority},
        )

        if parent:
            issue_dict['parent'] = parent

        # Double check
        print yaml.dump(issue_dict)
        self.query_continue("Create this issue?")

        # Create issue
        issue = self.app.client.create_issue(issue_dict)

        # Add to current sprint?
        sprint_q = "Add to sprint {}?".format(parsed_args.sprint)
        if self.query_continue(sprint_q, _raise=False):
            self.add_to_sprint(issue, parsed_args.sprint)

        return issue

    def take_action(self, parsed_args):
        issue = self.create_issue(parsed_args)
        return self.parse_issue(issue, parsed_args)


class IssueNewSubtask(IssueNew):
    issue_type = 'Sub-task'

    def take_action(self, parsed_args):
        parent = self.fetch_issue(parsed_args)
        issue = self.create_issue(parsed_args, parent={'id': parent.id})
        return self.parse_issue(issue, parsed_args)


class IssueNewTask(IssueNew):
    issue_type = 'Task'


class IssueNewBug(IssueNew):
    issue_type = 'Bug'


class IssueNewChore(IssueNew):
    issue_type = 'Chore'
