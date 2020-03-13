class File:

    def __init__(self, file_name, is_antlr_file, enter_cnt, exit_cnt, visit_cnt):

        self._file_name = file_name
        self._is_antlr_file = is_antlr_file
        self._enter_cnt = enter_cnt
        self._exit_cnt = exit_cnt
        self._visit_cnt = visit_cnt

