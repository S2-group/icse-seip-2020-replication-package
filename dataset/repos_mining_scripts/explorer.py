import time
import urllib3
import json
import sys
import logging
import certifi
import os
import random
import re
from datetime import datetime
import csv
import time
import configuration as c

def form_request(url: str) -> urllib3.response:
        time.sleep(random.random() * 2)
        http = urllib3.PoolManager(ca_certs=certifi.where())
        return http.request('GET', url)

def get_bitbucket_repo_substring(url):
        project_string = url.split("https://bitbucket.org/")[1]
        project_string = project_string.split(".git")[0]
        return project_string

def get_gitlab_repo_substring(url):
        project_string = url.split("https://gitlab.com/")[1]
        project_string = project_string.split(".git")[0]
        project_string = project_string.replace("/", "%2F")
        return project_string

def get_github_repo_substring(url):
    if(url.startswith("https://github.com")):
        project_string = url.split("https://github.com/")[1]
        project_string = project_string.split(".git")[0]
    if(url.startswith("https://api.github.com")):
        project_string = url.split("https://api.github.com/repos/")[1]
    return project_string

def commit_to_repo_name(url):
    project_string = url.split("https://api.github.com/repos/")[1]
    project_string = project_string.split("/git/commits/")[0]
    return project_string

def get_bitbucket_data(repo_url):
    project_string = get_bitbucket_repo_substring(repo_url)
    response = form_request(
        "https://api.bitbucket.org/2.0/repositories/" + project_string)
    if response.status == 200:
        data = response.data
        decoded = json.loads(data.decode(sys.stdout.encoding))
        return decoded
    print("Error for: " + repo_url)
    return -1   

def get_bitbucket_commits(repo_url):
    project_string = get_bitbucket_repo_substring(repo_url)
    response = form_request(
        "https://api.bitbucket.org/2.0/repositories/" + project_string + "/commits")
    if response.status == 200:
        data = response.data
        decoded = json.loads(data.decode(sys.stdout.encoding))
        return len(decoded["values"])
    print("Error for: " + repo_url)
    return -1

def get_gitlab_data(repo_url):
    project_string = get_gitlab_repo_substring(repo_url)
    response = form_request(
        "https://gitlab.com/api/v4/projects/" + project_string)
    if response.status == 200:
        data = response.data
        decoded = json.loads(data.decode(sys.stdout.encoding))
        return decoded
    print("Error for: " + repo_url)
    return -1   

def get_github_data(repo_url):
    time.sleep(3600/5000)
    project_string = get_github_repo_substring(repo_url)
    http = urllib3.PoolManager(ca_certs=certifi.where())
    response = http.request('GET',
                            "https://api.github.com/repos/" + project_string,
                            headers=urllib3.util.make_headers(basic_auth=c.github_username + ":" + c.github_key,
                                                              user_agent=c.github_username))
    if response.status == 200:
        data = response.data
        decoded = json.loads(data.decode(sys.stdout.encoding))
        return decoded
    print("Error for: " + repo_url)
    return -1 

def get_all_bitbucket_repos_data(data) -> list:
    result = list()
    counter = 1
    for p in data:
        url = p['url']
        if(url.startswith("https://bitbucket.org")):
            print("Fetching data for Bitbucket project: " + str(counter))
            analysis_result = get_bitbucket_data(url)
            if(analysis_result != -1):
                result.append(analysis_result)
            counter += 1
    return result

def get_all_gitlab_repos_data(data) -> list:
    result = list()
    counter = 1
    for p in data:
        url = p['url']
        if(url.startswith("https://gitlab.com")):
            print("Fetching data for GitLab project: " + str(counter))
            analysis_result = get_gitlab_data(url)
            if(analysis_result != -1):
                result.append(analysis_result)
            counter += 1
    return result

def get_all_github_repos_data(data) -> list:
    result = list()
    counter = 1
    for p in data:
        url = p['url']
        if(url.startswith("https://github.com")):
            print("Fetching data for GitHub project: " + str(counter))
            analysis_result = get_github_data(url)
            if(analysis_result != -1):
                result.append(analysis_result)
            counter += 1
    return result

