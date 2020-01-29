import json
import sys
import logging
import os
from git import Repo
import configuration as c

repos_to_clone = './repos_mining_data/otherData/repos_to_clone.json'
cloned_repos_json = './repos_mining_data/otherData/cloned_repos.json'
clones_path = '../Repos/'

def get_clone_path(repo, is_absolute):
    if(is_absolute):
        return os.path.abspath(clones_path + repo['id'].replace("/", organization_project_separator))
    else:
        return clones_path + repo['id'].replace("/", organization_project_separator)

def clone_repo(repo, path_to_clone):
    try:
        if(not os.path.exists(path_to_clone)):
            Repo.clone_from(url = repo['clone_url'], to_path = path_to_clone)
        else:
            print("Jumped repo because its folder already exists: " + repo['id'])
    except Er:
        print("Error for: " + repo['id'])
        print(sys.exc_info()[0])


def start_cloning():
    with open(repos_to_clone, 'r') as f:  
        repos_list = json.load(f)
        counter = 1
        cloned_repos = list()
        for p in repos_list:
            print("Cloning repo number " + str(counter) + " --- " + p['id'])
            counter += 1
            absolute_path_to_clone = get_clone_path(p, True)
            local_path_to_clone = get_clone_path(p, False)
            clone_repo(p, absolute_path_to_clone)
            p['absolute_clone_path'] = absolute_path_to_clone
            p['local_clone_path'] = local_path_to_clone
            cloned_repos.append(p)
    c.save(cloned_repos_json, cloned_repos)

start_cloning()