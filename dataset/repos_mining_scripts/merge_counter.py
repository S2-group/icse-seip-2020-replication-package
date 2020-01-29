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
import pickle
import configuration as c

def get_rosmap_repo_substring(url):
    if(url.startswith("https://github.com")):
        project_string = url.split("https://github.com/")[1]
        project_string = project_string.split(".git")[0]
    if(url.startswith("https://api.github.com")):
        project_string = url.split("https://api.github.com/repos/")[1]
    return project_string

def get_github_repo_substring(url):
        project_string = url.split("https://api.github.com/repos/")[1]
        return project_string

def get_all_github_repos_data(data) -> list:
    result = list()
    for p in data:
        url = p['url']
        if(url.startswith("https://github.com") or url.startswith("https://api.github.com")):
                result.append(p)
    return result

def analyze_pair(rosmap_file_path, gh_file_path, merged_file_path):

    with open(rosmap_file_path, 'r') as rosmap:
        with open(gh_file_path, 'r') as gh:  
            # we load the data
            rosmap_data = get_all_github_repos_data(json.load(rosmap))
            gh_reader = csv.DictReader(gh, delimiter='\t')

            rosmap_urls = list()
            for p in rosmap_data:
                rosmap_urls.append(get_rosmap_repo_substring(p['url']))

            results = rosmap_urls
            
            for line in gh_reader:
                try:
                    current_url = get_github_repo_substring(line['url'])
                    if(not current_url in rosmap_urls):
                        results.append(current_url)
                except (AttributeError, TypeError, IndexError):
                    print("Error for: " + str(line))
            gh.close()
        rosmap.close()

    c.save(merged_file_path, results)
    print(rosmap_file_path + " + " + gh_file_path + " = " + str(len(results)) + ". Saved in: " + merged_file_path)

analyze_pair('./repos_mining_data/intermediateResults/0_rosmap_github.json', './repos_mining_data/ghtorrentIntermediateResults/0_initial_search.txt', './ghtorrentIntermediateResults/0_merged_github.txt')
analyze_pair('./repos_mining_data/intermediateResults/1_github_rosmap_no_forks.json', './repos_mining_data/ghtorrentIntermediateResults/1_github_no_forks.txt', './ghtorrentIntermediateResults/1_merged_github_no_forks.txt')