def get_ghtorrent_github_repos_data(data) -> list:
    result = list()
    counter = 1
    for p in data:
        url = p['url']
        url = url.replace("https://api.github.com/repos/", "https://github.com/")
        print("Fetching data for GitHub project: " + str(counter))
        analysis_result = get_github_data(url)
        if(analysis_result != -1):
            result.append(analysis_result)
        counter += 1
    return result

def get_repo_by_url(repo_url):
    for p in data:
        if(p['url'] == repo_url):
            return p
    return -1

def get_rosmap_project(repo, rosmap_data):
    for p in rosmap_data:
        if(repo in p['url']):
            return p
    return None

def start_bitbucket_analysis(repos, rosmap_data):
    filtered_repos = list()
    print("0 - BitBucket Initial search: " + str(len(repos)))
    # Filter fork repositories
    for p in repos:
        if(not ('parent' in p)):
            filtered_repos.append(p)
    print("1 - BitBucket Filter fork repositories: " + str(len(filtered_repos)))
    c.save('./repos_mining_data/intermediateResults/1_bitbucket_forks.json', filtered_repos)
    repos = filtered_repos
    filtered_repos = list()
    # Filter repositories with #commits < NUM_COMMITS
    if(not os.path.isfile('./repos_mining_data/intermediateResults/2_bitbucket_commits.json')):
        for p in repos:
            if(get_bitbucket_commits(p['links']['clone'][0]['href']) >= c.NUM_COMMITS):
                filtered_repos.append(p)
        c.save('./repos_mining_data/intermediateResults/2_bitbucket_commits.json', filtered_repos)
        repos = filtered_repos
        print("2 - BitBucket Filter repositories with at least " + str(c.NUM_COMMITS) + " commits: " + str(len(repos)))
    else:
        repos = json.load(open('./repos_mining_data/intermediateResults/2_bitbucket_commits.json', 'r'))
        print("2 - BitBucket Filter repositories with at least " + str(c.NUM_COMMITS) + " commits: " + str(len(repos)))
    filtered_repos = list()
    # Filter repositories with at least X stars
    for p in repos:
        stars = get_rosmap_project(p['links']['html']['href'], rosmap_data)['stars']
        if(stars >= NUM_STARS):
            filtered_repos.append(p)
    print("3 - BitBucket Filter repositories with at least X stars: " + str(len(filtered_repos)))
    c.save('./repos_mining_data/intermediateResults/3_bitbucket_stars.json', filtered_repos)
    repos = filtered_repos
    filtered_repos = list()
    # Filter demo repositories
    for p in repos:
        if(p['description'] is not None):
            if(not (("demo" in p['description'].lower()) or ("course" in p['description'].lower()) or ("thesis" in p['description'].lower()) or ("exame" in p['description'].lower()))): # “demo”, “course”, "thesis", exame
                if(not (("demo" in p['full_name'].lower()) or ("course" in p['full_name'].lower()) or ("thesis" in p['full_name'].lower()) or ("exame" in p['full_name'].lower()))): # “demo”, “course”, "thesis", exame
                    filtered_repos.append(p)
        else:
            filtered_repos.append(p)
    print("4 - Bitbucket Filter DEMO repositories: " + str(len(filtered_repos)))
    c.save('./repos_mining_data/intermediateResults/4_bitbucket_no_demo.json', filtered_repos)
    repos = filtered_repos
    filtered_repos = list()
    # Filter tools repositories
    for p in repos:
        if(p['description'] is not None):
            if(not (("tool" in p['description'].lower()) or ("util" in p['description'].lower()) or ("helper" in p['description'].lower()) or ("library" in p['description'].lower()) or ("util" in p['description'].lower()) or ("plugin" in p['description'].lower()) or ("plug-in" in p['description'].lower()))): # tool, util, helper, library, plugin, plug-in
                if(not (("tool" in p['full_name'].lower()) or ("util" in p['full_name'].lower()) or ("helper" in p['full_name'].lower()) or ("library" in p['full_name'].lower()) or ("plugin" in p['full_name'].lower()) or ("plug-in" in p['full_name'].lower()))): # tool, util, helper, library, plugin, plug-in
                    filtered_repos.append(p)
        else:
            filtered_repos.append(p)
    print("5 - Bitbucket Filter TOOLS repositories: " + str(len(filtered_repos)))
    c.save('./repos_mining_data/intermediateResults/5_bitbucket_no_tools.json', filtered_repos)
    repos = filtered_repos
    filtered_repos = list()
    # Filter simulation-oriented repositories
    for p in repos:
        if(p['description'] is not None):
            if(not (("simulat" in p['description'].lower()) or ("gazebo" in p['description'].lower()))): # simulat, gazebo
                if(not (("simulat" in p['full_name'].lower()) or ("gazebo" in p['full_name'].lower()))): # simulat, gazebo
                    filtered_repos.append(p)
        else:
            filtered_repos.append(p)
    print("6 - Bitbucket Filter SIMULATION repositories: " + str(len(filtered_repos)))
    c.save('./repos_mining_data/intermediateResults/6_bitbucket_no_simul.json', filtered_repos)
    repos = filtered_repos
    filtered_repos = list()
    repos = filtered_repos
    filtered_repos = list()
    print("Bitbucket analysis done.")

