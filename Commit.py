import datetime
import os

import requests
from radon.visitors import ComplexityVisitor

from constant import TOKEN

FORMAT = "%Y-%m-%dT%H:%M:%SZ"

PYTHON_FILE_EXTENSIONS = {
    'py', 'pyc', 'pyo', 'pycpp', 'pyi', 'pyd', 'pyw', 'pyz'
}


def get_cyclomatic_complexity(files):
    complexity = 0
    count = 0
    max = 0
    lines = 0
    for file, funcs in files.items():
        try:
            with open(file, 'r') as f:
                text = f.read()
                lines += text.count('\n')
                vistor = ComplexityVisitor.from_code(text, no_assert=True)
                for function in vistor.functions:
                    if function.name in funcs:
                        complexity += function.complexity
                        if function.complexity > max:
                            max = function.complexity
                        count += 1

        except FileNotFoundError:
            pass

    if count == 0:
        return 0, 0, 0, 0

    return complexity / count, max, complexity, complexity / lines


class Commit:
    def __init__(self, repository, json=None, oid=None):
        self.total_cyclomatic_complexity = None
        self.repository = repository
        self.json = json
        if json is not None:
            self.hash = self.json["oid"]
        if oid is not None:
            self.hash = oid
        self.url = self.json.get('url')

    def checkout(self):
        parent = self.repository.repo.git.rev_parse(f'{self.hash}^')
        self.repository.repo.git.checkout('-f', parent)

    def changed(self):
        text = self.repository.repo.git.diff_tree('--no-commit-id', '--name-only', self.hash, '-r')
        out = []
        for file in text.split('\n'):
            extension = file.split('.')[-1]
            if extension in PYTHON_FILE_EXTENSIONS:
                out.append(os.path.join(self.repository.path, file))
        return out

    def get_all_files(self, directory=None):
        if directory is None:
            directory = self.repository.path

        self.repository.repo_thread.join()
        out = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                extension = file.split('.')[-1]
                if extension in PYTHON_FILE_EXTENSIONS:
                    out.append(os.path.join(root, file))
            for dir in dirs:
                out += self.get_all_files(os.path.join(root, dir))

        return out

    def get_total_cyclomatic_complexity(self):
        self.checkout()
        return get_cyclomatic_complexity(self.get_all_files())

    def get_changed_cyclomatic_complexity(self):
        self.checkout()
        return get_cyclomatic_complexity(self.changed())

    def is_valid(self):
        # print(commit_message)
        if str(self.repository) in self.json['url']:
            return False
        commit_message = self.json['message'].lower()
        return any(keyword in commit_message for keyword in ["fix"])  # TODO make sure commit is in correct repository

    def get_diff_text(self):
        headers = {
            'Authorization': f'token {TOKEN}',
            'Accept': 'application/vnd.github.v3.diff'
        }
        diff_url = self.url + ".diff"
        response = requests.get(diff_url, headers=headers)
        if response.status_code == 200:
            return response.text
        else:
            error_message = response.json().get('message', 'No error message available')
            print(f"Error fetching commit diff: {response.status_code}, Message: {error_message}")
            return None

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

        # Convert sets to lists for easier use later
        for file in files_and_functions:
            files_and_functions[file] = list(files_and_functions[file])

        return files_and_functions
