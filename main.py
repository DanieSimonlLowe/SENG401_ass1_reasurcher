from Repository import Repository

# ---------------------------------
# tensorflow: type:bug
# pandus: bug
# ---------------------------------

rep = Repository('tensorflow', 'tensorflow', "type:bug")

print('repo created')

rep.create_issues_file("text.csv", 50)

rep.create_commit_file('text.csv', 'output.csv')
