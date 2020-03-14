class Commit:
    
    def __init__(self, sha_id, timestamp):

        self._sha_id = sha_id
        self._timestamp = timestamp
        self._changed_files_list = []

    def add_changed_files(self, changed_file):
        self._changed_files_list.append(changed_file)

    def get_sha_id(self):
        return self._sha_id
    
    def get_timestamp(self):
        return self._timestamp

    def get_changed_files_list(self):
        return self._changed_files_list