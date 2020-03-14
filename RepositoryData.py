import json


class Repository():

    def __init__(self, repo_id, repo_name):

        self._repo_id = repo_id
        self._repo_name = repo_name
        self._commit_history = []

    def add_to_commit_history(self, commit_data):
        self._commit_history.append(commit_data)

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__, indent=4)

    def __repr__(self):
        return self.toJson()
