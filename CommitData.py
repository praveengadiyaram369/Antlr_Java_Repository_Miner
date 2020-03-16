import json


class Commit:

    def __init__(self, sha_id, timestamp, commit_index):

        self._sha_id = sha_id
        self._timestamp = timestamp
        self._commit_index = commit_index
        self._changed_files_list = []

    def add_changed_files(self, changed_file):
        self._changed_files_list.append(changed_file)

    def get_sha_id(self):
        return self._sha_id

    def get_timestamp(self):
        return self._timestamp

    def get_commit_index(self):
        return self._commit_index

    def get_changed_files_list(self):
        return self._changed_files_list

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__, indent=4)

    def __repr__(self):
        return self.toJson()
