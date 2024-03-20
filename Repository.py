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

    def get_issues_json(self, timeout=0):
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
                                                            url
                                                            state
                                                            repository {
                                                                url
                                                            }
                                                            commits(first: 20) {
                                                                edges {
                                                                    node {
                                                                        commit {
                                                                            oid
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

        try:
            issues = json['data']['repository']['issues']['edges']
            self.end_cursor = json['data']['repository']['issues']['pageInfo']['endCursor']
            self.has_next_page = json['data']['repository']['issues']['pageInfo']['hasNextPage']

            print('new json generated')
            return issues
        except KeyError as e:
            if timeout > 15:
                self.has_next_page = False
            print('slept')
            sleep(120)
            return self.get_issues_json(timeout+1)

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

    def create_commit_file_helper(self, aim_count, repo_thread):

        issues = self.get_random_issues(aim_count)
        times = []
        urls = []
        urls2 = []
        complexity_av = []
        complexity_max = []
        complexity_total = []
        print('waiting for tread clone')
        repo_thread.join()
        print('starting analysis')
        for issue in issues:
            try:
                av, m, total = issue.get_related_fork().calculate_complexity()
                if av == 0:
                    continue
                complexity_av.append(av)
                complexity_max.append(m)
                complexity_total.append(total)
                times.append(issue.fix_time)
                urls.append(issue.get_related_fork().url)
                urls2.append(issue.get_related_fork().url2)

                # issue.get_related_fork().delete()
                print(f'{len(urls)} out of {len(issues)} issues analyzed')
            except TabError as e:
                print(e)
            except SyntaxError as e:
                print(e)
            except git.exc.GitCommandError as e:
                print(e)
        return times, urls, urls2, complexity_av, complexity_max, complexity_total

    def create_commit_file(self, aim_count, name):
        repo_thread = threading.Thread(target=Repository.set_repo, args=(self,))
        repo_thread.start()
        times = []
        urls = []
        urls2 = []
        complexity_av = []
        complexity_max = []
        complexity_total = []

        try_count = 1
        while len(times) < aim_count and try_count < 10:
            print(f'retrival try {try_count}')
            try_count += 1
            o_times, o_urls, o_urls2, o_complexity_av, o_complexity_max, o_complexity_total = (
                self.create_commit_file_helper(aim_count - len(times), repo_thread))
            times += o_times
            urls += o_urls
            urls2 += o_urls2
            complexity_av += o_complexity_av
            complexity_max += o_complexity_max
            complexity_total += o_complexity_total

        df = DataFrame({'time': times, 'url': urls, 'url2': urls2,
                        'average complexity': complexity_av, 'max complexity': complexity_max,
                        'total complexity': complexity_total})

        df.to_csv(name, index=False)
