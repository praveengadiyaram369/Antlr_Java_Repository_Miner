import json


class Commit:
    """[Commit class encapsulates the information of the commit details for a particular repository]
    """

    def __init__(self, sha_id, timestamp, commit_index):
        """[this constructor initializes a commit object with provided arguments and return a commit object]

        Arguments:
            sha_id {[string]} -- [unique hash id of a commit]
            timestamp {[string]} -- [timestamp of the respective commit]
            commit_index {[int]} -- [commit id with respect to the HEAD]

        Returns:
            [object] -- [commit_object]
        """
        self._sha_id = sha_id
        self._timestamp = timestamp
        self._commit_index = commit_index
        self._changed_files_list = []  # _holds the list of file objects

    @classmethod
    def from_json_file(cls, json_data):
        cls_dict = json.loads(json_data)
        return cls(cls_dict['_sha_id'], cls_dict['_timestamp'], cls_dict['_commit_index'])

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