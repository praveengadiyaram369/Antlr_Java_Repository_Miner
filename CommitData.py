class Commit:
    
    def __init__(self, sha_id, timestamp):

        self._sha_id = sha_id
        self._timestamp = timestamp
        self._changed_files = []

    def add_changed_files(self, changed_file):
        self._changed_files.append(changed_file)
