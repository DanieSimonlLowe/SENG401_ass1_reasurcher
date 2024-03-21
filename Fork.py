import os
import threading
from datetime import datetime
import time

import requests
from git import Repo
from Commit import Commit, get_cyclomatic_complexity
from constant import FILEPATH, TOKEN, BASE_URL

FORMAT = "%Y-%m-%dT%H:%M:%SZ"

PYTHON_FILE_EXTENSIONS = {
    'py', 'pyc', 'pyo', 'pycpp', 'pyi', 'pyd', 'pyw', 'pyz'
}


class Fork:
    def __init__(self, json, repository, issue):
        # add fork validilty check
        self.url = json['url']
        self.url2 = json['source']['url']
        self.repository = repository
        self.issue = issue
        self.commits_json = json['source']['commits']['edges']

        temp = json['source']['repository']['url'].split('/')
        self.owner = temp[3]
        self.repo = temp[4]

        self.files = None
        self.state = json['source']['state']
        # self.files_thread = threading.Thread(target=Fork.set_files, args=(self,))

    def parse_diff(self, diff_text):
        funcs = set()
        current_file = None
        for line in diff_text.split('\n'):

            # Check if the line indicates a function change in the hunk header
            if line.startswith('@@') and 'def ' in line:
                # Extract the function name
                function_name = line[line.index('def '):].split('(')[0].replace('def ', '').strip()
                funcs.add(function_name)

        return funcs

    def set_file(self, oid, out, count=0):
        text = f"{BASE_URL}repos/{self.owner}/{self.repo}/commits/{oid}"
        req = requests.get(text,
                           headers={
                               'Authorization': f'bearer {TOKEN}',
                           },
                           )
        json = req.json()
        if 'files' not in json:
            print(json)
            if count > 15:
                raise TimeoutError(f'Timed out waiting for {text}')
            print('slept')
            time.sleep(120)
            return self.set_file(oid, out, count + 1)
        for file in json['files']:
            if 'filename' not in file or 'patch' not in file:
                continue
            current_file = file['filename']
            path = os.path.join(self.repository.path, current_file)
            if os.path.exists(path):
                patch = self.parse_diff(file['patch'])
                if path in out:
                    for func in patch:
                        out[path].add(func)
                else:
                    out[path] = patch

    def get_changed_files(self):
        threads = []
        out = dict()
        for node in self.commits_json:
            oid = node['node']['commit']['oid']
            thread = threading.Thread(target=Fork.set_file, args=(self, oid, out))
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()
        return out

    def calculate_complexity(self):
        log = self.repository.repo.git.log('-r', '--pretty=format:%h',
                                           f'--before="{self.issue.created_date}"')
        oid = log.split('\n')[0]
        self.repository.repo.git.checkout('-f', oid)

        files = self.get_changed_files()
        print(files)
        return get_cyclomatic_complexity(files)

    def is_valid(self):
        return self.state == 'MERGED'
