from Repository import Repository

rep = Repository('tensorflow', 'tensorflow')

issue = rep.get_issue(28)

issue.json_data['number'] = 1
# print(issue.json_data)
issue.get_linked_commit()
