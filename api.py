# coding: utf-8

import requests
import json
import inspect
import sys

from requests.models import Response
from useful import get_last_work_day_str, get_prev_time_str, get_round_current_time_str, get_current_time_str, get_previous_work_days_str
from market import Account, Ticker
from SECRET import api_token

api_url_base = 'https://api-invest.tinkoff.ru/openapi/'
api_headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer {0}'.format(api_token)}

### MARKET ###

def get_market_search_by_ticker(ticker):
    api_url = '{0}/market/search/by-ticker'.format(api_url_base)
    params = {'ticker': '{0}'.format(ticker)}
    return requests.get(api_url, headers=api_headers, params=params)

def get_market_stocks():
    api_url = '{0}/market/stocks'.format(api_url_base)
    return requests.get(api_url, headers=api_headers)

def get_market_candles(figi, start_time, end_time, interval):
    api_url = '{0}/market/candles'.format(api_url_base)
    params = {'figi': '{0}'.format(figi), 'from': '{0}'.format(start_time), 'to': '{0}'.format(end_time), 'interval': '{0}'.format(interval)}
    r = requests.get(api_url, headers=api_headers, params=params)
    if r.status_code == 200:
        return r.json()["payload"]["candles"]
    else:
        print('Not valid response!')
        print('Response code: {response_code}'.format(response_code=r.status_code))
        current_frame = inspect.currentframe()
        print(current_frame)
        sys.exit(0)

def get_market_search_by_ticker(ticker):
    api_url = '{0}/market/search/by-ticker'.format(api_url_base)
    params = {'ticker': '{0}'.format(ticker)}
    return requests.get(api_url, headers=api_headers, params=params)

def get_market_search_by_figi(figi):
    api_url = '{0}/market/search/by-figi'.format(api_url_base)
    params = {'figi': '{0}'.format(figi)}
    return requests.get(api_url, headers=api_headers, params=params)

### ORDERS ###

def get_orders(broker_account_id):
    api_url = '{0}/orders'.format(api_url_base)
    params = {'brokerAccountId': '{0}'.format(broker_account_id)}
    return requests.get(api_url, headers=api_headers, params=params)

def post_orders_limit_order(figi, broker_account_id, lots, operation, price):
    """
        Создание лимитной заявки
    """
    api_url = '{0}/orders/limit-order'.format(api_url_base)
    params = {'figi': '{0}'.format(figi), 'brokerAccountId': '{0}'.format(broker_account_id)}
    body = {'lots': lots, 'operation': operation, 'price': price}
    return requests.post(api_url, headers=api_headers, params=params, data=json.dumps(body))

def post_orders_market_order(figi, broker_account_id, lots, operation='Buy'):
    """
        Создание рыночной заявки
    """
    api_url = '{0}/orders/market-order'.format(api_url_base)
    params = {'figi': '{0}'.format(figi), 'brokerAccountId': '{0}'.format(broker_account_id)}
    body = {'lots': lots, 'operation': operation}
    return requests.post(api_url, headers=api_headers, params=params, data=json.dumps(body))

def post_orders_cancel(order_id, broker_account_id):
    """
        Отмена заявки
    """
    api_url = '{0}/orders/cancel'.format(api_url_base)
    params = {'orderId': '{0}'.format(order_id), 'brokerAccountId': '{0}'.format(broker_account_id)}
    return requests.post(api_url, headers=api_headers, params=params)

### PORTFOLIO ###

def get_portfolio(broker_account_id):
    api_url = '{0}/portfolio'.format(api_url_base)
    params = {'brokerAccountId': '{0}'.format(broker_account_id)}
    return requests.get(api_url, headers=api_headers, params=params)

def get_portfolio_currencies(broker_account_id):
    api_url = '{0}/portfolio/currencies'.format(api_url_base)
    params = {'brokerAccountId': '{0}'.format(broker_account_id)}
    return requests.get(api_url, headers=api_headers, params=params)

### SANDBOX ###

def post_sandbox_register():
    """
        Регистрация клиента в sandbox
    """
    api_url = '{0}sandbox/sandbox/register'.format(api_url_base)
    print(api_url)
    body = {"brokerAccountType": "Tinkoff"}
    return requests.post(api_url, headers=api_headers, data=json.dumps(body))

