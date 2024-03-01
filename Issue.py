import requests
import json

from constant import BASE_URL, TOKEN


# https://github.com/orgs/community/discussions/24367

class Issue:
    def __init__(self, json, repository):
        self.json_data = json
        self.repository = repository

    def get_linked_commit(self):
        #TODO finish this
        a = """
            query: {
                repository(owner: '""" + self.repository.owner + """', name: '"""+self.repository.name+"""'): {
                    issue(id: """+self.json_data["node_id"]+"""): {
                        'timelineItems(first: 5)': {
                            'nodes': {
                                '... on ClosedEvent': {
                                    'closer': {
                                        '... on PullRequest': "{"
                                                              "number,\n"
                                                              "title"
                                                              "}"
                                    },
                                },
                            },
                        },
                    },
                },
            }
            """

        # a = json.dumps(a)
        # print(a)

        req = requests.get(f"{BASE_URL}graphql",
                           headers={
                               'Authorization': f'bearer {TOKEN}',
                           },
                           data=a
        )
        print(req.json())

    def is_valid(self):
        pass
