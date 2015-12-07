import logging
import sys
import os
from jira import JIRA
import yaml
import getpass

from cliff.app import App
from cliff.commandmanager import CommandManager

PASS_PROMPT = "[JIRA_PASS unspecified] pass: "


class JiraApp(App):

    log = logging.getLogger(__name__)
    var_names = {
        'host': 'JIRA_HOST',
        'user': 'JIRA_USER',
        'project': 'JIRA_PROJECT',
    }

    def __init__(self):
        super(JiraApp, self).__init__(
            description='Jira cli app',
            version='0.1',
            command_manager=CommandManager('ainisio.cmds'),
        )
        self.config_path = os.environ.get(
            'AINISIO_CONFIG',
            os.path.expanduser('~/.ainisio.config')
        )
        self.host, self.user, self.project = None, None, None
        self.current_issue = None
        self._config = {}
        if os.path.isfile(self.config_path):
            with open(self.config_path, 'r') as f:
                self._config.update(yaml.load(f.read()))
        self.log.info(self._config)
        self.users = set()

    def config(self, key, default=None):
        return os.environ.get(key) or self._config.get(key) or default

    def initialize_app(self, argv):
        for name, var in self.var_names.iteritems():
            setattr(self, name, self.config(var))
            assert getattr(self, name, self.config(var)),\
                'Please specify {} in env vars or config'.format(var)

        password = self.config('JIRA_PASS') or getpass.getpass(PASS_PROMPT)
        self.client = JIRA(self.host, basic_auth=(self.user, password))


def main(argv=sys.argv[1:]):
    myapp = JiraApp()
    return myapp.run(argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
