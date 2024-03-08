from Repository import Repository

rep = Repository('tensorflow', 'tensorflow')

issue = rep.get_issue(28)

issue.json_data['number'] = 1
# print(issue.json_data)
issue.get_linked_commit()

def get_repositories(path):
    """Reads a list of repository ids in the format: 
    "name,owner"
    and returns a list of Repository objects
    """
    repos_file = open(path, 'r')
    repo_strings = [tuple(repo.split(',')) for repo in repos_file.read().splitlines()]
    repositories = [Repository(name, owner) for name, owner in repo_strings]
    return repositories