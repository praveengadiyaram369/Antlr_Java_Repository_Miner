import sys
import os
import json
import math
import logging
import random

import settings
from RepositoryData import Repository
from CommitData import Commit
from FileData import File

from antlr4 import *
import antlr4
from git import Repo

from antlr4_package.JavaLexer import *
from antlr4_package.JavaParser import *
from antlr4_package.JavaParserListener import *
from PatternListener import PatternListener


def configure_log_settings():
    """[this method is primarily used to configure all log relating settings - default log level is INFO]
    """
    logging.basicConfig(level=logging.INFO, filename='analysing_repos_pattern_evolution.log',
                        filemode='w', format='%(name)s - %(levelname)s - %(message)s')


def check_for_new_iteration(output_repo_data):
    """[this method validates whether the current itertion is a new mining process
       or a continuation of an existing mining process]

    Arguments:
        output_repo_data {[string]} -- [name of the file which stores the information of processed repos]

    Returns:
        [list] -- [holds the list of repository names which are already processed]
    """
    repo_done_name_list = []
    with open('Data_Config_Info/' + output_repo_data, 'r') as f:
        for line in f:
            repo_done_name_list.append(line.strip()) # _just parsing at new lines and appending to a list

    return repo_done_name_list


def get_all_repo_names(input_repo_data):
    """[this method fetches all the repository names]

    Arguments:
        input_repo_data {[string]} -- [description]

    Returns:
        [list] -- [holds the list of all repository names]
    """
    repo_name_list = []
    with open('Data_Config_Info/' + input_repo_data, 'r') as f:
        for line in f:
            repo_name_list.append(line.strip().split(',')[0]) # _just parsing at new lines and also with comma, then append the first value to a list
    return repo_name_list


def get_complexity_with_file(file_path):
    """[this method parses a java file using antlr]
    
    Arguments:
        file_path {[str]} -- [absolute path of the file]
 
    """
    try:
        istream = FileStream(file_path, encoding='utf-8')
        lexer = JavaLexer(istream)
        stream = CommonTokenStream(lexer)
        parser = JavaParser(stream)
        tree = parser.compilationUnit()

        # _using PatternListener to walk only through class and method Declarations
        walker = ParseTreeWalker()
        walker.walk(PatternListener(), tree)

    except Exception as e:
        print("Unexpected error:  " + file_path + "   " + str(e))


def get_complexity_with_content(file_content):
    """[this method parses a java file content using antlr]
    
    Arguments:
        file_content {[str]} -- [complete file content of an antlr file]
  
    """
    try:
        istream = antlr4.InputStream(file_content)
        lexer = JavaLexer(istream)
        stream = CommonTokenStream(lexer)
        parser = JavaParser(stream)
        tree = parser.compilationUnit()

        # _using PatternListener to walk only through class and method Declarations
        walker = ParseTreeWalker()
        walker.walk(PatternListener(), tree)

    except Exception as e:
        print("Unexpected error:  " + str(e))


def get_blob_recursively(hash_code, file_path_name, repo):
    """[this method gives file content(blob) by going recursively through the file path]
    
    Arguments:
        hash_code {bool} -- [hash code of the respective commit]
        file_path_name {[string]} -- [relative path of the blob]
        repo {[repository_object/Git Python]} -- [holds the information of the repository loaded through Git Python library]
    
    Returns:
        [string] -- [File content/blob]
    """
    try:
        if '/' in file_path_name:
            sub_dir = file_path_name.split('/', 1)
            changes = repo.git.execute(
                ['git', 'cat-file', '-p', hash_code]) # _ git cat-file gives the complete file data at that particular commit
            for line in changes.split('\n'):
                split = line.split()
                if split[3] == sub_dir[0]:
                    sub_tree_hash = split[2]
                    return get_blob_recursively(sub_tree_hash, sub_dir[1], repo) # _calling sub-tree recursively
        else:
            changes = repo.git.execute(
                ['git', 'cat-file', '-p', hash_code])
            for line in changes.split('\n'):
                split = line.split()
                if split[3] == file_path_name:
                    final_hash = split[2]
                    return repo.git.execute(
                        ['git', 'cat-file', '-p', final_hash]) # _getting the final blob content
    
    except Exception as e:
        print("Unexpected error:  " + str(e))