def start_gitlab_analysis(repos):
    filtered_repos = list()
    print("0 - GitLab Initial search: " + str(len(repos)))
    # Filter fork repositories
    for p in repos:
        if((not ('fork' in p['name_with_namespace'])) and not(('fork' in p['description']))):
            filtered_repos.append(p)
    print("1 - GitLab Filter fork repositories: " + str(len(filtered_repos)))
    c.save('./repos_mining_data/intermediateResults/1_gitlab_forks.json', filtered_repos)
    repos = filtered_repos
    filtered_repos = list()
    # Filter repositories with #commits < NUM_COMMITS
    if(not os.path.isfile('./repos_mining_data/intermediateResults/3_bitbucket_commits.json')):
        for p in repos:
            response = form_request(p['web_url'])
            try:
                if response.status == 200:
                    data = response.data
                    commits = int(re.findall(r"[\d]+</strong> Commits</a>", str(data))[0].split("<")[0])
                else:
                    print("error: " + p['web_url'])
            except:
                commits = 0
            if(commits >= c.NUM_COMMITS):
                filtered_repos.append(p)
        c.save('./repos_mining_data/intermediateResults/2_gitlab_commits.json', filtered_repos)
        repos = filtered_repos
        print("2 - GitLab Filter repositories with at least " + str(c.NUM_COMMITS) + " commits: " + str(len(filtered_repos)))
    else:
        repos = json.load(open('./repos_mining_data/intermediateResults/2_gitlab_commits.json', 'r')) # filtered_repos
        print("2 - GitLab Filter repositories with at least " + str(c.NUM_COMMITS) + " commits: " + str(len(repos)))
    filtered_repos = list()
    # Filter repositories with at least X stars
    for p in repos:
        if(p['star_count'] >= NUM_STARS):
            filtered_repos.append(p)
    print("3 - GitLab Filter repositories with at least X stars: " + str(len(filtered_repos)))
    c.save('./repos_mining_data/intermediateResults/3_gitlab_stars.json', filtered_repos)
    repos = filtered_repos
    filtered_repos = list()
    # Filter demo repositories
    for p in repos:
        if(p['description'] is not None):
            if(not (("demo" in p['description'].lower()) or ("course" in p['description'].lower()) or ("thesis" in p['description'].lower()) or ("exame" in p['description'].lower()))): # “demo”, “course”, "thesis"
                if(not (("demo" in p['path_with_namespace'].lower()) or ("course" in p['path_with_namespace'].lower()) or ("thesis" in p['path_with_namespace'].lower()) or ("exame" in p['path_with_namespace'].lower()))): # “demo”, “course”, "thesis", "exame"
                    filtered_repos.append(p)
        else:
            filtered_repos.append(p)
    print("4 - Gitlab Filter DEMO repositories: " + str(len(filtered_repos)))
    c.save('./repos_mining_data/intermediateResults/4_gitlab_no_demo.json', filtered_repos)
    repos = filtered_repos
    filtered_repos = list()
    # Filter tools repositories
    for p in repos:
        if(p['description'] is not None):
            if(not (("tool" in p['description'].lower()) or ("util" in p['description'].lower()) or ("helper" in p['description'].lower()) or ("library" in p['description'].lower()) or ("util" in p['description'].lower()) or ("plugin" in p['description'].lower()) or ("plug-in" in p['description'].lower()))): # tool, util, helper, library, plugin, plug-in
                if(not (("tool" in p['path_with_namespace'].lower()) or ("util" in p['path_with_namespace'].lower()) or ("helper" in p['path_with_namespace'].lower()) or ("library" in p['path_with_namespace'].lower()) or ("plugin" in p['path_with_namespace'].lower()) or ("plug-in" in p['path_with_namespace'].lower()))): # tool, util, helper, library, plugin, plug-in
                    filtered_repos.append(p)
        else:
            filtered_repos.append(p)    
    print("5 - Gitlab Filter TOOLS repositories: " + str(len(filtered_repos)))
    c.save('./repos_mining_data/intermediateResults/5_gitlab_no_tools.json', filtered_repos)
    repos = filtered_repos
    filtered_repos = list()
    # Filter simulation-oriented repositories
    for p in repos:
        if(p['description'] is not None):
            if(not (("simulat" in p['description'].lower()) or ("gazebo" in p['description'].lower()))): # simulat, gazebo
                if(not (("simulat" in p['path_with_namespace'].lower()) or ("gazebo" in p['path_with_namespace'].lower()))): # simulat, gazebo
                    filtered_repos.append(p)
        else:
            filtered_repos.append(p)
    print("6 - Gitlab Filter SIMULATION repositories: " + str(len(filtered_repos)))
    c.save('./repos_mining_data/intermediateResults/6_gitlab_no_simul.json', filtered_repos)
    repos = filtered_repos
    filtered_repos = list()
    repos = filtered_repos
    filtered_repos = list()
    print("GitLab analysis done.")

