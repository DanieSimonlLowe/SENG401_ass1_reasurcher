import requests
import json

from Commit import Commit
from constant import BASE_URL, TOKEN


# https://github.com/orgs/community/discussions/24367

class Issue:
    def __init__(self, json, repository):
        self.json_data = json
        self.repository = repository
        self.commit = None

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
        print(req.json())
        commits = req.json()['data']['repository']['issue']['timelineItems']['nodes']
        print(commits)
        for commit in commits:
            if len(commit) > 0:
                self.commit = Commit(self.repository, commit)
                return self.commit

    def is_valid(self):
        pass
