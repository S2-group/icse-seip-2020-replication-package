import json

__name__ = 'configuration'

NUM_COMMITS = 100
NUM_STARS = 2

github_username = 'INSERT_HERE_GITHUB_USERNAME'
github_key = 'INSERT_HERE_GITHUB_KEY'

organization_project_separator = '_____'

def save(filePath, data):
    with open(filePath, 'w') as outfile:  
        json.dump(data, outfile)