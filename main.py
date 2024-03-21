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

rep = Repository('pytorch', 'pytorch', "type:bug")

print('repo created 1')

rep.create_commit_file(99999999999, "pytorch.csv", 999999999)

