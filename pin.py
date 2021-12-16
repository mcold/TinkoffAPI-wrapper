# coding: utf-8

import api
import useful
import sys
import inspect
import datetime
from market import Candle

def is_pin(cur_candle, prev_candle):
    if cur_candle.high <= prev_candle.high and cur_candle.low >= prev_candle.low:
        return True
    else:
        return False

def is_bitten(cur_candle, next_candle):
    if next_candle.high > cur_candle.high:
        return True
    else:
        return False

def is_prev_hour_of_day_pin(ticker):
    try:
        figi = api.get_figi_by_ticker(ticker)
        cur_time_str = useful.get_round_current_time_str('day')
        prev_time_str = useful.get_prev_time_str('day')
        l_candles = api.get_market_candles(figi, prev_time_str, cur_time_str, 'hour')
        last_candle = Candle(l_candles[-1])
        prev_candle = Candle(l_candles[-2])
        return is_pin(last_candle, prev_candle), last_candle.high
    except:
        print(str(datetime.datetime.now()) + ': ' + 'Error in finding previous hour pin!')
        current_frame = inspect.currentframe()
        print(current_frame)
        print('Ticker: {ticker}'.format(ticker))
        sys.exit(0)

def is_prev_hour_pin(ticker):
    try:
        figi = api.get_figi_by_ticker(ticker)
        cur_time_str = useful.get_round_current_time_str('hour')
        prev_time_str = useful.get_prev_time_str('day')
        l_candles = api.get_market_candles(figi, prev_time_str, cur_time_str, 'hour')
        last_candle = Candle(l_candles[-1])
        prev_candle = Candle(l_candles[-2])
        return is_pin(last_candle, prev_candle), last_candle.high
    except:
        print(str(datetime.datetime.now()) + ': ' + 'Error in finding previous hour pin!')
        current_frame = inspect.currentframe()
        print(current_frame)
        print('Ticker: {ticker}'.format(ticker))
        sys.exit(0)

def is_prev_4hour_pin(ticker, interval):
    l_candles = api.get_prev_work_days_4hour_candles(ticker, interval)
    candle_last = l_candles[-1]
    candle_prev = l_candles[-2]
    if candle_last.high <= candle_prev.high and candle_last.low >= candle_prev.low:
        return True, candle_last.high, candle_last.low
    else:
        return False, None, None

def is_def_hour_is_pin(ticker, prev_time_str):
    try:
        figi = api.get_figi_by_ticker(ticker)
        cur_time_str = useful.get_round_current_time_str('hour')
        l_candles = api.get_market_candles(figi, prev_time_str, cur_time_str, 'hour')
        last_candle = Candle(l_candles[-1])
        prev_candle = Candle(l_candles[-2])
        return is_pin(last_candle, prev_candle), last_candle.high
    except:
        print(str(datetime.datetime.now()) + ': ' + 'Error in finding previous hour pin!')
        current_frame = inspect.currentframe()
        print(current_frame)
        print('Ticker: {ticker}'.format(ticker))
        print("Previous time: {prev_time}".format(prev_time=prev_time_str))
        sys.exit(0)

def pin_count(pin, next_2_candle, amount, lot):
    delta = next_2_candle.close - pin.high
    lots = amount / (lot * pin.high)
    return lots*delta

# TODO: change timezone arguments
def pin_candles_count(ticker, amount=100000, start_time='2021-01-01T00:00:00+03:00', end_time='2022-01-01T00:00:00+03:00', interval='hour'):
    """
        Count pinbar productivity
        1 lot
        amount: amount of money
    """
    t = api.get_ticker(ticker)
    l_candles = api.get_market_candles(t.figi, start_time, end_time, interval)
    sum = 0
    for i in range(1, len(l_candles)-2):
        cur_candle = Candle(l_candles[i])
        prev_candle = Candle(l_candles[i-1])
        next_candle = Candle(l_candles[i+1])
        next_2_candle = Candle(l_candles[i+2])
        if is_pin(cur_candle, prev_candle) and is_bitten(cur_candle, next_candle):
            if i + 1 + 2 <= len(l_candles):
                sum = sum + pin_count(cur_candle, next_2_candle)
        else:
            continue

if __name__ == "__main__":
    print(pin_candles_count('SBER'))