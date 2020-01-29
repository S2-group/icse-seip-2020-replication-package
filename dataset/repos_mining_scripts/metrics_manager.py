import json
import sys
import os
from bs4 import BeautifulSoup
import ast
import csv 
import re
import urllib3
import certifi
import time
import subprocess
import configuration as c

filtered_heuristic = './repos_mining_data/otherData/repos_filtered_launch_file.json'
metrics_exported_gdrive = './repos_mining_data/otherData/exported_gdrive_metrics.csv'
repos_filtered_heuristic_metrics = './repos_mining_data/otherData/repos_filtered_launch_file_metrics.json'

def count_metrics(repo):
        try:
                http = urllib3.PoolManager(ca_certs=certifi.where())
                response = http.request('GET', repo['web_url'])
                if response.status == 200:
                        data = response.data
                        # <span itemprop="name">Issues</span>
                        # <span class="Counter">1</span>
                        try:
                                issues = int(re.findall(r'<span itemprop="name">Issues</span>\\n[ ]+<span class="Counter">[\d]+</span>', str(data))[0].split('Counter">')[1].replace("</span>", ""))
                        except:
                                issues = 'NA'
                        # <span itemprop="name">Pull requests</span>
                        # <span class="Counter">0</span>
                        try:
                                pull_requests = int(re.findall(r'<span itemprop="name">Pull requests</span>\\n[ ]+<span class="Counter">[\d]+</span>', str(data))[0].split('Counter">')[1].replace("</span>", ""))
                        except:
                                pull_requests = 'NA'
                        other_metrics = re.findall(r'<span class="num text-emphasized">\\n[ ]+[\d|,]+', str(data))
                        try:
                                # commits = int(re.findall(r'[\d]+$', other_metrics[0].replace(",", ""))[0])
                                commits = get_commits_locally(repo['local_clone_path'])
                        except:
                                commits = 'NA'
                        try:
                                # branches = int(re.findall(r'[\d]+$', other_metrics[1].replace(",", ""))[0])
                                branches = get_branches_locally(repo['local_clone_path'])
                        except:
                                branches = 'NA'
                        try:
                                releases = int(re.findall(r'[\d]+$', other_metrics[2].replace(",", ""))[0])
                        except:
                                releases = 'NA'
                        try:
                                # contributors = int(re.findall(r'[\d]+$', other_metrics[3].replace(",", ""))[0])
                                contributors = get_contributors_locally(repo['local_clone_path'])
                        except:
                                contributors = 'NA'
                        print([issues, pull_requests, commits, branches, releases, contributors])
                        return [issues, pull_requests, commits, branches, releases, contributors]
                else:
                        print("Error: " + repo['web_url'])
                        return ['NA', 'NA', 'NA', 'NA', 'NA', 'NA']
        except:
                print("Generic exception for: " + repo['web_url'])
                return ['NA', 'NA', 'NA', 'NA', 'NA', 'NA']

def get_issues_github(repo):
        try:
                http = urllib3.PoolManager(ca_certs=certifi.where())
                url = repo['web_url'] + "/issues?is%3Aissue"
                response = http.request('GET', url, headers=urllib3.util.make_headers(basic_auth=c.github_username + ":" + c.github_key, user_agent=c.github_username))
                if response.status == 200:
                        data = str(response.data).replace(" ", "")
                        try:
                                open_issues = int(re.findall(r'svg>\\n[\d|,]+Open\\n</a>', data)[0].replace("svg>\\n", "").replace("Open\\n</a>", ""))
                        except:
                                open_issues = 'NA'
                        try:
                                closed_issues = int(re.findall(r'svg>\\n[\d|,]+Closed\\n</a>', data)[0].replace("svg>\\n", "").replace("Closed\\n</a>", ""))
                        except:
                                closed_issues = 'NA'
                        if(open_issues == 'NA' or closed_issues == 'NA'):
                                num_issues = "NA"
                        else:
                                num_issues = open_issues + closed_issues
                        return [num_issues, open_issues, closed_issues]
                else:
                        print("error: " + repo['web_url'])
                        return ['NA', 'NA', 'NA']
        except:
                return ['NA', 'NA', 'NA']

def collect_metrics_counts():
    with open(filtered_heuristic, 'r') as f:  
        repos_list = json.load(f)
        counter = 1
        enriched_result = list()
        for p in repos_list:
            print("Collecting metrics for repo number " + str(counter) + " --- " + p['id'])
            counter += 1
            metrics = count_metrics(p)
            p['num_issues'] = metrics[0]
            p['num_pull_requests'] = metrics[1]
            p['num_commits'] = metrics[2]
            p['num_branches'] = metrics[3]
            p['num_releases'] = metrics[4]
            p['num_contributors'] = metrics[5]
            # here we double check if there are repos with less than NUM_COMMITS commits
            if(p['num_commits'] != "NA"):
                if(int(p['num_commits']) >= c.NUM_COMMITS):
                        enriched_result.append(p)
                else:
                        print("Discarded this repo because it has less than NUM_COMMITS commits: " + p['id'])
            else:
                enriched_result.append(p)   
    c.save(repos_filtered_heuristic_metrics, enriched_result)

