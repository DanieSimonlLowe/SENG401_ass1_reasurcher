from Repository import Repository

rep = Repository('tensorflow', 'tensorflow')

issue = rep.get_issue(5)
#print(issue.json_data)
issue.get_linked_commit()
