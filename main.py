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

rep = Repository('numpy', 'numpy', "00 - Bug")

print('repo created')

rep.create_commit_file(20, "text.csv", )

# rep.create_commit_file("text.csv", 'out.csv')