def get_last_github_commits_api(repos):
    result = list()
    counter = 1
    for p in repos:
        url = p['url']
        url = url.replace("https://api.github.com/repos/", "https://github.com/") + "/commits"
        print("Fetching commits for GitHub project: " + str(counter) + " === " + url)
        analysis_result = get_github_data(url)
        if(analysis_result != -1):
            result.append(analysis_result)
        counter += 1
    return result

def count_commits(repo, commits):
    repo_url = "https://www.github.com/" + get_github_repo_substring(repo['url'])
    http = urllib3.PoolManager(ca_certs=certifi.where())
    response = http.request('GET', repo_url, headers=urllib3.util.make_headers(basic_auth=c.github_username + ":" + c.github_username, user_agent=c.github_username))
    if response.status == 200:
            data = str(response.data)
            metrics = re.findall(r'<span class="num text-emphasized">\\n[ ]+[\d|,]+', str(data))
            num_commits = int(re.findall(r'[\d]+$', metrics[0].replace(",", ""))[0])
            print(repo_url + " -- " + str(num_commits))
            return num_commits
    else:
            print("error: " + repo_url)
            return -1

def to_dictionary(repos):
    result = {}
    for p in repos:
        result[p['full_name']] = p
    return result

def to_dictionary_commits(commits):
    result = {}
    for p in commits:
        try:
            result[commit_to_repo_name(p[0]['commit']['url'])] = p
        except:
            None
    return result

def union_dictionaries(dict1, dict2):
    return dict(list(dict1.items()) + list(dict2.items()))

def is_commit_from_repo(commit, repo_url):
    return commit['commit']['url'].startswith(repo_url)

def get_last_commit(repo, commits):
    try:
        result = commits[repo['full_name']][0]
        return result
    except:
        "Error for: " + repo['full_name']
    return None

def has_readme_file(repo):
    response = form_request(repo['html_url'])
    if response.status == 200:
        data = str(response.data)
        return "readme" in data.lower()
    return False

