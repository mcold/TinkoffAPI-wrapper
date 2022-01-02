# coding: utf-8

import db

def main():
    """
        Search actions from db
    """
    act_list = db.Actions()
    for act in act_list:
        if act.type == 'GET PORTFOLIO':
            db.pop_portfolio()
            act_list.del_act_id(act.id)
        if act.type == 'BUY': # TODO: and do_time >= current_time
            pass # TODO: execute post
        if act.type == 'SELL': # TODO: and do_time >= current_time
            pass # TODO: execute post
         
    




if __name__ == "__main__":
    main()