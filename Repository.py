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

    def set_repo(self):
        self.path = os.path.join('holder', f'{self.owner}_{self.name}')
        print(self.path + '\n')
        if os.path.exists(self.path):
            self.repo = Repo(path=self.path)
        else:
            self.repo = Repo.clone_from(f'https://github.com/{self.owner}/{self.name}', self.path)

    def __str__(self):
        return f'{self.owner}/{self.name}'

    def get_search_url(self):
        return f"{BASE_URL}search/issues?q=repo:{self}+is:issue+state:closed+labels=bug&per_page=100"

    def get_issues_json(self):
        r = requests.get(self.get_search_url(),
                         headers={
                             'Authorization': f'bearer {TOKEN}',
                         })
        return r.json()

    # api has a 10 request limit seemingly per run?
    def get_issue(self, issue_number, json):
        # r = requests.get(f"{self.get_search_url()}&page={issue_number}&per_page=1",
        #                  headers={
        #                      'Authorization': f'bearer {TOKEN}',
        #                  })
        #
        # print(r.json())
        return Issue(json['items'][issue_number], self)

    def get_random_issues(self, aim_count):
        looked = set()
        issues = []
        json = self.get_issues_json()

        total_count = json['total_count']
        end = len(json['items'])
        start = 0
        if total_count < aim_count:
            aim_count = total_count

        while len(issues) < aim_count:
            look = random.randrange(end)
            while look in looked:
                look = random.randrange(end)
            print(look)
            looked.add(look)
            issue = self.get_issue(look, json)
            if issue.is_valid():
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