def start_github_analysis(rosmap_repos, rosmap_commits, ghtorrent_repos, ghtorrent_commits, jump_commits):
    filtered_repos = list()
    print("0 - GitHub ROSMAP Initial search: " + str(len(rosmap_repos)))
    # Filter ROSMAP fork repositories
    for key, p in rosmap_repos.items():
        if(p['fork'] == False):
            filtered_repos.append(p)
    print("1 - GitHub ROSMAP Fork repositories: " + str(len(filtered_repos)))
    c.save('./repos_mining_data/intermediateResults/1_github_rosmap_no_forks.json', filtered_repos)
    repos = filtered_repos
    filtered_repos = list()
    # Filter ROSMAP repositories with #commits < NUM_COMMITS
    # the check below is used just for saving time in case the number of commits has been already fetched from the web
    # i.e., the 2_github_rosmap_commits.json already exists and it is up to date
    if(not jump_commits):
        for p in repos:
            if(count_commits(p, rosmap_commits) >= c.NUM_COMMITS):
                filtered_repos.append(p)
        print("2 - Github ROSMAP Filter repositories with at least " + str(c.NUM_COMMITS) + " commits: " + str(len(filtered_repos)))
        c.save('./repos_mining_data/intermediateResults/2_github_rosmap_commits.json', filtered_repos)
    else:
        with open('./repos_mining_data/intermediateResults/2_github_rosmap_commits.json', 'r') as outputfile:  
            filtered_repos = json.load(outputfile)
    repos = filtered_repos
    filtered_repos = list()
    # MERGE rosmap and ghtorrent repos
    repos = union_dictionaries(to_dictionary(repos), ghtorrent_repos)
    repos = repos.values()
    commits = union_dictionaries(to_dictionary_commits(rosmap_commits), to_dictionary_commits(ghtorrent_commits))
    commits = commits.values()
    print("MERGE - Merged lists of GitHub repos coming from the rosmap and the ghtorrent searches: " + str(len(repos)))
    # Filter repositories with at least X stars
    for p in repos:
        if(p['stargazers_count'] >= NUM_STARS):
            filtered_repos.append(p)
    print("3 - GitHub Filter repositories with at least X stars: " + str(len(filtered_repos)))
    c.save('./repos_mining_data/intermediateResults/3_github_stars.json', filtered_repos)
    repos = filtered_repos
    filtered_repos = list()
    # Filter demo repositories
    discarded = list()
    for p in repos:
        if(p['description'] is not None):
            if(not (("demo" in p['description'].lower()) or ("tutorial" in p['description'].lower()) or ("course" in p['description'].lower()) or ("thesis" in p['description'].lower()) or ("exame" in p['description'].lower()))): # “demo”, "tutorial", “course”, "thesis", exame
                if(not (("demo" in p['full_name'].lower()) or ("tutorial" in p['description'].lower()) or ("course" in p['full_name'].lower()) or ("thesis" in p['full_name'].lower()) or ("exame" in p['full_name'].lower()))): # “demo”, "tutorial", “course”, "thesis", exame
                    filtered_repos.append(p)
                else:
                    discarded.append(p)
            else:
                discarded.append(p)
        else:
            filtered_repos.append(p)
    print("4 - Github Filter DEMO repositories: " + str(len(filtered_repos)))
    c.save('./repos_mining_data/intermediateResults/4_github_no_demo.json', filtered_repos)
    c.save('./repos_mining_data/intermediateResults/4_github_no_demo_discarded.json', discarded)
    repos = filtered_repos
    filtered_repos = list()
    discarded = list()
    # Filter tools repositories
    for p in repos:
        if(p['description'] is not None):
            if(not (("tool" in p['description'].lower()) or ("util" in p['description'].lower()) or ("helper" in p['description'].lower()) or ("library" in p['description'].lower()) or ("util" in p['description'].lower()) or ("plugin" in p['description'].lower()) or ("plug-in" in p['description'].lower()))): # tool, util, helper, library, plugin, plug-in
                if(not (("tool" in p['full_name'].lower()) or ("util" in p['full_name'].lower()) or ("helper" in p['full_name'].lower()) or ("library" in p['full_name'].lower()) or ("plugin" in p['full_name'].lower()) or ("plug-in" in p['full_name'].lower()))): # tool, util, helper, library, plugin, plug-in
                    filtered_repos.append(p)
                else:
                    discarded.append(p)
            else:
                discarded.append(p)
        else:
            filtered_repos.append(p)
    print("5 - GitHub Filter TOOLS repositories: " + str(len(filtered_repos)))
    c.save('./repos_mining_data/intermediateResults/5_github_no_tools.json', filtered_repos)
    c.save('./repos_mining_data/intermediateResults/5_github_no_tools_discarded.json', discarded)
    discarded = list()
    repos = filtered_repos
    filtered_repos = list()
    # Filter simulation-oriented repositories
    for p in repos:
        if(p['description'] is not None):
            if(not (("simulat" in p['description'].lower()) or ("gazebo" in p['description'].lower()))): # simulat, gazebo
                if(not (("simulat" in p['full_name'].lower()) or ("gazebo" in p['full_name'].lower()))): # simulat, gazebo
                    filtered_repos.append(p)
                else:
                    discarded.append(p)
            else:
                discarded.append(p)
        else:
            filtered_repos.append(p)
    print("6 - GitHub Filter SIMULATION repositories: " + str(len(filtered_repos)))
    c.save('./repos_mining_data/intermediateResults/6_github_no_simul.json', filtered_repos)
    c.save('./repos_mining_data/intermediateResults/6_github_no_simul_discarded.json', discarded)
    discarded = list()
    repos = filtered_repos
    filtered_repos = list()
    print("GitHub analysis done.")

