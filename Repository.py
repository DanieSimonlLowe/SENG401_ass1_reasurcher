import random

import requests

from constant import TOKEN, BASE_URL
from Issue import Issue
from git import Repo

class Repository:
    def __init__(self, owner, name):
        self.owner = owner
        self.name = name
        self.repo = Repo.clone_from(f'https://github.com/{self.owner}/{self.name}', 'holder')

    def __str__(self):
        return f'{self.owner}/{self.name}'

    def get_search_url(self):
        return f"{BASE_URL}search/issues?q=repo:{self}+is:issue+state:closed+labels=bug"

    def get_issue_count(self):
        r = requests.get(self.get_search_url(self),
                         data={
                             'access_token': TOKEN
                         })
        return r.json()['total_count']

    def get_issue(self, issue_number):
        r = requests.get(f"{self.get_search_url()}&page={issue_number}",
                         data={
                             'access_token': TOKEN
                         })

        return Issue(r.json()['items'][0], self)

    def get_random_issues(self, aim_count):
        looked = set()
        issues = []
        count = self.get_issue_count()
        if count < aim_count:
            aim_count = count

        while len(issues) < aim_count:
            look = random.randrange(count)
            while look in looked:
                look = random.randrange(count)

            looked.add(look)
            issue = self.get_issue(look)
            if issue.is_valid():
                issues.append(issue)

        return issues