import os
import random
from time import sleep
import threading
from pandas import DataFrame
import requests

from constant import TOKEN, BASE_URL
from Issue import Issue
from git import Repo

ISSUE_COUNT = 100


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

        self.end_cursor = None
        self.has_next_page = True

    def set_repo(self):
        self.path = os.path.join('holder', f'{self.owner}_{self.name}')
        if os.path.exists(self.path):
            self.repo = Repo(path=self.path)
        else:
            self.repo = Repo.clone_from(f'https://github.com/{self.owner}/{self.name}', self.path)

    def __str__(self):
        return f'{self.owner}/{self.name}'

    def get_issues_json(self):
        after = ""
        if self.end_cursor is not None:
            after = f", after: \"{self.end_cursor}\""

        query = """query {
                        repository(owner: \"""" + self.owner + """\", name: \"""" + self.name + """\") {
                            issues(states: [CLOSED], labels: "type:bug", first: """ + str(ISSUE_COUNT) + after + """) {
                                edges {
                                    node {
                                        id
                                        createdAt
                                        closedAt
                                        url
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
                                        
                                        labels(first: 10) {
                                            nodes {
                                                name
                                            },
                                        },
                                    },
                                },
                                pageInfo {
                                    endCursor
                                    hasNextPage
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
        json = req.json()
        try:
            issues = json['data']['repository']['issues']['edges']
            self.end_cursor = json['data']['repository']['issues']['pageInfo']['endCursor']
            self.has_next_page = json['data']['repository']['issues']['pageInfo']['hasNextPage']
            return issues
        except KeyError as e:
            sleep(30)
            return self.get_issues_json()

    def get_random_issues(self, aim_count):
        looked = set()
        issues = []
        json = self.get_issues_json()

        bound = ISSUE_COUNT - ISSUE_COUNT / 5

        while len(issues) < aim_count:
            if len(looked) > bound:
                if not self.has_next_page:
                    break

                json = self.get_issues_json()
                looked = set()
            look = random.randrange(ISSUE_COUNT)
            while look in looked:
                look = random.randrange(ISSUE_COUNT)

            looked.add(look)
            issue = Issue(json, self, look)
            if issue.is_valid():
                issues.append(issue)

                print(f'{len(issues)} out of {aim_count} issues found')

        return issues

    def create_file(self, file_name, issue_count):
        issues = self.get_random_issues(issue_count)
        print('issues:', len(issues))
        times = []
        hashes = []
        urls = []
        changed = []

        self.repo_thread.join()

        for issue in issues:
            times.append(issue.fix_time)
            hashes.append(issue.get_linked_commit().hash)
            urls.append(issue.json_data['url'])
            changed.append(issue.get_linked_commit().get_changed_cyclomatic_complexity())

        df = DataFrame({'time': times, 'hashes': hashes, 'url': urls, 'changed': changed})

        df.to_csv(file_name, index=False)

    def get_branch(self, oid):
        if self.branchs is None:
            pass
