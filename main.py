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

rep = Repository('numpy', 'numpy', "")

print('repo created')

rep.create_commit_file(500, "text.csv", )

# rep.create_commit_file("text.csv", 'out.csv')
