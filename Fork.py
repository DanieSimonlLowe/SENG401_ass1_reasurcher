import os
from git import Repo
from Commit import Commit

class Fork:
    def __init__(self, name, owner, created_on):
        self.name = name
        self.owner = owner
        self.path = os.path.join('holder', f'{self.owner}_{self.name}')

        if os.path.exists(self.path):
            self.repo = Repo(path=self.path)
        else:
            self.repo = Repo.clone_from(f'https://github.com/{self.owner}/{self.name}', self.path)

        self.created_on = created_on
    
    def get_commits(self):
        log = self.repo.git.log('--pretty=format:"%h"', f'--since={self.created_on}')
        hashes = log.split('\n')
        commits = []
        for hash_id in hashes:
            commit = Commit(self, oid=hash_id)
            commits.append(commit)
        return commits
    
    def get_changed_files(self):
        commits = self.get_commits()
        return set.union(*commits)