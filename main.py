from random import random

import requests
import webbrowser

from issue import Issue


token = 'token'


def get_search_url(project):
    return f"https://api.github.com/search/issues?q=repo:{project}is:issue+state:closed+labels=bug"


def get_issue_count(project):
    r = requests.get(base_search_url,
                     data={
                         'access_token': token
                     })
    return r.json()['total_count']


def get_issue(project, issue_number):
    r = requests.get(base_search_url + '&page=' + str(issue_number),
                     data={
                         'access_token': token
                     })

    return Issue(r.json()['items'][0])


def get_random_issues(project, aim_count):
    looked = set()
    issues = []
    count = get_issue_count(project)
    if count < aim_count:
        aim_count = count

    while len(issues) < aim_count:
        look = random.randrange(count)
        while look in looked:
            look = random.randrange(count)

        looked.add(look)
        issue = get_issue(project, look)
        if issue.is_valid():
            issues.append(issue)

    return issues
