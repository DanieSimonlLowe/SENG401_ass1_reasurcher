import os
import random
import shutil
import threading

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
        self.repo_thread.start()
        self.repo_thread.join()

    def set_repo(self):
        path = os.path.join('holder', f'{self.owner}_{self.name}')
        print(path + '\n')
        self.repo = Repo.clone_from(f'https://github.com/{self.owner}/{self.name}', path)

    def __str__(self):
        return f'{self.owner}/{self.name}'

    def clear_holder(self):
        for filename in os.listdir('holder'):
            file_path = os.path.join('holder', filename)
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)

    def get_search_url(self):
        return f"{BASE_URL}search/issues?q=repo:{self}+is:issue+state:closed+labels=bug"

    def get_issue_count(self):
        r = requests.get(self.get_search_url(),
                         data={
                             'access_token': TOKEN
                         })
        return r.json()['total_count']

# api has a 10 request limit seemingly per run?
    def get_issue(self, issue_number):
        r = requests.get(f"{self.get_search_url()}&page={issue_number}&per_page=1",
                         data={
                             'access_token': TOKEN
                         })
        print(r.json())
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