def analyze_commit(commit, antlr_file_list, repo, commit_index):
    """[this commit takes commit details and analyze all antlr files inside]
    
    Arguments:
        commit {[object]} -- [commit object holds commit information]
        antlr_file_list {[list]} -- [contains all antlr filenames present in the HEAD revision]
        repo {[repository_object/Git Python]} -- [holds the information of the repository loaded through Git Python library]
        commit_index {[int]} -- [commit id of the respective commit]
    
    Returns:
        [object] -- [commit_data object]
    """
    try:
        commit_data = Commit(str(commit.hexsha), str(
            commit.authored_datetime), commit_index) # _initializing the commit object

        for file_path_name in antlr_file_list:

            file_content = get_blob_recursively(
                str(commit.tree.hexsha), file_path_name, repo) # _getting blob data recursively
            
            if file_content is not None:
                enter_cnt = exit_cnt = visit_cnt = 0
                settings.init() # _resets all the antlr count details

                get_complexity_with_content(file_content)

                is_antlr_file = settings.is_antlr_file
                enter_cnt = settings.enter_cnt
                exit_cnt = settings.exit_cnt
                visit_cnt = settings.visit_cnt

                if is_antlr_file is True:
                    commit_data.add_changed_files(
                        File(file_path_name, is_antlr_file, enter_cnt, exit_cnt, visit_cnt)) # _creating File object and appending to the commit data list

        return commit_data
    except ValueError as ve:
        print("Value error:   " + str(ve))
    except Exception as e:
        print("Unexpected error:  " + str(e))


def get_complexity_project(commit_sha_id, commit_timestamp, repo_path, repo_name, final_commit_id):
    """[this method would be used only for the last commit/HEAD revision, we are finding the all antlr files in the repositories in order to trace back]
    
    Arguments:
        commit_sha_id {[string]} -- [unique hash id of a commit/HEAD]
        commit_timestamp {[string]} -- [timestamp of the commit/HEAD]
        repo_path {[string]} -- [absolute path of the repository]
        repo_name {[string]} -- [name of the repository]
        final_commit_id {[int]} -- [last commit id]
    
    Returns:
        [object] -- [commit data]
    """
    commit_data = Commit(commit_sha_id, commit_timestamp, final_commit_id)
    for subdir, dirs, files in os.walk(os.path.join(repo_path, repo_name)):
        for file in files:
            if file.endswith('.java') and 'BaseListener' not in file and 'BaseVisitor' not in file:

                enter_cnt = exit_cnt = visit_cnt = 0
                settings.init() # _resets all antlr count values 

                get_complexity_with_file(os.path.join(subdir, file))

                is_antlr_file = settings.is_antlr_file
                if is_antlr_file is True:
                    enter_cnt = settings.enter_cnt
                    exit_cnt = settings.exit_cnt
                    visit_cnt = settings.visit_cnt

                    commit_data.add_changed_files(
                        File(os.path.join(subdir, file).replace(repo_path + repo_name + '/', ''), is_antlr_file, enter_cnt, exit_cnt, visit_cnt))

    return commit_data


def get_commit_complexity(commit_data):
    """[this method takes in the commit object and returns the complexity]
    
    Arguments:
        commit_data {[object]} -- [commit object]
    
    Returns:
        [int] -- [complexity of the commit - sum(enter, exit, visit)]
    """
    commit_complexity = 0
    for file_data in commit_data.get_changed_files_list():
        if file_data.get_is_antlr_file() is True:
            commit_complexity += (file_data.get_enter_cnt() +
                                  file_data.get_exit_cnt() + file_data.get_visit_cnt())

    return commit_complexity


def get_antlr_classes(commit_data):
    """[this method takes commit object and returns antlr file list]
    
    Arguments:
        commit_data {[object]} -- [holds commit object data]
    
    Returns:
        [list] -- [list of all antlr files]
    """
    antlr_file_list = []
    for file_data in commit_data.get_changed_files_list():
        if file_data.get_is_antlr_file() is True:
            antlr_file_list.append(file_data.get_file_name())

    return antlr_file_list


