from setuptools import setup, find_packages

setup(
    name='ainisio',
    version='0.0.1',
    packages=find_packages(),
    install_requires=[
        'jira==1.0.3',
        'cliff',
        'termcolor',
    ],
    entry_points={
        'console_scripts': [
            'ainisio = ainisio.main:main',
            'jira = ainisio.main:main',
        ],
        'ainisio.cmds': [
            # ======== Search ========
            'recent = ainisio.search:IssueSearchRecent',
            'list = ainisio.search:IssueSearch',
            'ls = ainisio.search:IssueSearch',
            # ======== Show details ========
            'cat = ainisio.base:IssueShower',
            'show = ainisio.base:IssueShower',
            'raw = ainisio.show:IssueShowerRaw',
            # ======== State ========
            'checkout = ainisio.state:IssueCheckout',
            'co = ainisio.state:IssueCheckout',
            'wo = ainisio.state:IssueCheckout',
            # ======== Comments ========
            'comment = ainisio.comments:IssueCommenter',
            'conversation = ainisio.comments:IssueShowerComment',
            'con = ainisio.comments:IssueShowerComment',
            # ======== Status ========
            'close = ainisio.status:IssueCloser',
            'start = ainisio.status:IssueStarter',
            'open = ainisio.status:IssueOpener',
            'status = ainisio.status:IssueArbitraryStatusUpdater',
            # ======== Create ========
            'task = ainisio.create:IssueNewTask',
            'subtask = ainisio.create:IssueNewSubtask',
            'chore = ainisio.create:IssueNewChore',
            'bug = ainisio.create:IssueNewBug',
            # ======== Sprints ========
            'sprint = ainisio.create:IssueAddToSprint',
            # ======== Priority ========
            'priority = ainisio.priority:IssuePriorityUpdater',
        ],
    },
)
