class Commit:
    def __init__(self, repository, json):
        self.repository = repository
        self.json = json
        self.hash = json['oid']
        self.main = self.repository.repo.commit(self.hash)

