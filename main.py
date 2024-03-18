from Repository import Repository

# ---------------------------------
# tensorflow: type:bug
# pandus: bug
# ansible: bug,
# scikit-learn: bug
# numpy: 00+-+bug
# matplotlib: status%3A+confirmed+bug
# scrapy: bug
# ---------------------------------

rep = Repository('python', 'cpython', "type-bug")
# rep.set_repo()
print('repo created')

# rep.create_issues_file('text.csv', 50)
rep.create_commit_file("text.csv", 'test.csv')
