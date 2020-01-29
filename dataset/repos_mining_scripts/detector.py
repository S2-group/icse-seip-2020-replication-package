import json
import sys
import os
from bs4 import BeautifulSoup
import ast
import csv 
import re
import configuration as c

cloned_repos = './repos_mining_data/otherData/cloned_repos.json'
clones_path = '../Repos/'
detection_result_path = './repos_mining_data/otherData/repos_detected_files.json'
filtered_heuristic = './repos_mining_data/otherData/repos_filtered_launch_file.json'
exported_gdrive = './repos_mining_data/otherData/exported_gdrive.csv'

def is_xml(file_name):
        try:
                with open(file_name) as f:
                        content = f.read()
                        re.sub(r"\W", "", content)
                        return content.strip().startswith('<')
        except:
                return False        

def search_files(path, pattern) -> list:
        filellist = list()
        for root, dirs, files in os.walk(path):
                for name in files:
                        if((name.endswith(pattern))):
                                filellist.append(os.path.join(root, name))
        return filellist

def search_xml_files(path) -> list:
        filellist = list()
        for root, dirs, files in os.walk(path):
                for name in files:
                        if(is_xml(os.path.join(root, name))):
                                filellist.append(os.path.join(root, name))
        return filellist

def get_xml_launch_file_info(xml_file):
        try:
                with open(xml_file) as f:
                        content = f.read().encode('utf-8', 'ignore')
                        soup = BeautifulSoup(content, 'xml')
                        # The XML file is a ROS launch file if it contains one <launch> tag as root
                        if(not soup.find('launch')):
                                return -1
                        num_nodes = len(soup.find_all('node'))
                        num_includes = len(soup.find_all('include'))
                        return {'path': xml_file, 'num_nodes': num_nodes, 'num_includes': num_includes, 'type': 'xml'}
        except:
                print(xml_file)
                return -1

def get_py_launch_file_info(py_file):
        try: 
                with open(py_file) as f:
                        string_contents = f.read()
                        # the Python file is a ROS2 Launch file if it BOTH imports the "launch" package and refers to the "LaunchDescription" module
                        if((not ("from launch" in " ".join(string_contents.split()))) or (not ("import launch" in " ".join(string_contents.split()))) or (not ("LaunchDescription" in string_contents))):
                                return -1
                        num_nodes =  string_contents.count('actions.Node(')
                        num_includes = string_contents.count('include_launch_description')
                        return {'path': py_file, 'num_nodes': num_nodes, 'num_includes': num_includes, 'type': 'py'}
        except:
                return -1
        

def detect_xml_launch_files(repo):
        result = list()
        file_list = search_files(repo['local_clone_path'], '.xml')
        file_list= file_list + search_xml_files(repo['local_clone_path'])
        for xml_file in file_list:
                file_info = get_xml_launch_file_info(xml_file)
                if(file_info != -1):
                        result.append(file_info)
        return result

def detect_py_launch_files(repo):
        result = list()
        file_list = search_files(repo['local_clone_path'], '.py')
        for py_file in file_list:
                file_info = get_py_launch_file_info(py_file)
                if(file_info != -1):
                        result.append(file_info)
        return result

def start_detecting():
    with open(cloned_repos, 'r') as f:  
        repos_list = json.load(f)
        counter = 1
        detection_result = list()
        for p in repos_list:
            print("Detecting files for repo number " + str(counter) + " --- " + p['id'])
            counter += 1
            p['xml_launch_files'] = detect_xml_launch_files(p)
            p['py_launch_files'] = detect_py_launch_files(p)
            detection_result.append(p)      
    c.save(detection_result_path, detection_result)

def apply_filtering_heuristics():
        with open(detection_result_path, 'r') as f:
                repos = json.load(f)
                with_launch_file = 0
                final_filtered = 0
                collected_xml_launch_files = list()
                collected_py_launch_files = list()
                filtered_repos = list()
                for p in repos:
                        # Check 1: the repo must contain at least one Launch file
                        if((len(p['xml_launch_files']) > 0) or (len(p['py_launch_files']) > 0)):
                                with_launch_file += 1
                                total_nodes = 0
                                total_includes = 0
                                for el in p['xml_launch_files']:
                                        total_nodes += el['num_nodes']
                                        total_includes += el ['num_includes']
                                for el in p['py_launch_files']:
                                        total_nodes += el['num_nodes']
                                        total_includes += el ['num_includes']
                                collected_xml_launch_files.append(len(p['xml_launch_files']))
                                collected_py_launch_files.append(len(p['py_launch_files']))
                                if(total_nodes >= 2 or total_includes >= 1):
                                        final_filtered += 1
                                filtered_repos.append(p)
                c.save(filtered_heuristic, filtered_repos)
                print("Total number XML launch file: " + str(sum(collected_xml_launch_files)))
                print("Details: " + str(collected_xml_launch_files))
                print("Total number Python launch file: " + str(sum(collected_py_launch_files)))
                print("Details: " + str(collected_py_launch_files))
                print("Repos with either an XML or Python launch file: " + str(with_launch_file))
                print("Repos with either more than 2 nodes or 1 include statement: " + str(final_filtered))

def prepare_export_gdrive():
        csv.register_dialect('tab_separated_csv', delimiter = '\t', quoting=csv.QUOTE_ALL, skipinitialspace=True)
        exported_contents = list()
        with open(filtered_heuristic, 'r') as f:
              repos = json.load(f)
              for p in repos:
                      exported_contents.append([p['id'], p['description'], p['web_url'], p['default_branch'], len(p['xml_launch_files']), len(p['py_launch_files'])])
        with open(exported_gdrive, 'w+') as f:
                writer = csv.writer(f, dialect='tab_separated_csv')
                for row in exported_contents:
                        writer.writerow(row)
        
start_detecting()
apply_filtering_heuristics()
prepare_export_gdrive()
