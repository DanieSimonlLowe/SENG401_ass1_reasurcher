import os
import threading

from git import Repo
from Commit import Commit


class Fork:
    def __init__(self, name, issue_creation, issue_close):
        self.issue_creation = issue_creation
        self.issue_close = issue_close
        self.name = name
        self.path = os.path.join('holder', f'fork_{name.replace("/", "_").strip()}')
        self.repo = None
        self.repo_thread = threading.Thread(target=Fork.set_repo, args=(self,))
        self.repo_thread.start()

    def set_repo(self):
        if os.path.exists(self.path):
            self.repo = Repo(path=self.path)
        else:
            self.repo = Repo.clone_from(f'https://github.com/{self.name}', self.path)

    def get_commits(self):
        first = self.name.split('/')[0]

        self.repo_thread.join()
        log = self.repo.git.log('--pretty=format:%h', f'--since={self.issue_creation}', f'--before={self.issue_close}',
                                                                                        f'--author={first}')
        hashes = log.split('\n')
        commits = []
        for hash_id in hashes:
            commit = Commit(self, oid=hash_id)
            commits.append(commit)
        return commits

    def get_changed_files(self):
        commits = self.get_commits()
        files = set()
        for commit in commits:
            files.update(commit.changed())
        return list(files)
