import sys
from git import Repo


def print_commit(commit, repo_path):

    try:
        print('----')
        print(str(commit.hexsha))
        print(commit.stats.files)
        changed_files = commit.stats.files

        # for tree in commit.tree.trees:
        #     for blob in commit.blobs:
        #         print(blob)
        #     print(blob.name)

        for file_path_name in changed_files.keys():
            changes = repo.git.execute(
                        ['git', 'cat-file','233ca8063361cfe16a53abf3bbb0e47b0b4b38a7', file_path_name, repo_path])
            print(changes)

        
        #print(commit.tree.blobs[0].data_stream.read())
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
    # Repo object used to programmatically interact with Git repositories
    repo = Repo(repo_path)
    # check that the repository loaded correctly
    if not repo.bare:
        print('Repo at {} successfully loaded.'.format(repo_path))
        print_repository(repo)
    
        # create list of commits then print some of them to stdout
        commits = list(repo.iter_commits('master'))
        for commit in commits:
            print_commit(commit, repo_path)
            pass
    else:
        print('Could not load repository at {} :('.format(repo_path))