import time
import datetime

from Commit import Commit
from Repository import Repository

FORMAT = "%Y-%m-%dT%H:%M:%SZ"

INVALID_LABELS = [
    'stat:duplicate',
    'type:support'
]


class Issue:
    def __init__(self, json, repository, index):
        self.json_data = json[index]['node']
        self.repository = repository
        self.commit = None
        self.created_date = time.mktime(datetime.datetime.strptime(self.json_data['createdAt'], FORMAT).timetuple())
        self.closed_date = time.mktime(datetime.datetime.strptime(self.json_data['closedAt'], FORMAT).timetuple())
        self.fix_time = self.closed_date - self.created_date

    def get_linked_commit(self):
        if self.commit is not None:
            return self.commit

        commits = self.json_data['timelineItems']['nodes']

        cs = []
        for commit in commits:
            if len(commit) > 0:
                if 'commit' not in commit:
                    continue
                elif commit['commit'] is None:
                    continue
                cs.append(commit['commit'])
        if len(cs) < 1:
            return None

        cs.sort(key=lambda c: time.mktime(datetime.datetime.strptime(c['committedDate'], FORMAT).timetuple()))
        commit = Commit(self.repository, json=cs[-1])

        if not commit.is_valid():
            return None

        self.commit = commit
        return self.commit

    def get_related_forks(self):
        timelineItems = self.json_data['timelineItems']['nodes']
        forks = []

        for timelineItem in timelineItems:
            if len(timelineItem) > 0:
                if 'commitRepository' not in timelineItem:
                    continue
                elif timelineItem['commitRepository'] is None:
                    continue
                elif timelineItem['commitRepository']['isFork'] is False:
                    continue
                else:
                    name = timelineItem['commitRepository']['name']
                    owner = timelineItem['commitRepository']['owner']
                    forks.append(Repository(name, owner))
        return forks

    def is_valid(self):

        for c in self.json_data['timelineItems']['nodes']:
            if 'commit' in c:
                continue
            elif c['stateReason'] != 'COMPLETED':
                return False

        for label in self.json_data['labels']['nodes']:
            if label['name'] in INVALID_LABELS:
                return False

        return self.get_linked_commit() is not None

    def get_total_cyclomatic_complexity(self):
        return self.commit.get_total_cyclomatic_complexity()
