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

rep = Repository('tensorflow', 'tensorflow', "type:bug")

print('repo created')

rep.create_issues_file("text.csv", 500)
