import datetime
import os
import time
from radon.visitors import ComplexityVisitor

from constant import FILEPATH, BASE_URL, TOKEN

FORMAT = "%Y-%m-%dT%H:%M:%SZ"

PYTHON_FILE_EXTENSIONS = {
    'py', 'pyc', 'pyo', 'pycpp', 'pyi', 'pyd', 'pyw', 'pyz'
}


def get_cyclomatic_complexity(files):
    complexity = 0
    count = 0
    max = 0
    for file in files:
        try:
            with open(file, 'r') as f:
                text = f.read()
                vistor = ComplexityVisitor.from_code(text, no_assert=True)
                for function in vistor.blocks:
                    complexity += function.complexity
                    if function.complexity > max:
                        max = function.complexity
                    count += 1

        except FileNotFoundError:
            pass

    if count == 0:
        return 0, 0, complexity

    return complexity / count, max, complexity


class Commit:
    def __init__(self, repository, json=None, oid=None):
        self.total_cyclomatic_complexity = None
        self.repository = repository
        self.json = json
        if json is not None:
            self.hash = self.json["oid"]
        if oid is not None:
            self.hash = oid

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
        return True
