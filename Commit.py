import os


from radon.visitors import ComplexityVisitor

from constant import FILEPATH, BASE_URL, TOKEN

PYTHON_FILE_EXTENSIONS = {
    'py', 'pyc', 'pyo', 'pycpp', 'pyi', 'pyd', 'pyw', 'pyz'
}


def get_cyclomatic_complexity(files):
    print(files)
    text = ''
    for file in files:
        try:
            with open(file, 'r') as f:
                text += f.read() + '\n'
        except FileNotFoundError:
            pass

    if text.count('def ') == 0:
        return 0

    vistor = ComplexityVisitor.from_code(text)
    return vistor.functions_complexity / text.count('def ')



class Commit:
    def __init__(self, repository, json):
        self.total_cyclomatic_complexity = None
        self.repository = repository
        self.json = json
        self.hash = self.json["oid"]

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
        return str(self.repository) in self.json['url']
