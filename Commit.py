import os
from radon.complexity import cc_rank

from constant import FILEPATH

PYTHON_FILE_EXTENSIONS = {
    'py', 'pyc', 'pyo', 'pycpp', 'pyi', 'pyd', 'pyw', 'pyz'
}


def get_cyclomatic_complexity(files):
    text = ''
    for file in files:
        with open(file, 'r') as f:
            # https://radon.readthedocs.io/en/latest/api.html#module-radon.complexity
            text += f.read() + '\n'

    return cc_rank(text)


class Commit:
    def __init__(self, repository, json):
        self.total_cyclomatic_complexity = None
        self.repository = repository
        self.json = json
        self.lastHash = json['oid']

        log = self.repository.repo.git.log(f'{self.lastHash} --pretty=format:"%h" --no-patch')
        self.hash = log.split('\n')[1]

    def checkout(self):
        self.repository.repo.git.cherry_pick(self.hash)

    def changed(self):
        text = self.repository.repo.git.diff_tree('--no-commit-id', '--name-only', self.hash, '-r')

        return text.split('\n')

    def get_all_files(self):
        self.repository.repo_thread.join()
        out = []
        for root, dirs, files in os.walk(self.repository.path):
            for file in files:
                extension = file.split('.')[-1]
                if extension in PYTHON_FILE_EXTENSIONS:
                    out.append(os.path.join(root, file))
            for dir in dirs:
                out += self.get_all_files(os.path.join(root, dir))

        return out

    def get_total_cyclomatic_complexity(self):
        return get_cyclomatic_complexity(self.get_all_files())