# coding: utf-8

import sys
sys.path.append('..')

import schedule
import time

import pin
import api
import db
import cx_Oracle

# TODO: get through arguments
ticker = 'GAZP'     
commission = 0.05
reserve = 200
tz = 3
interval = 'hour'


figi = api.get_figi_by_ticker(ticker)
broker_id = api.get_broker_account_id()
t = api.get_ticker(ticker)



hour_start, hour_finish = api.get_hour_interval(ticker, interval, tz)
hour_num = hour_start - 1


l_orders = list()

def update_status_orders():
    with cx_Oracle.connect(user=db.user, password=db.password,
                    dsn=db.dsn,
                    encoding="UTF-8") as connection:
        cursor = connection.cursor()
        for i in range(len(l_orders)):
            print('Trying to update order with rowid: {rowid}'.format(rowid=l_orders[i]))
            try:
                stmt = "UPDATE TINKOFF.ORDERS SET OP_STATUS = 'CLOSED' WHERE ROWID = '{rowid}'".format(rowid = l_orders[i])
                cursor.execute(stmt)
            except:
                print('Update is failed!')
                connection.commit()
                sys.exit(0)
            connection.commit()

def close_previous(level):
    global ticker
    l_orders = [] # empty before cycle
    with cx_Oracle.connect(user=db.user, password=db.password,
                    dsn=db.dsn,
                    encoding="UTF-8") as connection:
        cursor = connection.cursor()
        for order_row in cursor.execute("""SELECT EXECUTED_LOTS
                                                , ROWID
                                             FROM TINKOFF.ORDERS
                                            WHERE ORDER_LEVEL = {level} - 2
                                              AND OP_STATUS = 'OPEN'
                                              AND TRUNC(CREATE_DATE) = TRUNC(SYSDATE)
                                              AND TICKER = '{ticker}'""".format(level=level, ticker=ticker)):
            print('Trying to close with rowid: {rowid}'.format(rowid=order_row[1]))
            status_code, b_json = api.post_market_order(figi, broker_id, order_row[0], 'Sell')
            if status_code == 200:
                l_orders.append(order_row[1])
            else:
                print('Closing failed!')
                db.pop_log(ticker, b_json, status_code, 'CREATION MARKET ORDER', 'ERROR')
                sys.exit(0)

def count_lots(cur_level, t_ticker):
    global commission, reserve
    balance = api.get_balance()
    lots = int(balance / (cur_level * t_ticker.lot))
    amount = lots*cur_level + lots*cur_level * commission + reserve
    if balance > amount:
        return lots
    else:
        return None
    
def job():
    global hour_num, hour_start, hour_finish, ticker, broker_id, reserve, commission
    hour_num = hour_num + 1

    print('hour_num: ' + str(hour_num))

    # close previous order
    if hour_num != hour_start:
        close_previous(hour_num)
        update_status_orders()
    
    # if last - don't create others
    if hour_num == hour_finish:
        print('THE END')
        sys.exit(0)

    # create new order
    print("Let's find previous pin!")
    if hour_num == hour_start:
        b, level = pin.is_prev_hour_of_day_pin(ticker)
        b, level = pin.is_prev_hour_pin(ticker)
    n = 0
    if b:
        print('Has found previous pin with level: {level}'.format(level=level))
        while n < 60:
            time.sleep(60)
            n = n + 1
            cur_level = api.get_cur_high(ticker, 'hour')
            if cur_level > level:
                lots = count_lots()
                if lots != None:
                    status_code, b_json = api.post_market_order(figi, broker_id, lots)
                    if status_code == 200:
                        db.pop_log(ticker, b_json, status_code, 'CREATED BUY MARKET ORDER')
                        db.pop_order(ticker, b_json, 'hour', hour_num)
                    else:
                        db.pop_log(ticker, b_json, status_code, 'CREATION MARKET ORDER ERROR', 'ERROR')
                break
            else:
                continue

if __name__ == "__main__":
    for i in range(hour_start, hour_finish):
        if i == hour_finish:
            schedule.every().day.at(str(hour_finish-1) + ":55:00").do(job)
            continue
        hour = str(i) if len(str(i)) == 2 else '0' + str(i)
        schedule.every().day.at(hour + ":00:01").do(job)
        
    while True:
        schedule.run_pending()
        time.sleep(1)