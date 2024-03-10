import time
import datetime

import requests

from Commit import Commit
from constant import BASE_URL, TOKEN


FORMAT = "%Y-%m-%dT%H:%M:%SZ"

class Issue:
    def __init__(self, json, repository):
        self.json_data = json
        self.repository = repository
        self.commit = ''
        self.commit = self.get_linked_commit()
        self.created_date = time.mktime(datetime.datetime.strptime(json['created_at'],FORMAT).timetuple())
        self.closed_date = time.mktime(datetime.datetime.strptime(json['closed_at'],FORMAT).timetuple())
        self.fix_time = self.closed_date - self.created_date

    def get_linked_commit(self):
        if self.commit is not None:
            return self.commit

        query = """query {
                repository(owner: \"""" + self.repository.owner + """\", name: \"""" + self.repository.name + """\") {
                    issue(number: """ + str(self.json_data["number"]) + """) {
                        timelineItems(first: 50, itemTypes: REFERENCED_EVENT) {
                            nodes {
                                ... on ReferencedEvent {
                                    commit {
                                        oid
                                        message
                                        committedDate
                                    },
                                },
                            },
                        },
                    },
                },
            }
            """

        req = requests.post(f"{BASE_URL}graphql",
                           headers={
                               'Authorization': f'bearer {TOKEN}',
                           },
                           json={
                               'query': query
                           }
                           )

        commits = req.json()['data']['repository']['issue']['timelineItems']['nodes']

        for commit in commits:
            if len(commit) > 0:
                self.commit = Commit(self.repository, commit)
                return self.commit

    def is_valid(self):
        return self.get_linked_commit() is not None
