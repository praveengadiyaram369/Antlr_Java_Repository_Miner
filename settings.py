def init():
    """[this method is primarly used to hold global variables all around the project
         and mainly for initialization of variables to empty]
    """

    # _holds method names which are tracking in the listener - enter, exit and visit
    global target_method_list
    target_method_list = ['enter', 'exit', 'visit']

    global is_antlr_file
    is_antlr_file = False

    global enter_cnt
    global exit_cnt
    global visit_cnt

    enter_cnt = exit_cnt = visit_cnt = 0