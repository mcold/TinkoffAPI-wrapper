# coding: utf-8

import db
import datetime
import time
import sys
import api
import cx_Oracle
from market import Candle, Order


time_delta = 15
commission = 0.05
reserve = 200
broker_id = api.get_broker_account_id()
level = 0
start_4hour_order = None

def count_lots(cur_level, t_ticker):
    global commission, reserve
    balance = api.get_balance()
    lots = int(balance / (cur_level * t_ticker.lot))
    amount = lots*cur_level + lots*cur_level * commission + reserve
    if balance > amount:
        return lots
    else:
        return None

def get_cur_4hour():
    cur_hour = datetime.datetime.now().hour
    for hour in range(22, 6, -4):
        if hour <= cur_hour:
            return hour

def thread():
    global broker_id, time_delta, level, start_4hour_order
    order = Order(dict())
    pop_4h_flag = False
    l_pins = list()
    while datetime.datetime.now().hour != 23:
        time.sleep(time_delta)
        cur_hour = datetime.datetime.now().hour
        if cur_hour < 10:
            print("It's too early!")
            continue
        # reload 4hour pins
        if order == Order(dict()): # if no order
            if cur_hour in (10, 14, 18) and not pop_4h_flag:
                db.pop_4h_pin_ru()
                l_pins = []
                with cx_Oracle.connect(user=db.user, password=db.password,
                            dsn=db.dsn,
                            encoding="UTF-8") as connection:
                    cursor = connection.cursor()
                    for row in cursor.execute("""
                                            SELECT ticker
                                                , high
                                                , low
                                                FROM pin
                                            """):
                        l_pins.append(row)
                pop_4h_flag = True
            
            if cur_hour in (11, 15, 19) and pop_4h_flag:
                pop_4h_flag = False
            
            for tup_pin in l_pins:
                ticker = tup_pin[0]
                high = tup_pin[1]
                low = tup_pin[2]
                candle = Candle(api.get_cur_candle(ticker, '1min'))
                if candle.high > high:
                    print('-'*40)
                    print('Pin is bitten! high')
                    print(ticker)
                    print('Current 1min bar:\n')
                    print(candle)
                    print('-'*40)
                    lots = count_lots(candle.close, api.get_ticker(ticker))
                    if lots != None:
                        status_code, b_json = api.post_market_order(api.get_figi_by_ticker(ticker), broker_id, lots, 'Buy')
                        if status_code == 200:
                            print('Bought: ' + str(datetime.datetime.now()) + ' lots: ' + str(lots))
                            order = Order(b_json, candle.high, ticker)
                            db.pop_order('4h', order, 'OPEN')
                            level = candle.high
                            start_4hour_order = get_cur_4hour() # set start of order
                            continue
                        else:
                            print('Tried to buy\n')
                            print(str(status_code) + '\n')
                            print(str(b_json) + '\n')
                            sys.exit(0)
                    else:
                        print("I'd like to buy, but I can't\n\n")
                        
                if candle.low < low:
                    print('-'*40)
                    print('Pin is bitten! low')
                    print(ticker)
                    print('Current 1min bar:\n')
                    print(candle)
                    print('-'*40)
                    lots = count_lots(candle.close, api.get_ticker(ticker))
                    if lots != None:
                        status_code, b_json = api.post_market_order(api.get_figi_by_ticker(ticker), broker_id, lots, 'Sell')
                        if status_code == 200:
                            print('Sold: ' + str(datetime.datetime.now()) + ' lots: ' + str(lots) + ' ' + ticker)
                            order = Order(b_json, candle.high, ticker)
                            db.pop_order('4h', order, 'OPEN')
                            level = candle.low
                            start_4hour_order = get_cur_4hour() # set start of order
                            continue
                        else:
                            print('Tried to sell\n')
                            print(str(status_code) + '\n')
                            print(str(b_json) + '\n')
                            sys.exit(0)
                    else:
                        print("I'd like to buy, but I can't\n\n")                                                    
        else: # order exists
            print('-'*40)
            print('Order exists!')
            print(ticker)
            print(order)
            candle = Candle(api.get_cur_candle(order.ticker, '1min'))
            print('Current 1min bar:\n')
            print(candle)
            print('-'*40)
            # close partly if it's time
            if datetime.datetime.now().hour == start_4hour_order + 4:
                print('Closing partly')
                if order.operation == 'Buy':
                    close_lots = int(order.lots/2)
                    status_code, b_json = api.post_market_order(api.get_figi_by_ticker(order.ticker), broker_id, close_lots, 'Sell')
                    if status_code == 200:
                        close_lots = b_json['executedLots']
                        print('Sold: {ticker}'.format(ticker=order.ticker) + ' ' + str(datetime.datetime.now()) + ' lots: ' + str(close_lots))
                        order.lots = order.lots - close_lots
                    else:
                        print('Tried to sell\n')
                        print(str(status_code) + '\n')
                        print(str(b_json) + '\n')
                        sys.exit(0)
                if order.operation == 'Sell':
                    close_lots = int(order.lots/2)
                    status_code, b_json = api.post_market_order(api.get_figi_by_ticker(order.ticker), broker_id, close_lots, 'Buy')
                    if status_code == 200:
                        closed_lots = b_json['executedLots']
                        print('Bought {ticker}: '.format(ticker=order.ticker) + ' ' + str(datetime.datetime.now()) + ' lots: ' + str(closed_lots))
                        order.lots = order.lots - closed_lots
                    else:
                        print('Tried to buy\n')
                        print(str(status_code) + '\n')
                        print(str(b_json) + '\n')
                        sys.exit(0)

            # close order if it's time
            if datetime.datetime.now().hour == start_4hour_order + 8:
                print('Closing order')
                print(order)
                if order.operation == 'Buy':
                    status_code, b_json = api.post_market_order(api.get_figi_by_ticker(order.ticker), broker_id, order.lots, 'Sell')
                    if status_code == 200:
                        closed_lots = b_json['executedLots']
                        print('Sold: {ticker}'.format(ticker=order.ticker) + ' ' + str(datetime.datetime.now()) + ' lots: ' + str(closed_lots))
                        order = Order(dict()) # clear order
                    else:
                        print('Tried to sell\n')
                        print(str(status_code) + '\n')
                        print(str(b_json) + '\n')
                        sys.exit(0)
                if order.operation == 'Sell':
                    status_code, b_json = api.post_market_order(api.get_figi_by_ticker(order.ticker), broker_id, order.lots, 'Buy')
                    if status_code == 200:
                        closed_lots = b_json['executedLots']
                        print('Bought {ticker}: '.format(ticker=order.ticker) + str(datetime.datetime.now()) + ' lots: ' + str(closed_lots))
                        order = Order(dict()) # clear order
                    else:
                        print('Tried to buy\n')
                        print(str(status_code) + '\n')
                        print(str(b_json) + '\n')
                        sys.exit(0)
            # if price is out
            if order.operation == 'Buy' and candle.close <= level:
                status_code, b_json = api.post_market_order(api.get_figi_by_ticker(order.ticker), broker_id, order.lots, 'Sell')
                if status_code == 200:
                    closed_lots = b_json['executedLots']
                    print('Sold: {ticker}'.format(ticker=order.ticker) + ' ' + str(datetime.datetime.now()) + ' lots: ' + str(closed_lots))
                    order = Order(dict()) # clear order
                else:
                    print('Tried to sell\n')
                    print(str(status_code) + '\n')
                    print(str(b_json) + '\n')
                    sys.exit(0)
            if order.operation == 'Sell' and candle.close >= level:
                status_code, b_json = api.post_market_order(api.get_figi_by_ticker(order.ticker), broker_id, order.lots, 'Buy')
                if status_code == 200:
                    closed_lots = b_json['executedLots']
                    print('Bought {ticker}: '.format(ticker=order.ticker) + str(datetime.datetime.now()) + ' lots: ' + str(closed_lots))
                    order = Order(dict()) # clear order
                else:
                    print('Tried to buy\n')
                    print(str(status_code) + '\n')
                    print(str(b_json) + '\n')
                    sys.exit(0)
            else:
                continue
        
    if order == Order(dict()): # close order if exists
        if order.operation == 'Buy':
            status_code, b_json = api.post_market_order(api.get_figi_by_ticker(order.ticker), broker_id, order.lots, 'Sell')
            if status_code == 200:
                closed_lots = b_json['executedLots']
                print('Sold: {ticker}'.format(ticker=order.ticker) + ' ' + str(datetime.datetime.now()) + ' lots: ' + str(closed_lots))
                order = Order(dict()) # clear order
            else:
                print('Tried to sell\n')
                print(str(status_code) + '\n')
                print(str(b_json) + '\n')
                sys.exit(0)
        if order.operation == 'Sell':
            status_code, b_json = api.post_market_order(api.get_figi_by_ticker(order.ticker), broker_id, order.lots, 'Buy')
            if status_code == 200:
                print('Bought {ticker}: '.format(ticker=order.ticker) + str(datetime.datetime.now()) + ' lots: ' + str(lots))
                order = Order(dict()) # clear order
            else:
                print('Tried to buy\n')
                print(str(status_code) + '\n')
                print(str(b_json) + '\n')
                sys.exit(0)

if __name__ == "__main__":
    db.pop_4h_pin_ru() # if start not from morning
    thread()