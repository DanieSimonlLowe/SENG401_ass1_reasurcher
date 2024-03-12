import os
import random
import shutil
import threading
from pandas import DataFrame
import requests

from constant import TOKEN, BASE_URL
from Issue import Issue
from git import Repo


# only one of these can exist at a time.
class Repository:
    def __init__(self, owner, name):
        self.repo = None
        self.owner = owner
        self.name = name
        self.repo_thread = threading.Thread(target=Repository.set_repo, args=(self,))
        self.path = None
        self.repo_thread.start()
        self.repo_thread.join()

        self.branchs = None

        self.last_issue = 'null'

    def set_repo(self):
        self.path = os.path.join('holder', f'{self.owner}_{self.name}')
        print(self.path + '\n')
        if os.path.exists(self.path):
            self.repo = Repo(path=self.path)
        else:
            self.repo = Repo.clone_from(f'https://github.com/{self.owner}/{self.name}', self.path)

    def __str__(self):
        return f'{self.owner}/{self.name}'

    def get_issues_json(self):
        query = """query {
                        repository(owner: \"""" + self.owner + """\", name: \"""" + self.name + """\") {
                            issues(states: [CLOSED], first: 100 after: """ + self.last_issue + """) {
                                edges {
                                    node {
                                        id
                                        createdAt
                                        closedAt
                                        timelineItems(first: 50, itemTypes: REFERENCED_EVENT) {
                                            nodes {
                                                ... on ReferencedEvent {
                                                    commit {
                                                        oid
                                                        url
                                                        committedDate
                                                    },
                                                },
                                            },
                                        },
                                    }
                                }
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
        json = req.json()
        issues = json['data']['repository']['issues']['edges']
        self.last_issue = issues[-1]['node']['id']
        return issues

    def get_random_issues(self, aim_count):
        looked = set()
        issues = []
        json = self.get_issues_json()

        end = 100

        while len(issues) < aim_count:
            if len(looked) > end/2:
                json = self.get_issues_json()
            look = random.randrange(end)
            while look in looked:
                look = random.randrange(end)

            looked.add(look)
            issue = Issue(json, self, look)
            if issue.is_valid():
                print(look)
                issues.append(issue)

        return issues

    def create_file(self, file_name, issue_count):
        issues = self.get_random_issues(issue_count)
        times = []
        complexity = []

        for issue in issues:
            times.append(issue.fix_time)
            complexity.append(issue.get_total_cyclomatic_complexity())

        df = DataFrame({'time': times, 'complexity': complexity})

        df.to_csv(file_name, index=False)

    def get_branch(self, oid):
        if self.branchs is None:
            req
