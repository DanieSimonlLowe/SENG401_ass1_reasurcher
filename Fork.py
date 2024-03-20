import os
import threading
from datetime import datetime
import time

from git import Repo
from Commit import Commit, get_cyclomatic_complexity

FORMAT = "%Y-%m-%dT%H:%M:%SZ"


class Fork:
    def __init__(self, json, repository, issue):
        #add fork validilty check
        self.url = json['url']
        self.commits_json = json['source']['commits']['edges']
        self.repository = repository
        self.issue = issue
        self.commits = None

        temp = json['source']['repository']['url'].split('/')
        self.name = f'{temp[3]}/{temp[4]}'
        self.path = os.path.join('holder', f'fork_{temp[3]}_{temp[4]}')

        self.repo = None
        self.repo_thread = threading.Thread(target=Fork.set_repo, args=(self,))
        self.repo_thread.start()

    def set_repo(self):
        if os.path.exists(self.path):
            self.repo = Repo(path=self.path)
        else:
            self.repo = Repo.clone_from(f'https://github.com/{self.name}', self.path)

    def get_commits(self):
        if self.commits is not None:
            return self.commits

        self.commits = []
        for node in self.commits_json:
            if 'commit' in node['node'] and 'abbreviatedOid' in node['node']['commit']:
                commit = Commit(self, oid=node['node']['commit']['abbreviatedOid'])
                self.commits.append(commit)
        return self.commits

    def get_changed_files(self):
        commits = self.get_commits()
        files = set()
        for commit in commits:
            files.update(commit.changed())
        return list(files)

    def calculate_complexity(self):
        log = self.repository.repo.git.log('-r', '--pretty=format:%h',
                                           f'--before="{self.issue.created_date}"')
        oid = log.split('\n')[0]
        self.repository.repo.git.checkout('-f', oid)
        self.repo_thread.join()

        files = self.get_changed_files()
        return get_cyclomatic_complexity(files)
