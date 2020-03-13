import sys
import os
from git import Repo


def get_blob_recursively(hash_code, file_path_name, repo):

    if '/' in file_path_name:
        sub_dir = file_path_name.split('/', 1)
        changes = repo.git.execute(
            ['git', 'cat-file' , '-p', hash_code])
        for line in changes.split('\n'):
            split = line.split()
            if split[3] == sub_dir[0]:
                sub_tree_hash = split[2]
                return get_blob_recursively(sub_tree_hash, sub_dir[1], repo)
    else:
        changes = repo.git.execute(
            ['git', 'cat-file' , '-p', hash_code])
        for line in changes.split('\n'):
            split = line.split()
            if split[3] == file_path_name:
                final_hash = split[2]
                return repo.git.execute(
                        ['git', 'cat-file' , '-p', final_hash])


def print_commit(commit, repo):

    try:
        print('----')
        print(str(commit.hexsha))
        print(commit.stats.files)
        changed_files = commit.stats.files

        for file_path_name in changed_files.keys():
            print(get_blob_recursively(
                str(commit.tree.hexsha), file_path_name, repo))

        print("\"{}\" by {} ({})".format(commit.summary,
                                         commit.author.name,
                                         commit.author.email))
        print(str(commit.authored_datetime))
        print(str("count: {} and size: {}".format(commit.count(),
                                                  commit.size)))
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
    repo_path = sys.argv[1]
    for repo_index, repo_dir in enumerate(os.scandir(repo_path)):
        repo_path = repo_dir.path
        repo_name = repo_path.split('/')[-1]
        repo = Repo(repo_path)
        
        if not repo.bare:
            commits = list(repo.iter_commits(repo.active_branch))
            print(f'{repo_index+1}. {repo_name} -- {len(commits)}')

            for commit in commits:
                print_commit(commit, repo)
                pass
        else:
            print('Could not load repository at {} :('.format(repo_path))