import os
import random
from time import sleep
import threading

import git
from pandas import DataFrame
import requests

from Commit import Commit
from constant import TOKEN, BASE_URL
from Issue import Issue
from git import Repo

ISSUE_COUNT = 100


# only one of these can exist at a time.
class Repository:
    def __init__(self, owner, name, bug_tag):
        self.repo = None
        self.owner = owner
        self.name = name
        self.bug_tag = bug_tag
        self.path = None

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
                            issues(states: [CLOSED], labels: \"""" + self.bug_tag + """\", first: """ + str(
            ISSUE_COUNT) + after + """) {
                                edges {
                                    node {
                                        id
                                        createdAt
                                        closedAt
                                        url
                                        timelineItems(first: 50, itemTypes: [REFERENCED_EVENT, CLOSED_EVENT]) {
                                            nodes {
                                                ... on ReferencedEvent {
                                                    commit {
                                                        oid
                                                        url
                                                        committedDate
                                                        message
                                                    },
                                                    commitRepository {
                                                        isFork
                                                        name
                                                        owner
                                                    }
                                                },
                                                ... on ClosedEvent {
                                                    stateReason
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
            print('slept')
            sleep(30)
            return self.get_issues_json()

    def get_random_issues(self, aim_count):
        look = 0
        issues = []
        json = self.get_issues_json()

        while len(issues) < aim_count:
            if look >= ISSUE_COUNT or look >= len(json):
                if not self.has_next_page:
                    break

                json = self.get_issues_json()
                look = 0
            issue = Issue(json, self, look)
            look += 1
            if issue.is_valid():
                print(issue.json_data)
                issues.append(issue)
                print(f'{len(issues)} out of {aim_count} issues found')

        return issues

    def create_issues_file(self, file_name, issue_count):
        issues = self.get_random_issues(issue_count)
        print('issues:', len(issues))
        times = []
        hashes = []
        urls = []
        commits = []

        for issue in issues:
            times.append(issue.fix_time) # TODO What about commit time minus issue creation time?
            hashes.append(issue.get_linked_commit().hash)
            urls.append(issue.json_data['url'])
            commits.append(issue.get_linked_commit().json['url'])

        df = DataFrame({'time': times, 'hashes': hashes, 'url': urls, 'commits': commits})

        df.to_csv(file_name, index=False)

    def create_commit_file(self, file, name):
        repo_thread = threading.Thread(target=Repository.set_repo, args=(self,))
        repo_thread.start()
        times = []
        hashes = []
        urls = []
        complexity_av = []
        complexity_max = []
        complexity_total = []
        with open(file, 'r') as f:
            lines = f.readlines()
            print('loading repository data')
            repo_thread.join()
            for i in range(1, len(lines)):
                line = lines[i].split(',')
                time = line[0]
                oid = line[1]
                url = line[2]
                commit = Commit(self, oid=oid)
                print(f'{i} out of {len(lines) - 1}')
                try:
                    av, m, total = commit.get_changed_cyclomatic_complexity()

                    complexity_av.append(av)
                    complexity_max.append(m)
                    complexity_total.append(total)
                except TabError:
                    pass
                except SyntaxError:
                    pass
                except git.exc.GitCommandError:
                    pass
                else:
                    times.append(time)
                    urls.append(url)
                    hashes.append(oid)

        df = DataFrame({'time': times, 'hashes': hashes, 'url': urls,
                        'average complexity': complexity_av, 'max complexity': complexity_max,
                        'total complexity': complexity_total})

        df.to_csv(name, index=False)
