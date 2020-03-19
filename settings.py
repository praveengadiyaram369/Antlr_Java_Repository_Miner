def init():
    """[this method is primarly used to hold global variables all around the project
         and mainly for initialization of variables to empty]
    """

    # _holds method names which are tracking in the listener - enter, exit and visit
    global target_method_list
    target_method_list = ['enter', 'exit', 'visit']

    # _holds a boolean value to determine whether file is antlr or not
    global is_antlr_file
    is_antlr_file = False

    # _these three variables hold the information of the counts of enter, exit and visit methods in an antlr file
    global enter_cnt
    global exit_cnt
    global visit_cnt

    # _intializing the variables with count zero
    enter_cnt = exit_cnt = visit_cnt = 0