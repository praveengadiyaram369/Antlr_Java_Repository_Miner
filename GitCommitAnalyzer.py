import sys
import os
import json
import math

import settings
from CommitData import Commit
from FileData import File
from antlr4_package.JavaLexer import *
from antlr4_package.JavaParser import *
from antlr4_package.JavaParserListener import *
from PatternListener import PatternListener
from RepositoryData import Repository

from antlr4 import *
import antlr4
from git import Repo


def get_complexity_with_file(file_path):
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
        print("Unexpected error:  " + repo_path + "   " + str(e))


def get_blob_recursively(hash_code, file_path_name, repo):

    if '/' in file_path_name:
        sub_dir = file_path_name.split('/', 1)
        changes = repo.git.execute(
            ['git', 'cat-file', '-p', hash_code])
        for line in changes.split('\n'):
            split = line.split()
            if split[3] == sub_dir[0]:
                sub_tree_hash = split[2]
                return get_blob_recursively(sub_tree_hash, sub_dir[1], repo)
    else:
        changes = repo.git.execute(
            ['git', 'cat-file', '-p', hash_code])
        for line in changes.split('\n'):
            split = line.split()
            if split[3] == file_path_name:
                final_hash = split[2]
                return repo.git.execute(
                    ['git', 'cat-file', '-p', final_hash])


def analyze_commit(commit, antlr_file_list, repo, commit_index):

    try:
        commit_data = Commit(str(commit.hexsha), str(commit.authored_datetime), commit_index)
        changed_files = commit.stats.files

        for file_path_name in changed_files.keys():

            if file_path_name.endswith('.java') and file_path_name in antlr_file_list:

                enter_cnt = exit_cnt = visit_cnt = 0
                settings.init()

                file_content = get_blob_recursively(
                    str(commit.tree.hexsha), file_path_name, repo)
                get_complexity_with_content(file_content)

                is_antlr_file = settings.is_antlr_file
                enter_cnt = settings.enter_cnt
                exit_cnt = settings.exit_cnt
                visit_cnt = settings.visit_cnt

                commit_data.add_changed_files(
                    File(file_path_name, is_antlr_file, enter_cnt, exit_cnt, visit_cnt))

        return commit_data
    except ValueError as ve:
        print("Value error:  " + repo_path + "   " + str(ve))
    except Exception as e:
        print("Unexpected error:  " + repo_path + "   " + str(e))


def get_complexity_project(commit_sha_id, commit_timestamp,repo_path):

    commit_data = Commit(commit_sha_id, commit_timestamp, len(commits))
    for subdir, dirs, files in os.walk(os.path.join(repo_path, repo_name)):
        for file in files:
            if file.endswith('.java') and 'BaseListener' not in file and 'BaseVisitor' not in file:

                enter_cnt = exit_cnt = visit_cnt = 0
                settings.init()

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
    commit_complexity = 0
    for file_data in commit_data.get_changed_files_list():
        if file_data.get_is_antlr_file() is True:
            commit_complexity += (file_data.get_enter_cnt() +
                                  file_data.get_exit_cnt() + file_data.get_visit_cnt())

    return commit_complexity


def get_antlr_classes(commit_data):
    antlr_file_list = []
    for file_data in commit_data.get_changed_files_list():
        if file_data.get_is_antlr_file() is True:
            antlr_file_list.append(file_data.get_file_name())

    return antlr_file_list


def auto_analyze_commits(commit_dict, antlr_file_list, commits):

    commit_step = 0
    commit_data_list = []

    while commit_step <= 8:
        commit_index_list = sorted([key for key, value in commit_dict.items()])
        max_complexity_diff = 0
        max_complexity_index = 0

        for commit_index, commit_index_value in enumerate(commit_index_list[1:]):
            if commit_dict[commit_index_value] - commit_dict[commit_index_list[commit_index]] > max_complexity_diff:
                max_complexity_diff = commit_dict[commit_index_value] - \
                    commit_dict[commit_index_list[commit_index]]
                max_complexity_index = commit_index + 1

        lower_bound = int(commit_index_list[max_complexity_index - 1])
        upper_bound = int(commit_index_list[max_complexity_index])

        next_commit_index = lower_bound + math.floor(
            (abs(lower_bound - upper_bound))/2)

        if next_commit_index == lower_bound or next_commit_index == upper_bound or next_commit_index >= len(commits) - 1:
            return commit_data_list

        next_commit_data = analyze_commit(
            commits[next_commit_index], antlr_file_list, repo, next_commit_index)
        commit_data_list.append(next_commit_data)

        commit_dict[str(next_commit_index)] = get_commit_complexity(
            next_commit_data)

        commit_step += 1


if __name__ == "__main__":

# /home/praveen/anaconda3/bin/python /home/praveen/Documents/web_and_data_science/semester_1/mining_software_repositories/assignment_3/finalproject/GitCommitAnalyzer.py /home/praveen/Documents/web_and_data_science/semester_1/mining_software_repositories/assignment_3/project/repositories/ 

    repositories_path = sys.argv[1]
    for repo_index, repo_dir in enumerate(os.scandir(repositories_path)):

        repo_path = repo_dir.path
        repo = Repo(repo_path)

        repo_id = repo_index+1
        repo_name = repo_path.split('/')[-1]
        repo_data = Repository(repo_id, repo_name)


        if not repo.bare:
            commits = list(repo.iter_commits(repo.active_branch))
            print(f'{repo_id}. {repo_name} -- {len(commits)}')

            commits.reverse()
            total_commits_len = len(commits)
            project_commit_data = get_complexity_project(str(repo.head.commit.hexsha), str(repo.head.commit.authored_datetime),repositories_path)
            antlr_file_list = get_antlr_classes(project_commit_data)

            commit_1_data = analyze_commit(commits[0], antlr_file_list, repo, commit_index = 1)
            commit_dict = {'0': get_commit_complexity(commit_1_data), str(
                total_commits_len - 1): get_commit_complexity(project_commit_data)}

            repo_data.add_to_commit_history(commit_1_data)

            commit_data_list = auto_analyze_commits(
                commit_dict, antlr_file_list, commits)

            if commit_data_list is not None:
                for commit_data in commit_data_list:
                    repo_data.add_to_commit_history(commit_data)

            repo_data.add_to_commit_history(project_commit_data)

            with open('Repository_Commit_Data/'+repo_name + '_data.json', 'w', encoding='utf-8') as f:
                f.write(repo_data.toJson())

        else:
            print('Could not load repository at {} :('.format(repo_path))
