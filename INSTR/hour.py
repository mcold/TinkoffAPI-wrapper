# coding: utf-8

import sys
sys.path.append('..')

import schedule
import time
import datetime

import pin
import api
import db
from market import Order

order = Order(dict())

ticker = 'GAZP'     
commission = 0.05
reserve = 200
tz = 3
interval = 'hour'
type = 'M'


flag = False # is being used in closing order partly (not to close fully)
figi = api.get_figi_by_ticker(ticker)
broker_id = api.get_broker_account_id()
t = api.get_ticker(ticker)



hour_start, hour_finish = api.get_hour_interval(ticker, interval, tz)
hour_num = hour_start - 1

def close_previous():
    global order, ticker, figi, interval, type, flag
    if order.bar_number == 2:
        print(str(datetime.datetime.now()) + ': ' + 'Trying to close {ticker}'.format(ticker=ticker))
        lots = int(order.lots / 2)
        status_code, b_json = api.post_market_order(figi, broker_id, lots, 'Sell')
        if status_code == 200:
            print(str(datetime.datetime.now()) + ': ' + 'Sold {ticker}: {lots}'.format(ticker=ticker, lots=lots))
            order.lots = order.lots - lots
            order.bar_number = order.bar_number - 1 # level down
            flag = True # closed partly
            # for order population
            pop_order = order
            pop_order.lots = lots
            db.pop_order(interval, pop_order, 'CLOSE', type=type)
        else:
            print(str(datetime.datetime.now()) + ': ' + 'Closing is failed!')
            db.pop_log(ticker, b_json, status_code, 'CREATION MARKET ORDER', 'ERROR')
            sys.exit(0)
    elif order.bar_number == 1:
        status_code, b_json = api.post_market_order(figi, broker_id, order.lots, 'Sell')
        if status_code == 200:
            print('Sold {ticker}: {lots}'.format(ticker=ticker, lots=order.lots))
            db.pop_order(interval, order, 'CLOSE', type=type)
            order = Order(dict()) # clear order
        else:
            print(str(datetime.datetime.now()) + ': ' + 'Closing is failed!')
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
    global hour_num, hour_start, hour_finish
    global ticker, broker_id, reserve, commission
    global order, interval, flag
    hour_num = hour_num + 1

    print(str(datetime.datetime.now()) + ': ' + 'hour_num: ' + str(hour_num))

    # close previous order
    if hour_num != hour_start:
        if order.order_id != '':
            close_previous(hour_num)
    
    # if last - don't create others
    if hour_num == hour_finish:
        print(str(datetime.datetime.now()) + ': ' + 'THE END')
        sys.exit(0)
    
    if order.order_id == '':
        # create new order
        print(str(datetime.datetime.now()) + ': ' + "Let's find previous pin!")
        if hour_num == hour_start:
            b, level = pin.is_prev_hour_of_day_pin(ticker)
        else:        
            b, level = pin.is_prev_hour_pin(ticker)
        n = 0
        if b:
            print(str(datetime.datetime.now()) + ': ' + 'Has found previous pin with level: {level}'.format(level=level))
            while n < 60:
                time.sleep(60)
                n = n + 1
                cur_level = api.get_cur_high(ticker, interval)
                if cur_level > level:
                    lots = count_lots()
                    if lots != None:
                        status_code, b_json = api.post_market_order(figi, broker_id, lots)
                        if status_code == 200:
                            db.pop_log(ticker, b_json, status_code, 'CREATED BUY MARKET ORDER')
                            db.pop_order(interval, order, 'OPEN')
                            order = Order(b_json, cur_level, ticker)
                        else:
                            db.pop_log(ticker, b_json, status_code, 'CREATION MARKET ORDER ERROR', 'ERROR')
                    break
                else:
                    continue
    else:
        # close if price less then level
        print(order)
        if not flag: # only if it next hour_num
            n = 0
            while n < 60:
                time.sleep(60)
                n = n + 1
                cur_level = api.get_cur_high(ticker, interval)
                if cur_level < order.level:
                    status_code, b_json = api.post_market_order(figi, broker_id, order.lots, 'Sell')
                    if status_code == 200:
                        print('Sold {ticker}: {lots}'.format(ticker=ticker, lots=order.lots))
                        db.pop_order(interval, order, 'CLOSE', type=type)
                        order = Order(dict()) # clear order
                    else:
                        print(str(datetime.datetime.now()) + ': ' + 'Closing is failed!')
                        db.pop_log(ticker, b_json, status_code, 'CREATION MARKET ORDER', 'ERROR')
                        sys.exit(0)
    flag = False # finished current hour_num


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