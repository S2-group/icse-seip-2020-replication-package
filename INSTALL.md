### Introduction

In the following we describe (i) how to use the dataset containing real-world ROS-based robotic systems and (ii) the steps needed to replicate the whole study (i.e., rebuilding the dataset, rerunning the analysis, etc.)


### Using the dataset

At the core of our study lies a reusable dataset including 598 GitHub repositories containing ROS-based robotic systems. 
The whole dataset is available as a single CSV file called [repos_dataset_all.csv](https://github.com/S2-group/icse-seip-2020-replication-package/dataset/repos_dataset_all.csv) and it has the following fields:
- **ID**: the unique ID of the repository
- **Source**: whether the repository comes from one of this platforms**: `<bitbucket, github, gitlab>`
- **Default branch**: name of the default branch of the repository (e.g., `master`)
- **XML launch files**: the number ROS launch files in XML
- **Py launch files**: the number ROS launch files in Python (useful for ROS2 projects)
- **Language**: the programming language mainly used in the repository as provided by the hosting platform (e.g., GitHub)
- **Issues (total)**: the total number of issues  
- **Open issues**: the number of open issues 
- **Closed issues**: the number of cloosed issues
- **PR (total)**: the total number of pull requests
- **Open PRs**: the number of open pull requests
- **Closed PRs**: the number of closed pull requests
- **Commits**: the number of commits in the default branch
- **Branches**: the number of branches 
- **Releases**: the number of releases
- **Contributors**: the number of contributors who made at least one commit in the repository
- **Description**: the description of the repository as provided by the hosting platform
- **URL**: the public URL of the repository
- **Categorized by**: the name of the researcher who firstly classified the repository (other two researchers collaboratively double checked the initial classification)
- **Batch**: the batch in which the repository has been classified (repositories where classified in two batches)
- **Included**: `YES` if the repository is included in the final set of 335 _real-world_ projects, `NO` otherwise
- **Violated criterion**: if not included, then this value contains the first selection criterion violated by the repository ([criteria](https://github.com/S2-group/icse-seip-2020-replication-package/data_analysis/RQ1_codes_and_selection_criteria.pdf)) 
- **Scope**: `FULL_SYSTEM` if the repository contains the implementation of a whole system, `SUBSYSTEM` otherwise
- **System type 1**: the type of robots supported by the software in the repository ([see here](https://github.com/S2-group/icse-seip-2020-replication-package/data_analysis/RQ1_codes_and_selection_criteria.pdf))
- **System type 2**: as `System type 1`, in case the repository supports more than one system type
- **System type 3**: as `System type 1`, in case the repository supports more than one system type
- **Capability 1**: the robotic capabilities supported by the software in the repository ([see here](https://github.com/S2-group/icse-seip-2020-replication-package/data_analysis/RQ1_codes_and_selection_criteria.pdf)
- **Capability 2**: as `System Capability 1`, in case the repository supports more than one system capability
- **Capability 3**: as `System Capability 1`, in case the repository supports more than one system capability
- **SA documented**: `YES` if the software architecture is fully documented (e.g., all nodes, topics, and their connections are explicit), `PARTIALLY` if the software architecture is partially documented (e.g., only the exposed topics are documented), `NO` otherwise ([see here](https://github.com/S2-group/icse-seip-2020-replication-package/data_analysis/RQ1_codes_and_selection_criteria.pdf))
- **SA documentation**: the direct link to the documentation of the software architecture of the system (if `SA documented` is either `YES` or `PARTIALLY`)
- **Notes**: additional notes taken during the data extraction process 

The replication package contains also other two comma-separated files, which are proper subsets of the previous one, they are:
- [repos_dataset_selected.csv](https://github.com/S2-group/icse-seip-2020-replication-package/dataset/repos_dataset_selected.csv): it contains all 335 repositories passing the last filtering step related to the manually filtering of irrelevant repositories (filtering step 10 in the paper) 
- [repos_dataset_selected_sadoc.csv](https://github.com/S2-group/icse-seip-2020-replication-package/dataset/repos_dataset_selected_sadoc.csv): it contains the 115 repositories with either a fully or partially documented software architecture (i.e., those having a `YES` or `PARTIALLY` in the `SA documented` field) 

Moreover, additional CSV and PDF files related to the dataset and the extracted guidelines are reported in the [dataset](.dataset) and [data_analysis](.data_analysis) folders, they are not meant for direct use by third-party researchers and are reported for transparency from a methodological perspective. 

---

### Full replication of the study  

The steps for collecting the data on which the study is based are reported below. 

#### Rebuilding the dataset of real-world open-source ROS systems

The goal of the steps below is to build the dataset we provide in [repos_dataset_all.csv](https://github.com/S2-group/icse-seip-2020-replication-package/dataset/repos_dataset_all.csv). All the steps can executed on any UNIX-based machine and have been tested both on MacOS and Ubuntu. As a reference, in [dataset/repos_mining_data/Archive.zip](https://github.com/S2-group/icse-seip-2020-replication-package/dataset/repos_mining_data/Archive.zip) we provide a Zip archive containing all the intermediate artifacts generated along the steps below, so that the reader can double check what to expect at each step.

- Install Python 3.7 (see [here](https://wiki.python.org/moin/BeginnersGuide/Download))
- [optional] setup a Python virtual environment in order to keep all the modules always available and do not run into conflicts with other Python projects (see [here](https://virtualenv.pypa.io/en/latest/))
- Install the following Python modules:
  - git
  - bs4
  - ast
  - urllib3
  - certifi
  - pickle
- configure and run *rosmap* ([instructions](https://github.com/jr-robotics/rosmap)) and collect its results into the following files:
  - `dataset/repos_mining_data/intermediateResults0_rosmap_github.json`
  - `dataset/repos_mining_data/intermediateResults0_all_bitbucket.json`
  - `dataset/repos_mining_data/intermediateResults0_all_gitlab.json`
- Configure *GHTorrent* ([instructions](http://ghtorrent.org/)) as a MySQL database instance, run all the queries in [ghtorrent_queries.sql](https://github.com/S2-group/icse-seip-2020-replication-package/dataset/repos_mining_scripts/ghtorrent_queries.sql), and save the final result in `dataset/repos_mining_dataintermediateResults/2_ghtorrent_github.json`
- run [merge_counter.py](https://github.com/S2-group/icse-seip-2020-replication-package/dataset/repos_mining_scripts/merge_counter.py)
- run [explorer.py](https://github.com/S2-group/icse-seip-2020-replication-package/dataset/repos_mining_scripts/explorer.py)
- run [cloner.py](https://github.com/S2-group/icse-seip-2020-replication-package/dataset/repos_mining_scripts/cloner.py)
- run [detector.py](https://github.com/S2-group/icse-seip-2020-replication-package/dataset/repos_mining_scripts/detector.py)
- run [metrics_manager.py](https://github.com/S2-group/icse-seip-2020-replication-package/dataset/repos_mining_scripts/metrics_manager.py)

The execution of the steps above correspond to the first 9 steps reported in Figure 4 in the [paper](https://github.com/S2-group/icse-seip-2020-replication-package/ICSE_SEIP_2020.pdf). Then, in order to obtain the final list of repositories (i.e., the one equivalent to our 335 repositories), the final manual filtering step (step 10 in Figure 4 in the [paper](https://github.com/S2-group/icse-seip-2020-replication-package/ICSE_SEIP_2020.pdf)) must be performed.   

#### Online questionnaire administration 

- Install Python 3.7 (see [here](https://wiki.python.org/moin/BeginnersGuide/Download))
- [optional] setup a Python virtual environment (see [here](https://virtualenv.pypa.io/en/latest/))
- Install the following Python modules:
  - pdb
  - sendgrid
- Move into `online_questionnaire/online_questionnaire_scripts/repos_to_clone.csv` the ID column of the CSV file containing all the repositories to consider. In other words, the `repos_to_clone.csv` file should contain only one column named `ID` and have a row containing just the ID of the GitHub repository to clone. It is important to note that in this phase we obtained only GitHub repositories in the dataset, so this step assumes that the provided ID are about GitHub repositories only.
- run [email_detector.py](https://github.com/S2-group/icse-seip-2020-replication-package/online_questionnaire/online_questionnaire_scripts/email_detector.py); this will produce the list of all contributors to be targeted by the online questionnaire
- move the contents of the [./online_questionnaire/online_questionnaire_scripts/people_12_months.csv](https://github.com/S2-group/icse-seip-2020-replication-package/online_questionnaire/online_questionnaire_scripts/people_12_months.csv) file into [./online_questionnaire/online_questionnaire_scripts/Mail Sender/email.csv](https://github.com/S2-group/icse-seip-2020-replication-package/online_questionnaire/online_questionnaire_scripts/Mail Sender/emails.csv); this step is done in order to avoid to accidentally send thousands of emails to third-party developers 
- configure the [./online_questionnaire/online_questionnaire_scripts/mailSender.py](https://github.com/S2-group/icse-seip-2020-replication-package/online_questionnaire/online_questionnaire_scripts/mailSender.py) script according to its readme (in the same folder)
- Prepare the questionnaire as a form in Google Drive and update the email template directly in the code of [./online_questionnaire/online_questionnaire_scripts/mailSender.py](https://github.com/S2-group/icse-seip-2020-replication-package/online_questionnaire/online_questionnaire_scripts/mailSender.py)   
- run [./online_questionnaire/online_questionnaire_scripts/mailSender.py](https://github.com/S2-group/icse-seip-2020-replication-package/online_questionnaire/online_questionnaire_scripts/mailSender.py)
- Wait for the first results of the questionnaire!

It is important to note that in this study the data extraction and analysis are predominantly manual, so we refer the reader to the Study design section of the [paper](./ICSE_SEIP_2020.pdf) for knowing the methods we applied for those two phases.  

