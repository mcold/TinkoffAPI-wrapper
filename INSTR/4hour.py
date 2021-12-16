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
interval2 = '4hour'
type = 'M'


flag = False # is being used in closing order partly (not to close fully)
figi = api.get_figi_by_ticker(ticker)
broker_id = api.get_broker_account_id()
t = api.get_ticker(ticker)

hour_start, hour_finish = api.get_4hour_interval(ticker, interval, tz)
hour_num = hour_start - 4
hour_end = hour_finish + 4 

def close_previous():
    global order, ticker, figi, interval, type, flag
    if order.bar_number == 2:
        print(str(datetime.datetime.now()) + ': ' + 'Trying to close {ticker}'.format(ticker=ticker))
        lots = int(order.lots / 2)
        status_code, b_json = api.post_market_order(figi, broker_id, lots, 'Sell' if order.operation == 'Buy' else 'Sell')
        if status_code == 200:
            print(str(datetime.datetime.now()) + ': ' + 'Sold {ticker}: {lots}'.format(ticker=ticker, lots=lots))
            order.lots = order.lots - lots
            order.bar_number = order.bar_number - 1 # level down
            flag = True # closed partly
            # for order population
            # pop_order = order
            # pop_order.lots = lots
            # db.pop_order(interval2, pop_order, 'CLOSE', type=type)
        else:
            print(str(datetime.datetime.now()) + ': ' + 'Closing is failed!')
            # db.pop_log(ticker, b_json, status_code, 'CREATION MARKET ORDER', 'ERROR')
            sys.exit(0)
    elif order.bar_number == 1:
        status_code, b_json = api.post_market_order(figi, broker_id, order.lots, 'Sell' if order.operation == 'Buy' else 'Sell')
        if status_code == 200:
            print('Sold {ticker}: {lots}'.format(ticker=ticker, lots=order.lots))
            # db.pop_order(interval2, order, 'CLOSE', type=type)
            order = Order(dict()) # clear order
        else:
            print(str(datetime.datetime.now()) + ': ' + 'Closing is failed!')
            # db.pop_log(ticker, b_json, status_code, 'CREATION MARKET ORDER', 'ERROR')
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
    hour_num = hour_num + 4

    print(str(datetime.datetime.now()) + ': ' + 'hour_num: ' + str(hour_num) + '\n')

    # close previous order
    if hour_num != hour_start:
        if order.order_id != '':
            close_previous()
    
    # if last - don't create others
    if hour_num == hour_finish+1:
        print(str(datetime.datetime.now()) + ': ' + 'THE END\n\n')
        # sys.exit(0)
    
    if order.order_id == '':
        # create new order
        print(str(datetime.datetime.now()) + ': ' + "Let's find previous pin!"+ '\n')
        b, high_level, low_level = pin.is_prev_4hour_pin(ticker, interval)
        n = 1
        if b:
            print(str(datetime.datetime.now()) + ': ' + 'Has found previous pin with levels: high: {high} low: {low}'.format(high=high_level, low=low_level) + '\n')
            while n < 60:
                time.sleep(60)
                n = n + 1

                candle = api.get_cur_day_4hour_candle(ticker, interval)
                if candle.high > high_level:
                    lots = count_lots(candle.close, t)
                    if lots != None:
                        status_code, b_json = api.post_market_order(figi, broker_id, lots, 'Buy')
                        if status_code == 200:
                            print('Bought: ' + str(datetime.datetime.now()) + 'lots: ' + str(lots))
                            # db.pop_log(ticker, b_json, status_code, 'CREATED BUY MARKET ORDER' + '\n')
                            # db.pop_order(interval, order, 'OPEN')
                            order = Order(b_json, candle.high, ticker)
                        # else:
                        #     db.pop_log(ticker, b_json, status_code, 'CREATION MARKET ORDER ERROR', 'ERROR')
                    break
                elif candle.low < low_level: 
                    lots = count_lots(candle.close, t)
                    if lots != None:
                        status_code, b_json = api.post_market_order(figi, broker_id, lots, 'Sell')
                        if status_code == 200:
                            print('Sold: ' + str(datetime.datetime.now()) + 'lots: ' + str(lots))
                            # db.pop_log(ticker, b_json, status_code, 'CREATED SELL MARKET ORDER' + '\n')
                            # db.pop_order(interval, order, 'OPEN')
                            order = Order(b_json, candle.low, ticker)
                        # else:
                        #     db.pop_log(ticker, b_json, status_code, 'CREATION MARKET ORDER ERROR', 'ERROR')
                else:
                    print('-'*50 + str(datetime.datetime.now()))
                    print('Current level: close: ' + str(candle.close))
                    print('Pin' + ' '*10 + ': high: ' + str(high_level) + ' low: ' + str(low_level))
                    print('-'*50)
                    continue
    else:
        # close if price less then level
        print(order)
        if not flag: # only if it next hour_num
            n = 0
            while n < 60:
                time.sleep(60)
                n = n + 1
                candle = api.get_cur_day_4hour_candle(ticker, interval)
                if order.operation == 'Buy':
                    if candle.close < order.level:
                        status_code, b_json = api.post_market_order(figi, broker_id, order.lots, 'Sell')
                        if status_code == 200:
                            print('Sold {ticker}: {lots}'.format(ticker=ticker, lots=order.lots))
                            # db.pop_order(interval, order, 'CLOSE', type=type)
                            order = Order(dict()) # clear order
                        else:
                            print(str(datetime.datetime.now()) + ': ' + 'Closing is failed!' + '\n')
                            # db.pop_log(ticker, b_json, status_code, 'CREATION MARKET ORDER', 'ERROR')
                            sys.exit(0)
                else:
                    if candle.close > order.level:
                        status_code, b_json = api.post_market_order(figi, broker_id, order.lots, 'Buy')
                        if status_code == 200:
                            print('Bought {ticker}: {lots}'.format(ticker=ticker, lots=order.lots))
                            # db.pop_order(interval, order, 'CLOSE', type=type)
                            order = Order(dict()) # clear order
                        else:
                            print(str(datetime.datetime.now()) + ': ' + 'Closing is failed!' + '\n')
                            # db.pop_log(ticker, b_json, status_code, 'CREATION MARKET ORDER', 'ERROR')
                            sys.exit(0)

    flag = False # finished current hour_num


if __name__ == "__main__":
    for i in range(hour_start, hour_finish, 4):
        hour = str(i) if len(str(i)) == 2 else '0' + str(i)
        schedule.every().day.at(hour + ":00:01").do(job)
    schedule.every().day.at(str(hour_finish+1) + ":55:00").do(job)
    while True:
        schedule.run_pending()
        time.sleep(1)