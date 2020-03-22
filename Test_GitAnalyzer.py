# _importing python in-built libraries
import unittest
import os
import json

# _importing repository wrapper classes
from RepositoryData import Repository
from CommitData import Commit
from FileData import File

# _importing GitCommitAnalyzer to simulate sample repository test
from GitCommitAnalyzer import process_repositories


class TestGitCommitAnalyzer(unittest.TestCase):
    """[this class is strictly used to test results from the GitCommitAnalyzer.py]

    Arguments:
        unittest {[class]} -- [unitest Base class - in-built python library]

    """

    @classmethod
    def setUpClass(cls):
        """[this method is used to create necessary setup for testing -- loading sample repository data]

        Test 1: Testing whether the name of the repository is appropriate
        Test 2: Testing the enter/exit/visit method counts after the last commit are stored properly
        Test 3: Testing the enter/exit/visit method counts after the some random commit are stored properly

        """

        open('Data_Config_Info/repo_names_done_sample.txt',
             'w').close()  # _clearing contents output data file

        repo_data_json = process_repositories(os.path.abspath(
            "repositories/"), "repository_mining_data_sample.csv", "repo_names_done_sample.txt")  # _simulating repository analysis on sample data

        # _using in-built json library, loading file data to a json object
        repo_json_data = json.loads(repo_data_json)

        TestGitCommitAnalyzer.repo_data = Repository(
            repo_json_data['_repo_id'], repo_json_data['_repo_name'], repo_json_data['_total_commits'])  # _initializing Repository data

        for commit in repo_json_data['_commit_history']:
            commit_data = Commit(
                commit['_sha_id'], commit['_timestamp'], commit['_commit_index'])  # _initializing commit object for each commit

            for file_data in commit['_changed_files_list']:
                commit_data.add_changed_files(File(file_data['_file_name'], file_data['_is_antlr_file'],
                                                   file_data['_enter_cnt'], file_data['_exit_cnt'], file_data['_visit_cnt']))

            TestGitCommitAnalyzer.repo_data.add_to_commit_history(
                commit_data)  # _adding all commit objects to a list

    def test_repo_name(self):
        """[this method primarily tests whether the repository name is being captured along with username or not]
        """

        self.assertEqual(
            TestGitCommitAnalyzer.repo_data.get_repo_name(), 'meridor/perspective-backend')

    def test_repo_last_commit(self):
        """[this method primarily tests whether the complexity after last commit/HEAD is saved corectly or not]
        
            1) https://github.com/meridor/perspective-backend/blob/master/perspective-sql/src/main/java/org/meridor/perspective/sql/impl/parser/QueryParserImpl.java
            2) https://github.com/meridor/perspective-backend/blob/master/perspective-sql/src/main/java/org/meridor/perspective/sql/impl/PlaceholderConfigurer.java
        """

        PlaceholderConfigurer_exit_cnt = 4
        QueryParserImpl_exit_cnt = 9

        file_data_list = get_file_data_list(
            TestGitCommitAnalyzer.repo_data, TestGitCommitAnalyzer.repo_data.get_total_commits())

        for file_data in file_data_list:
            if 'QueryParserImpl' in file_data.get_file_name():
                self.assertEqual(file_data.get_exit_cnt(),
                                 QueryParserImpl_exit_cnt)
            elif 'PlaceholderConfigurer' in file_data.get_file_name():
                self.assertEqual(file_data.get_exit_cnt(),
                                 PlaceholderConfigurer_exit_cnt)

    def test_repo_random_commit(self):
        """[this method primarily tests whether the complexity after random commit is saved corectly or not]
        

            1)  git cat-file -p 1d2ab4ec04ed4feeb6c084b186a7e38ac1d4bc63
            2)  git cat-file -p eb606b114fe4d221b3cf09654f9e8e4fcea4e8ed
            3)  git cat-file -p 67b7573c974a3a4a65498d629673b7706df625a8
            4)  git cat-file -p db3589274877f858f84704ac917dcb318acfdf99
            5)  git cat-file -p 532c93151e4af81d0c385f4c7ef37791449550bc
            6)  git cat-file -p f03c1205397e5f3433def5b933536d13f7eadfea
            7)  git cat-file -p eda73e59b3fa197987a47ddcd5b1992ffaff8550
            8)  git cat-file -p 1aea46ee5a6877a00c35b1fd517c0d02c6dbd064
            9)  git cat-file -p 35e9fe3c81c5ceb25d5991f5e1ed6f7cb72e929d
            10)  git cat-file -p e294c6d2bfa24f18e4f6cd993ca64c134c32cf36
            11)  git cat-file -p 70dff7339e7ec5ef261a6a1a1b598a85baac2e6a
            12)  git cat-file -p 1fc62c7edcdae4114e4f90308053065cdd8ad642 (whole file contents after 141 commit)
        """

        commit_id = 141
        PlaceholderConfigurer_exit_cnt = 4

        file_data_list = get_file_data_list(
            TestGitCommitAnalyzer.repo_data, commit_id)

        for file_data in file_data_list:
            if 'PlaceholderConfigurer' in file_data.get_file_name():
                self.assertEqual(file_data.get_exit_cnt(),
                                 PlaceholderConfigurer_exit_cnt)


def get_file_data_list(repo_data, commit_id):
    """[this method returns list files in a particular commit ina repository]

    Arguments:
        repo_data {[object]} -- [Repository object of the testing repo]
        commit_id {[int]} -- [commit id of a particular repository commit]

    Returns:
        [list] -- [list files inside commit id given]
    """
    commit_data_list = repo_data.get_commit_history()
    for commit in commit_data_list:
        if commit.get_commit_index() == commit_id:
            return commit.get_changed_files_list()

    return []


if __name__ == '__main__':
    """[this is the starting point of this testing process/thread]
    """

    unittest.main(argv=['first-arg-is-ignored'], exit=False)