def auto_analyze_commits(commit_dict, repo,  antlr_file_list, commits):
    """[this method analyzes all commits by traversing to the middle of the commits everytime and considers the part which has maximum complexity difference]
    
    Arguments:
        commit_dict {[dict]} -- [dictionary contains commit_id as key and complexity as value]
        repo {[object]} -- [repository object data]
        antlr_file_list {[list]} -- [list of all antlr files in that repository]
        commits {[list]} -- [list of all commits in a repository]
    
    Returns:
        [list, list] -- [processed commit object list, processed commit id list]
    """
    commit_step = 0
    previous_commit_index = 0
    commit_data_list = []
    commit_id_list = []

    # _considering a total of 10 commits for each repository
    while commit_step < 8:
        commit_index_list = sorted([int(key) for key, value in commit_dict.items()])
        max_complexity_diff = 0
        max_complexity_index = 0 # _initializing max complexity and index values to 0

        for commit_index, commit_index_value in enumerate(commit_index_list[1:]):
            if commit_dict[commit_index_value] - commit_dict[commit_index_list[commit_index]] > max_complexity_diff:
                max_complexity_diff = commit_dict[commit_index_value] - \
                    commit_dict[commit_index_list[commit_index]]
                max_complexity_index = commit_index + 1

        lower_bound = commit_index_list[max_complexity_index - 1]
        upper_bound = commit_index_list[max_complexity_index]

        next_commit_index = lower_bound + math.floor(
            (abs(lower_bound - upper_bound))/2) # _finding the middle commit

        # _base cases to abort the auto analyze
        if previous_commit_index == next_commit_index or next_commit_index == lower_bound or next_commit_index == upper_bound or next_commit_index > len(commits) - 2:
            return commit_data_list, commit_id_list

        next_commit_data = analyze_commit(
            commits[next_commit_index], antlr_file_list, repo, next_commit_index) # _process the middle commit

        commit_id_list.append(next_commit_index)
        commit_data_list.append(next_commit_data) # _append the middle commit to the procesed the list

        commit_dict[next_commit_index] = get_commit_complexity(
            next_commit_data)
        
        previous_commit_index = next_commit_data
        commit_step += 1

    return commit_data_list, commit_id_list


def fill_random_commits(repo, commits, commit_id_list, antlr_file_list):
    """[this method fills the repositories which has less than 10 commits with random commits]
    
    Arguments:
        repo {[object]} -- [repository object]
        commits {[list]} -- [lsit of all commits in the repository]
        commit_id_list {[list]} -- [list of procesed commits]
        antlr_file_list {[list]} -- [list of all antlr from HEAD revision]
    
    Returns:
        [list] -- [processed list of commit objects]
    """
    commit_data_list = []

    # _considering a total of 10 commits for each repository
    while len(commit_id_list) < 8:
        rand_commit_id = random.randint(1, len(commits) - 2)

        # _considering random commits to fill the limit of 10 
        if rand_commit_id not in commit_id_list:
            rand_commit_data = analyze_commit(
                commits[rand_commit_id], antlr_file_list, repo, rand_commit_id)

            commit_id_list.append(rand_commit_id)
            commit_data_list.append(rand_commit_data)

    return commit_data_list