def get_repos_list_to_clone(file_path):
    gitlab_no_simul = json.load(open('./repos_mining_data/intermediateResults/6_gitlab_no_simul.json', 'r'))
    bitbucket_no_simul = json.load(open('./repos_mining_data/intermediateResults/6_bitbucket_no_simul.json', 'r'))
    github_no_simul = json.load(open('./repos_mining_data/intermediateResults/6_github_no_simul.json', 'r'))

    repos = list()
    for p in github_no_simul:
        repos.append({'id': p['full_name'], 'description': p['description'], 'web_url': p['html_url'], 'clone_url': p['clone_url'], 'default_branch': p['default_branch'], 'source': 'github'})
    for p in gitlab_no_simul:
        repos.append({'id': p['path_with_namespace'], 'description': p['description'], 'web_url': p['web_url'], 'clone_url': p['http_url_to_repo'], 'default_branch': p['default_branch'], 'source': 'gitlab'})
    for p in bitbucket_no_simul:
        repos.append({'id': p['full_name'], 'description': p['description'], 'web_url': p['links']['html']['href'], 'clone_url': p['links']['clone'][0]['href'], 'default_branch': p['mainbranch']['name'], 'source': 'bitbucket'})

    c.save(file_path, repos)

def start_analysis():    
    with open('./otherData/rosmap_output.json', 'r') as outputfile:  
        # we load the data
        data = json.load(outputfile)

        # in bitbucket_repos we will have the JSON representation of all the data we mined from the search API of bitbucket.org
        if(not os.path.isfile('./repos_mining_data/intermediateResults/0_all_bitbucket.json')):
            bitbucket_repos = get_all_bitbucket_repos_data(data)
            c.save('./repos_mining_data/intermediateResults/0_all_bitbucket.json', gitlab_repos)
        else:
            bitbucket_repos = json.load(open('./repos_mining_data/intermediateResults/0_all_bitbucket.json', 'r'))
        
        # in gitlab_repos we will have the JSON representation of all the data we mined from the search API of gitlab.com 
        # Notice that out of the 46 initial gitlab repos, 16 of them are not hosted on gitlab.com, we did a manual analysis of those repos, which lead to no included results
        if(not os.path.isfile('./repos_mining_data/intermediateResults/0_all_gitlab.json')):
            gitlab_repos = get_all_gitlab_repos_data(data)
            c.save('./repos_mining_data/intermediateResults/0_all_gitlab.json', gitlab_repos)
        else:
            gitlab_repos = json.load(open('./repos_mining_data/intermediateResults/0_all_gitlab.json', 'r'))

        # in github_rosmap_repos we will have the JSON representation of all the data we mined from the search of ROSMAP
        if(not os.path.isfile('./repos_mining_data/intermediateResults/0_rosmap_github.json')):
            github_rosmap_repos = get_all_github_repos_data(data)
            c.save('./repos_mining_data/intermediateResults/0_rosmap_github.json', github_rosmap_repos)

            # here we transform into a dictionary for eliminating duplicates and for easing the rest of the filtering
            commits_rosmap = to_dictionary(get_last_github_commits_api(github_rosmap_repos))
            c.save('./repos_mining_data/intermediateResults/0_rosmap_github_commits.json', commits_rosmap)
        else:
            # here we transform into a dictionary for eliminating duplicates and for easing the rest of the filtering
            github_rosmap_repos = to_dictionary(json.load(open('./repos_mining_data/intermediateResults/0_rosmap_github.json', 'r')))
            commits_rosmap = json.load(open('./repos_mining_data/intermediateResults/0_rosmap_github_commits.json', 'r'))
        
        # in github_gh_repos we will have the JSON representation of all the data we mined from the search API of the GitHub platform 
        # The initial point here is the data coming from the GHTorrent query as of this filtering step: "Filter repositories with #commits < 100"
        if(not os.path.isfile('./repos_mining_data/intermediateResults/2_ghtorrent_github.json')):
            # we load the data from the output of the GHTorrent query
            with open("./ghtorrentIntermediateResults/2_github_num_commits.txt", 'r') as gh:
                gh_reader = csv.DictReader(gh, delimiter='\t')
                data_ghtorrent = list()
                for line in gh_reader:
                    try:
                        data_ghtorrent.append(line)
                    except (AttributeError, TypeError, IndexError):
                        print("Error for: " + str(line))
            github_ghtorrent_repos = get_ghtorrent_github_repos_data(data_ghtorrent)
            c.save('./repos_mining_data/intermediateResults/2_ghtorrent_github.json', github_ghtorrent_repos)

            # here we transform into a dictionary for eliminating duplicates and for easing the rest of the filtering
            commits_ghtorrent = to_dictionary(get_last_github_commits_api(github_ghtorrent_repos))
            c.save('./repos_mining_data/intermediateResults/2_ghtorrent_github_commits.json', commits_ghtorrent)
        else:
            # here we transform into a dictionary for eliminating duplicates and for easing the rest of the filtering
            github_ghtorrent_repos = to_dictionary(json.load(open('./repos_mining_data/intermediateResults/2_ghtorrent_github.json', 'r')))
            commits_ghtorrent = json.load(open('./repos_mining_data/intermediateResults/2_ghtorrent_github_commits.json', 'r'))
        
        start_bitbucket_analysis(bitbucket_repos, data)
        start_gitlab_analysis(gitlab_repos)
        start_github_analysis(github_rosmap_repos, commits_rosmap, github_ghtorrent_repos, commits_ghtorrent, True)

