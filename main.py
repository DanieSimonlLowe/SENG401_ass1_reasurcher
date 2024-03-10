from Repository import Repository

rep = Repository('tensorflow', 'tensorflow')

rep.create_file("text.csv", 1)


def get_repositories(path):
    """Reads a list of repository ids in the format: 
    "name,owner"
    and returns a list of Repository objects
    """
    repos_file = open(path, 'r')
    repo_strings = [tuple(repo.split(',')) for repo in repos_file.read().splitlines()]
    repositories = [Repository(name, owner) for name, owner in repo_strings]
    return repositories