def walk_repositories(repositories_path, repo_name_list, repo_done_name_list, output_repo_data):
    """[this method walk repositories iterates over all the existing repositories and processes them accordingly]
    Arguments:
        repos_path {[str]} -- [holds absolute path of the folder which contains all repositories]
        repo_name_list {[list]} -- [list of all repository names]
        repo_done_name_list {[type]} -- [list of all repository names which are already processed]
    """
    for repo_index, repo_name in enumerate(repo_name_list):

        # _process the repository only if its not processed earlier
        if repo_name.split('/')[1] not in repo_done_name_list:

            repo_path = repositories_path + repo_name.split('/')[1]
            repo = Repo(repo_path)

            if 'sample' not in output_repo_data:
                repo_id =  ((int(output_repo_data.split('.')[0].split('_')[3]) - 1) * 150) + repo_index + 1
            else:
                repo_id = repo_index + 1

            logging.info(
                f'Started processing repository -- {repo_name} with repo id - {repo_id}')
            
            repo_data = Repository(repo_id, repo_name)
            repo_name = repo_name.split('/')[1]

            if not repo.bare:
                commits = list(repo.iter_commits(repo.active_branch))

                commits.reverse()
                total_commits_len = len(commits)
                repo_data.update_total_commits(total_commits_len)
                project_commit_data = get_complexity_project(str(repo.head.commit.hexsha), str(
                    repo.head.commit.authored_datetime), repositories_path, repo_name, total_commits_len)
                antlr_file_list = get_antlr_classes(project_commit_data)

                commit_1_data = analyze_commit(
                    commits[0], antlr_file_list, repo, commit_index=1)
                commit_dict = {0: get_commit_complexity(commit_1_data), 
                    total_commits_len - 1: get_commit_complexity(project_commit_data)}

                repo_data.add_to_commit_history(commit_1_data)

                commit_data_list, commit_id_list = auto_analyze_commits(
                    commit_dict, repo, antlr_file_list, commits)

                if len(commit_data_list) < 8 and total_commits_len > 9:
                    commit_data_list.extend(fill_random_commits(
                        repo, commits, commit_id_list, antlr_file_list))

                if commit_data_list is not None:
                    for commit_data in commit_data_list:
                        repo_data.add_to_commit_history(commit_data)

                repo_data.add_to_commit_history(project_commit_data)

                with open('Repository_Commit_Data/'+repo_name+ '_' + str(repo_id) + '_data.json', 'w', encoding='utf-8') as f:
                    f.write(repo_data.toJson())

                with open('Data_Config_Info/' + output_repo_data, 'a') as the_file:
                    the_file.write(repo_name + '\n')

            else:
                print('Could not load repository at {} :('.format(repo_path))


def process_repositories(repositories_path, input_repo_data, output_repo_data):
    """[this method processes the information of all repos and repos which are already processed]
    
    Arguments:
        repositories_path {[string]} -- [absolute path of the repositories]
        input_repo_data {[string]} -- [Name of the csv file which contains repository info]
        output_repo_data {[string]} -- [name of the file which stores the information of processed repos]
    """
    repo_done_name_list = check_for_new_iteration(output_repo_data)
    repo_name_list = get_all_repo_names(input_repo_data)

    # _walk through all the repositories
    walk_repositories(repositories_path, repo_name_list,
                      repo_done_name_list, output_repo_data)


if __name__ == "__main__":
    """[main method -- starting point of this program/project]
        command line arguments usage: executable_python_path GitCommitAnalyzer.py #repository_path #input_repo_data.csv #output_repo_data.csv

          #repository_path - Absolute path of the folder where all repositries cloned(using absolute path here, as data is partitioned in other disk, not reachable by relative path).
          #input_repo_data.csv - Name of the csv file which contains repository info
          #output_repo_data.csv - Name of the txt which will be updated once a repo is processed/mined.

        Example;-
        # /home/praveen/anaconda3/bin/python /home/praveen/Documents/web_and_data_science/semester_1/mining_software_repositories/assignment_3/finalproject/GitCommitAnalyzer.py /home/praveen/Documents/web_and_data_science/semester_1/mining_software_repositories/assignment_2/project/repositories/ repository_mining_data_sample.csv repo_names_done_sample.txt

    """

    configure_log_settings()

    logging.info(
        f'Starting Analysing Java Repositories for evolution of antlr4 patterns...')

    repo_path = sys.argv[1]
    input_repo_data = sys.argv[2]
    output_repo_data = sys.argv[3]

    # _start porcessing the repositories
    process_repositories(
        repo_path, input_repo_data, output_repo_data)

    logging.info(
        f'Finished Analysing Java Repositories for evolution of antlr4 patterns...')