def prepare_export_gdrive():
        csv.register_dialect('tab_separated_csv', delimiter = '\t', quoting=csv.QUOTE_ALL, skipinitialspace=True)
        exported_contents = list()
        with open(repos_filtered_heuristic_metrics, 'r') as f:
              repos = json.load(f)
              for p in repos:
                      exported_contents.append([p['id'], p['description'], p['web_url'], p['source'], p['default_branch'], len(p['xml_launch_files']), len(p['py_launch_files']), p['num_issues'], p['num_pull_requests'], p['num_commits'], p['num_branches'], p['num_releases'], p['num_contributors']])
        with open(metrics_exported_gdrive, 'w+') as f:
                writer = csv.writer(f, dialect='tab_separated_csv')
                for row in exported_contents:
                        writer.writerow(row)

def visit_all_github_pages():
        with open(filtered_heuristic, 'r') as f:  
                repos_list = json.load(f)
                counter = 1
                for p in repos_list:
                        print("Visiting web page for repo number " + str(counter) + " --- " + p['id'])
                        os.system("osascript ./visit_website.scpt " + p['web_url'].replace('https://', ''))
                        time.sleep(3)
                        counter += 1

def get_contributors_locally(repo_path):
        contributors = int(subprocess.check_output("cd " + repo_path + ";git shortlog -s HEAD | wc -l", shell=True))
        return contributors

def get_commits_locally(repo_path):
        commits = int(subprocess.check_output("cd " + repo_path + ";git rev-list --count HEAD", shell=True))
        return commits

def get_branches_locally(repo_path):
        branches = int(subprocess.check_output("cd " + repo_path + ";git branch -r | wc -l", shell=True))
        return branches

def patch_contributors(save_to_external_file):
        with open(repos_filtered_heuristic_metrics, 'r') as f:
                repos = json.load(f)
                enriched_result = list()
                for p in repos:
                        p['num_contributors'] = get_contributors_locally(p['local_clone_path'])
                        enriched_result.append(p)
        if(save_to_external_file):
                c.save(repos_filtered_heuristic_metrics, enriched_result)
        else:
                csv.register_dialect('tab_separated_csv', delimiter = '\t', quoting=csv.QUOTE_ALL, skipinitialspace=True)
                to_save = list()
                for p in enriched_result:
                        to_save.append([p['id'], p['num_contributors']])
                with open("./repos_mining_data/otherData/locally_identified_contributors.csv", 'w') as f:
                        writer = csv.writer(f, dialect='tab_separated_csv')
                        for row in to_save:
                                writer.writerow(row)

def patch_issues(save_to_external_file):
        with open(repos_filtered_heuristic_metrics, 'r') as f:
                repos = json.load(f)
                enriched_result = list()
                counter = 1
                for p in repos:
                        print("Patching issues for repo number " + str(counter) + " --- " + p['id'])
                        counter += 1
                        if(p['source'] == "github"):
                                mined_issue_data = get_issues_github(p)
                                p['num_issues'] = mined_issue_data[0]
                                p['open_issues'] = mined_issue_data[1]
                                p['closed_issues'] = mined_issue_data[2]
                        else:
                                p['num_issues'] = "NA"
                                p['open_issues'] = "NA"
                                p['closed_issues'] = "NA"
                        enriched_result.append(p)
        if(save_to_external_file):
                c.save(repos_filtered_heuristic_metrics, enriched_result)
        else:
                csv.register_dialect('tab_separated_csv', delimiter = '\t', quoting=csv.QUOTE_ALL, skipinitialspace=True)
                to_save = list()
                for p in enriched_result:
                        to_save.append([p['id'], p['num_issues'], p['open_issues'], p['closed_issues']])
                with open("./repos_mining_data/otherData/issues_patch.csv", 'w') as f:
                        writer = csv.writer(f, dialect='tab_separated_csv')
                        for row in to_save:
                                writer.writerow(row)

def get_repo_data(repo_id, repos):
        for p in repos:
                if(p['full_name'] == repo_id):
                        return p['language']

def patch_languages(save_to_external_file):
        github_no_simul = json.load(open('./repos_mining_data/intermediateResults/6_github_no_simul.json', 'r'))
        bitbucket_no_simul = json.load(open('./repos_mining_data/intermediateResults/6_bitbucket_no_simul.json', 'r'))
        with open(repos_filtered_heuristic_metrics, 'r') as f:
                repos = json.load(f)
                enriched_result = list()
                counter = 1
                for p in repos:
                        print("Patching languages for repo number " + str(counter) + " --- " + p['id'])
                        counter += 1
                        if(p['source'] == "github"):
                                p['language'] = get_repo_data(p['id'], github_no_simul)
                        if(p['source'] == "bitbucket"):
                                p['language'] = get_repo_data(p['id'], bitbucket_no_simul)
                        if(p['source'] == "gitlab"):
                                p['language'] = "NA"
                        enriched_result.append(p)
        if(save_to_external_file):
                c.save('./repos_mining_data/otherData/repos_filtered_launch_file_metrics_languages.json', enriched_result)
        else:
                csv.register_dialect('tab_separated_csv', delimiter = '\t', quoting=csv.QUOTE_ALL, skipinitialspace=True)
                to_save = list()
                for p in enriched_result:
                        to_save.append([p['id'], p['language']])
                with open("./repos_mining_data/otherData/languages_patch.csv", 'w') as f:
                        writer = csv.writer(f, dialect='tab_separated_csv')
                        for row in to_save:
                                writer.writerow(row)
                
# visit_all_github_pages()
collect_metrics_counts()
prepare_export_gdrive()
# patch_contributors(False)
patch_issues(False)
patch_languages(False)