def print_name_description(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
        for p in data:
            print(p['full_name'] + " --- " + p['description'])

def is_github_fork(repo):
    response = form_request(repo['web_url'])
    if response.status == 200:
        data = str(response.data)
        return "forked from" in data.lower()
    return False

def count_filtering_steps():
    all_bitbucket = json.load(open('./repos_mining_data/intermediateResults/0_all_bitbucket.json', 'r'))
    print("0_all_bitbucket: " + str(len(all_bitbucket)))
    all_gitlab = json.load(open('./repos_mining_data/intermediateResults/0_all_gitlab.json', 'r'))
    print("0_all_gitlab: " + str(len(all_gitlab)))
    rosmap_github = to_dictionary(json.load(open('./repos_mining_data/intermediateResults/0_rosmap_github.json', 'r')))
    print("0_rosmap_github: " + str(len(rosmap_github)))
    rosmap_github_commits = json.load(open('./repos_mining_data/intermediateResults/0_rosmap_github_commits.json', 'r'))
    print("0_rosmap_github_commits: " + str(len(rosmap_github_commits)))
    bitbucket_forks = json.load(open('./repos_mining_data/intermediateResults/1_bitbucket_forks.json', 'r'))
    print("1_bitbucket_forks: " + str(len(bitbucket_forks)))
    github_rosmap_no_forks = json.load(open('./repos_mining_data/intermediateResults/1_github_rosmap_no_forks.json', 'r'))
    print("1_github_rosmap_no_forks: " + str(len(github_rosmap_no_forks)))
    gitlab_forks = json.load(open('./repos_mining_data/intermediateResults/1_gitlab_forks.json', 'r'))
    print("1_gitlab_forks: " + str(len(gitlab_forks)))
    bitbucket_commits = json.load(open('./repos_mining_data/intermediateResults/2_bitbucket_commits.json', 'r'))
    print("2_bitbucket_commits: " + str(len(bitbucket_commits)))
    ghtorrent_github = to_dictionary(json.load(open('./repos_mining_data/intermediateResults/2_ghtorrent_github.json', 'r')))
    print("2_ghtorrent_github: " + str(len(ghtorrent_github)))
    ghtorrent_github_commits = json.load(open('./repos_mining_data/intermediateResults/2_ghtorrent_github_commits.json', 'r'))
    print("2_ghtorrent_github_commits: " + str(len(ghtorrent_github_commits)))
    github_rosmap_commits = json.load(open('./repos_mining_data/intermediateResults/2_github_rosmap_commits.json', 'r'))
    print("2_github_rosmap_commits: " + str(len(github_rosmap_commits)))
    gitlab_commits = json.load(open('./repos_mining_data/intermediateResults/2_gitlab_commits.json', 'r'))
    print("2_gitlab_commits: " + str(len(gitlab_commits)))
    bitbucket_no_description = json.load(open('./repos_mining_data/intermediateResults/3_bitbucket_stars.json', 'r'))
    print("3_bitbucket_stars: " + str(len(bitbucket_no_description)))
    github_no_description = json.load(open('./repos_mining_data/intermediateResults/3_github_stars.json', 'r'))
    print("3_github_stars: " + str(len(github_no_description)))
    gitlab_no_description = json.load(open('./repos_mining_data/intermediateResults/3_gitlab_stars.json', 'r'))
    print("3_gitlab_stars: " + str(len(gitlab_no_description)))
    bitbucket_no_demo = json.load(open('./repos_mining_data/intermediateResults/4_bitbucket_no_demo.json', 'r'))
    print("4_bitbucket_no_demo: " + str(len(bitbucket_no_demo)))
    github_no_demo = json.load(open('./repos_mining_data/intermediateResults/4_github_no_demo.json', 'r'))
    print("4_github_no_demo: " + str(len(github_no_demo)))
    github_no_demo_discarded = json.load(open('./repos_mining_data/intermediateResults/4_github_no_demo_discarded.json', 'r'))
    print("4_github_no_demo_discarded: " + str(len(github_no_demo_discarded)))
    gitlab_no_demo = json.load(open('./repos_mining_data/intermediateResults/4_gitlab_no_demo.json', 'r'))
    print("4_gitlab_no_demo: " + str(len(gitlab_no_demo)))
    bitbucket_no_tools = json.load(open('./repos_mining_data/intermediateResults/5_bitbucket_no_tools.json', 'r'))
    print("5_bitbucket_no_tools: " + str(len(bitbucket_no_tools)))
    github_no_tools = json.load(open('./repos_mining_data/intermediateResults/5_github_no_tools.json', 'r'))
    print("5_github_no_tools: " + str(len(github_no_tools)))
    github_no_tools_discarded = json.load(open('./repos_mining_data/intermediateResults/5_github_no_tools_discarded.json', 'r'))
    print("5_github_no_tools_discarded: " + str(len(github_no_tools_discarded)))
    gitlab_no_tools = json.load(open('./repos_mining_data/intermediateResults/5_gitlab_no_tools.json', 'r'))
    print("5_gitlab_no_tools: " + str(len(gitlab_no_tools)))
    bitbucket_no_simul = json.load(open('./repos_mining_data/intermediateResults/6_bitbucket_no_simul.json', 'r'))
    print("6_bitbucket_no_simul: " + str(len(bitbucket_no_simul)))
    github_no_simul = json.load(open('./repos_mining_data/intermediateResults/6_github_no_simul.json', 'r'))
    print("6_github_no_simul: " + str(len(github_no_simul)))
    github_no_simul_discarded = json.load(open('./repos_mining_data/intermediateResults/6_github_no_simul_discarded.json', 'r'))
    print("6_github_no_simul_discarded: " + str(len(github_no_simul_discarded)))
    gitlab_no_simul = json.load(open('./repos_mining_data/intermediateResults/6_gitlab_no_simul.json', 'r'))
    print("7_gitlab_no_simul: " + str(len(gitlab_no_simul)))

start_analysis()
count_filtering_steps()

# print_name_description("./repos_mining_data/intermediateResults/4_github_no_demo_discarded.json")
# print_name_description("./repos_mining_data/intermediateResults/5_github_no_tools_discarded.json")
# print_name_description("./repos_mining_data/intermediateResults/6_github_no_simul_discarded.json")

get_repos_list_to_clone("./repos_mining_data/otherData/repos_to_clone.json")


