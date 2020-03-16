import json


class Repository():

    def __init__(self, repo_id, repo_name, total_commits= 0):

        self._repo_id = repo_id
        self._repo_name = repo_name
        self._total_commits = total_commits
        self._commit_history = []

    @classmethod
    def from_json_file(cls, json_data):
        cls_dict = json.loads(json_data)
        return cls(cls_dict['_repo_id'], cls_dict['_repo_name'], cls_dict['_total_commits'])

    def update_total_commits(self, total_commits):
        self._total_commits = total_commits
        
    def add_to_commit_history(self, commit_data):
        self._commit_history.append(commit_data)

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__, indent=4)

    def __repr__(self):
        return self.toJson()
