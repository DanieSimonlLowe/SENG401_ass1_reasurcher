import os
import random
from time import sleep
import threading

import git
from pandas import DataFrame
import requests

from Commit import Commit, get_cyclomatic_complexity
from Fork import Fork
from constant import TOKEN, BASE_URL, FILEPATH
from Issue import Issue
from git import Repo

ISSUE_COUNT = 100


# only one of these can exist at a time.
class Repository:
    def __init__(self, owner, name, bug_tag='bug'):
        self.repo = None
        self.owner = owner
        self.name = name
        self.bug_tag = bug_tag
        self.path = None
        self.repo_thread = None
        self.end_cursor = None
        self.has_next_page = True
        self.timeout = 0

        self.thread_called = False

    def set_repo(self):
        if self.thread_called:
            return
        self.thread_called = True
        self.path = os.path.join(FILEPATH, f'{self.owner}_{self.name}')
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
                            issues(states: [CLOSED], first: """ + str(
            ISSUE_COUNT) + after + """) {
                                edges {
                                    node {
                                        id
                                        createdAt
                                        closedAt
                                        url
                                        timelineItems(last: 5, itemTypes: [CLOSED_EVENT, CROSS_REFERENCED_EVENT]) {
                                            nodes {
                                                ... on ClosedEvent {
                                                    stateReason
                                                }
                                                ... on CrossReferencedEvent {
                                                    id
                                                    url
                                                    source {
                                                        ... on PullRequest {
                                                            repository {
                                                                url
                                                            }
                                                            commits(first: 20) {
                                                                edges {
                                                                    node {
                                                                        commit {
                                                                            abbreviatedOid
                                                                        }
                                                                    }
                                                                }
                                                            }
                                                        }
                                                    }
                                                }
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
        print(json)

        try:
            issues = json['data']['repository']['issues']['edges']
            self.end_cursor = json['data']['repository']['issues']['pageInfo']['endCursor']
            self.has_next_page = json['data']['repository']['issues']['pageInfo']['hasNextPage']

            print('new json generated')
            return issues
        except KeyError as e:
            if self.timeout > 10:
                self.has_next_page = False
            print('slept')
            self.timeout += 1
            # print(json)
            sleep(30)
            return self.get_issues_json()

    def get_random_issues(self, aim_count):
        look = 0
        issues = []
        json = self.get_issues_json()

        while len(issues) < aim_count:
            if look >= len(json):
                if not self.has_next_page:
                    break

                json = self.get_issues_json()
                look = 0
            issue = Issue(json, self, look)
            look += 1
            if issue.is_valid():
                issues.append(issue)
                print(f'{len(issues)} out of {aim_count} issues found')
        return issues

    def create_commit_file(self, aim_count, name):
        repo_thread = threading.Thread(target=Repository.set_repo, args=(self,))
        repo_thread.start()
        issues = self.get_random_issues(aim_count)

        times = []
        urls = []
        complexity_av = []
        complexity_max = []
        complexity_total = []
        print('waiting for tread clone')
        repo_thread.join()
        print('starting analysis')
        for issue in issues:
            try:
                av, m, total = issue.get_related_fork().calculate_complexity()
                complexity_av.append(av)
                complexity_max.append(m)
                complexity_total.append(total)
                times.append(issue.fix_time)
                urls.append(issue.get_related_fork().url)

                # issue.get_related_fork().delete()
                print(f'{len(urls)} out of {len(issues)} issues found')
            except TabError as e:
                print(e)
            except SyntaxError as e:
                print(e)
            except git.exc.GitCommandError as e:
                print(e)

        df = DataFrame({'time': times, 'url': urls,
                        'average complexity': complexity_av, 'max complexity': complexity_max,
                        'total complexity': complexity_total})

        df.to_csv(name, index=False)