def post_sandbox_balance(broker_account_id, balance, currency='RUB'):
    """
        Выставление баланса по валютным позициям
    """
    api_url = '{0}/sandbox/sandbox/currencies/balance'.format(api_url_base)
    params = {'brokerAccountId': broker_account_id}
    body = {"currency": currency, 'balance': balance}
    return requests.post(api_url, headers=api_headers, params=params, data=json.dumps(body))

def post_sandbox_balance(broker_account_id, figi, balance):
    """
        Выставление баланса по инструментным позициям
    """
    api_url = '{0}/sandbox/sandbox/positions/balance'.format(api_url_base)
    params = {'brokerAccountId': broker_account_id}
    body = {"figi": figi, 'balance': balance}
    return requests.post(api_url, headers=api_headers, params=params, data=json.dumps(body))

def post_sandbox_remove(broker_account_id):
    """
        Удаление счета
    """
    api_url = '{0}/sandbox/sandbox/remove'.format(api_url_base)
    params = {'brokerAccountId': broker_account_id}
    return requests.post(api_url, headers=api_headers, params=params)

def post_sandbox_remove(broker_account_id):
    """
        Удаление всех позиций
    """
    api_url = '{0}/sandbox/sandbox/clear'.format(api_url_base)
    params = {'brokerAccountId': broker_account_id}
    return requests.post(api_url, headers=api_headers, params=params)

### USER ###

def get_user_accounts():
    api_url = '{0}/user/accounts'.format(api_url_base)
    return requests.get(api_url, headers=api_headers)

##### Functions from api #####

def get_figi_by_ticker(ticker):
    try:
        r = get_market_search_by_ticker(ticker)
        if r.status_code == 200:
            return r.json()['payload']['instruments'][0]['figi']
        else:
            print('Not valid value!')
            current_frame = inspect.currentframe()
            print(current_frame)
            print('Ticker: {ticker}'.format(ticker))
            sys.exit(0)
    except:
        print('API error!')
        current_frame = inspect.currentframe()
        print(current_frame)
        print('Ticker: {ticker}'.format(ticker))
        sys.exit(0)

def get_ticker(ticker):
    try:
        r = get_market_search_by_ticker(ticker)
        if r.status_code == 200:
            return Ticker(r.json()['payload']['instruments'][0])
        else:
            print('Not valid value!')
            current_frame = inspect.currentframe()
            print(current_frame)
            print('Ticker: {ticker}'.format(ticker))
            sys.exit(0)
    except:
        print('API error!')
        current_frame = inspect.currentframe()
        print(current_frame)
        print('Ticker: {ticker}'.format(ticker))
        sys.exit(0)

def get_broker_account_id():
    try:
        r = get_user_accounts()
        if r.status_code == 200:
            return r.json()['payload']['accounts'][0]['brokerAccountId']
        else:
            print('Not valid response!')
            print('Response code: {response_code}'.format(response_code=r.status_code))
            current_frame = inspect.currentframe()
            print(current_frame)
            sys.exit(0)
    except: 
            print('Not valid value!')
            current_frame = inspect.currentframe()
            print(current_frame)
            sys.exit(0)

def get_account():
    try:
        r = get_user_accounts()
        if r.status_code == 200:
            return Account(r.json()['payload']['accounts'][0])
        else:
            print('Not valid response!')
            print('Response code: {response_code}'.format(response_code=r.status_code))
            current_frame = inspect.currentframe()
            print(current_frame)
            sys.exit(0)
    except:
        print('Not valid value!')
        current_frame = inspect.currentframe()
        print(current_frame)
        sys.exit(0)

def get_balance(currency='RUB'):
    a = get_account()
    b = get_portfolio_currencies(a.broker_account_id)
    if b.status_code == 200:
        l_currencies = b.json()['payload']['currencies']
        for i in range(len(l_currencies)):
            d_cur = l_currencies[i]
            if d_cur['currency'] == currency:
                return d_cur['balance']
    else:
        print('Not valid response!')
        print('Response code: {response_code}'.format(response_code=b.status_code))
        current_frame = inspect.currentframe()
        print(current_frame)
        sys.exit(0)

