import time
import datetime

from Commit import Commit
from Fork import Fork

FORMAT = "%Y-%m-%dT%H:%M:%SZ"

INVALID_LABELS = [
    'stat:duplicate',
    'type:support'
]


class Issue:
    def __init__(self, json, repository, index):
        self.json_data = json[index]['node']
        self.repository = repository
        self.created_date = time.mktime(datetime.datetime.strptime(self.json_data['createdAt'], FORMAT).timetuple())
        self.closed_date = time.mktime(datetime.datetime.strptime(self.json_data['closedAt'], FORMAT).timetuple())
        self.fix_time = self.closed_date - self.created_date

        self.fork = 0

    def get_related_fork(self):
        if self.fork != 0:
            return self.fork

        for node in self.json_data['timelineItems']['nodes']:
            if 'id' in node and 'source' in node and 'commits' in node['source']:
                self.fork = Fork(node, self.repository, self)
                if self.fork.is_valid():
                    return self.fork

        self.fork = None
        return None

    def is_valid(self):

        for c in self.json_data['timelineItems']['nodes']:
            if 'stateReason' in c and c['stateReason'] != 'COMPLETED':
                return False

        for label in self.json_data['labels']['nodes']:
            if label['name'] in INVALID_LABELS:
                return False

        return self.get_related_fork() is not None

    def get_total_cyclomatic_complexity(self):
        return self.commit.get_total_cyclomatic_complexity()
