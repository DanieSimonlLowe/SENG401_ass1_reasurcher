import time
import datetime

import requests

from Commit import Commit
from constant import BASE_URL, TOKEN

FORMAT = "%Y-%m-%dT%H:%M:%SZ"


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

        for commit in commits:
            if len(commit) > 0:
                print(commit)
                commit = Commit(self.repository, commit['commit'])
                if commit.is_valid():
                    self.commit = commit
                    return self.commit

    def is_valid(self):
        return self.get_linked_commit() is not None

    def get_total_cyclomatic_complexity(self):
        return self.commit.get_total_cyclomatic_complexity()