## ORDERS ##
def get_active_orders():
    broker_account_id = get_broker_account_id()
    r = get_orders(broker_account_id)
    if r.status_code == 200:
        return r.json()["payload"]
    else:
        print('Not valid response!')
        print('Response code: {response_code}'.format(response_code=r.status_code))
        current_frame = inspect.currentframe()
        print(current_frame)
        sys.exit(0)

### LIMIT ORDERS ###

def post_order_limit(figi, lots, operation, price):
    broker_account_id = get_broker_account_id()
    return post_orders_limit_order(figi, broker_account_id, lots, operation, price)

def post_order_limit_buy(figi, lots, price):
    return post_order_limit(figi, lots, 'Buy', price)

def post_order_limit_sell(figi, lots, price):
    return post_order_limit(figi, lots, 'Sell', price)

def post_order_limit_buy_by_ticker(ticker, lots, price):
    figi = get_figi_by_ticker(ticker)
    return post_order_limit(figi, lots, 'Buy', price)

def post_order_limit_sell_by_ticker(ticker, lots, price):
    figi = get_figi_by_ticker(ticker)
    return post_order_limit(figi, lots, 'Sell', price)

### MARKET ORDERS ###

def post_market_order(figi, broker_id, lots, operation='Buy'):
    b = post_orders_market_order(figi, broker_id, lots, operation)
    if b.status_code == 200:
        return b.status_code, b.json()['payload']
    else:
        print('Not valid response!')
        print('Response code: {response_code}'.format(response_code=b.status_code))
        current_frame = inspect.currentframe()
        print(current_frame)
        sys.exit(0)

### CANDLES ###

def get_cur_high(ticker, interval):
    figi = get_figi_by_ticker(ticker)
    end_time = get_current_time_str()
    start_time = get_last_work_day_str()
    b = get_market_candles(figi, start_time, end_time, interval)
    return b[-1]['h']
    
def get_prev_high(ticker, interval):
    """
        Get a high price of previous candle
    """
    figi = get_figi_by_ticker(ticker)
    end_time = get_round_current_time_str(interval)
    start_time = get_last_work_day_str()
    b = get_market_candles(figi, start_time, end_time, interval)
    return b[-1]['h']
    
def get_prev_low(ticker, interval):
    """
        Get a low price of previous candle
    """
    figi = get_figi_by_ticker(ticker)
    end_time = get_round_current_time_str(interval)
    start_time = get_last_work_day_str()
    b = get_market_candles(figi, start_time, end_time, interval)
    return b[-1]['l']
    
def get_prev_open(ticker, interval):
    """
        Get a open price of previous candle
    """
    figi = get_figi_by_ticker(ticker)
    end_time = get_round_current_time_str(interval)
    start_time = get_last_work_day_str()
    b = get_market_candles(figi, start_time, end_time, interval)
    return b[-1]['o']
    
def get_prev_close(ticker, interval):
    """
        Get a close price of previous candle
    """
    figi = get_figi_by_ticker(ticker)
    end_time = get_round_current_time_str(interval)
    start_time = get_last_work_day_str()
    b = get_market_candles(figi, start_time, end_time, interval)
    return b[-1]['c']
    
def get_tickers():
    r = get_market_stocks()
    if r.status_code == 200:
        return r.json()["payload"]["instruments"]
    else:
        print('Not valid response!')
        print('Response code: {response_code}'.format(response_code=r.status_code))
        print(r.json())
        current_frame = inspect.currentframe()
        print(current_frame)
        sys.exit(0)

def get_prev_work_days_candles(ticker, interval):
    figi = get_figi_by_ticker(ticker)
    prev_day_1, prev_day_2 = get_previous_work_days_str() # define previous days strings
    return get_market_candles(figi, prev_day_2, prev_day_1, interval)

def get_hour_interval(ticker, interval, tz):
    l_candles = get_prev_work_days_candles(ticker, interval)
    hour_start = int(l_candles[0]['time'].split('T')[-1].split(':')[0]) + tz
    hour_end = int(l_candles[-1]['time'].split('T')[-1].split(':')[0]) + tz
    return hour_start, hour_end
    
