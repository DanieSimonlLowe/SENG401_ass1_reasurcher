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

    # def parse_diff(self, diff_text):
    #     funcs = set()
    #     current_file = None
    #     for line in diff_text.split('\n'):
    #
    #         # Check if the line indicates a function change in the hunk header
    #         if line.startswith('@@') and 'def ' in line:
    #             # Extract the function name
    #             function_name = line[line.index('def '):].split('(')[0].replace('def ', '').strip()
    #             funcs.add(function_name)
    #
    #     return funcs

    def parse_diff(self, diff_text):
        files_and_functions = {}
        current_file = None
        for line in diff_text.split('\n'):
            # Check if the line indicates a file change
            if line.startswith('diff --git'):
                # Extract the file name from the diff --git line
                parts = line.split(' ')
                if len(parts) >= 3:
                    current_file = parts[2][2:]  # Remove the 'b/' prefix
                    if current_file not in files_and_functions:
                        files_and_functions[current_file] = set()
            # Check if the line indicates a function change in the hunk header
            elif line.startswith('@@') and 'def ' in line:
                # Extract the function name
                function_name = line[line.index('def '):].split('(')[0].replace('def ', '').strip()
                if current_file:
                    files_and_functions[current_file].add(function_name)

        return files_and_functions

    def set_file(self, oid, out, count=0):
        text = f"https://github.com/{self.owner}/{self.repo}/commit/{oid}.diff"
        req = requests.get(text,
                           headers={
                               'Authorization': f'bearer {TOKEN}',
                           },
                           )
        patch = self.parse_diff(req.text)

        for file, funcs in patch.items():
            ext = file.split('.')[-1]
            if ext not in PYTHON_FILE_EXTENSIONS:
                continue
            path = os.path.join(self.repository.path, file)
            if os.path.exists(path):
                if path in out:
                    for func in funcs:
                        out[path].add(func)
                else:
                    out[path] = funcs


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
        return get_cyclomatic_complexity(files)

    def is_valid(self):
        return self.state == 'MERGED'
