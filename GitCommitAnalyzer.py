import sys
import os
import json

import settings
from CommitData import Commit
from FileData import File
from antlr4_package.JavaLexer import *
from antlr4_package.JavaParser import *
from antlr4_package.JavaParserListener import *
from PatternListener import PatternListener
from RepositoryData import Repository

from antlr4 import *
from git import Repo


def get_complexity(file_content):
    try:
        istream = FileStream(file_content, encoding='utf-8')
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


def analyze_commit(commit, repo):

    try:
        commit_data = Commit(str(commit.hexsha), str(commit.authored_datetime))
        changed_files = commit.stats.files

        for file_path_name in changed_files.keys():

            if file_path_name.endswith('.java'):

                enter_cnt = exit_cnt = visit_cnt = 0
                settings.init()

                file_content = get_blob_recursively(
                    str(commit.tree.hexsha), file_path_name, repo)
                file_content = file_content.encode('unicode_escape').decode('utf-8')
                print(file_content)
                get_complexity(file_content)

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


def print_repository(repo):
    print('Repo description: {}'.format(repo.description))
    print('Repo active branch is {}'.format(repo.active_branch))
    for remote in repo.remotes:
        print('Remote named "{}" with URL "{}"'.format(remote, remote.url))
    print('Last commit for repo is {}.'.format(str(repo.head.commit.hexsha)))


if __name__ == "__main__":

    for repo_index, repo_dir in enumerate(os.scandir(sys.argv[1])):

        repo_path = repo_dir.path
        repo = Repo(repo_path)

        repo_id = repo_index+1
        repo_name = repo_path.split('/')[-1]
        repo_data = Repository(repo_id, repo_name)

        if not repo.bare:
            commits = list(repo.iter_commits(repo.active_branch))
            print(f'{repo_id}. {repo_name} -- {len(commits)}')

            for commit in commits:
                repo_data.add_to_commit_history(analyze_commit(commit, repo))

            with open(repo_name + '_data.json', 'w', encoding='utf-8') as f:
                json.dump(repo_data.__dict__, f, ensure_ascii=False, indent=4)

        else:
            print('Could not load repository at {} :('.format(repo_path))
