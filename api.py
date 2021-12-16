# coding: utf-8

import requests
import json
import inspect
import sys
import datetime
from time import gmtime, strftime

from requests.models import Response
from useful import get_last_work_day_str, get_prev_work_day_str, get_round_current_time_str, get_current_time_str, get_previous_work_days_str
from market import Account, Ticker, Candle
from SECRET import api_token, sandbox_flag

api_url_base = 'https://api-invest.tinkoff.ru/openapi/'
api_url_base = api_url_base +'sandbox/' if sandbox_flag else api_url_base
api_headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer {0}'.format(api_token)}

### MARKET ###

def get_market_search_by_ticker(ticker):
    api_url = '{0}/market/search/by-ticker'.format(api_url_base)
    params = {'ticker': '{0}'.format(ticker)}
    return requests.get(api_url, headers=api_headers, params=params)

def get_market_stocks():
    api_url = '{0}/market/stocks'.format(api_url_base)
    return requests.get(api_url, headers=api_headers)

def get_bonds():
    api_url = '{0}/market/bonds'.format(api_url_base)
    return requests.get(api_url, headers=api_headers).json()["payload"]["instruments"]

def get_market_candles(figi, start_time, end_time, interval):
    api_url = '{0}/market/candles'.format(api_url_base)
    params = {'figi': '{0}'.format(figi), 'from': '{0}'.format(start_time), 'to': '{0}'.format(end_time), 'interval': '{0}'.format(interval)}
    r = requests.get(api_url, headers=api_headers, params=params)
    if r.status_code == 200:
        return r.json()["payload"]["candles"]
    else:
        print('Not valid response!')
        print('Response code: {response_code}'.format(response_code=r.status_code))
        print(r.json())
        current_frame = inspect.currentframe()
        print(r.json())
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

def get_portfolio_list():
    """
        Get portfolio positions
    """
    broker_id = get_broker_account_id()
    return get_portfolio(broker_id).json()['payload']['positions']

def get_portfolio_currencies(broker_account_id):
    api_url = '{0}/portfolio/currencies'.format(api_url_base)
    params = {'brokerAccountId': '{0}'.format(broker_account_id)}
    return requests.get(api_url, headers=api_headers, params=params)

### SANDBOX ###

def post_sandbox_register():
    """
        Register client in sandbox
    """
    api_url = '{0}/sandbox/register'.format(api_url_base)
    print(api_url)
    body = {"brokerAccountType": "Tinkoff"}
    return requests.post(api_url, headers=api_headers, data=json.dumps(body))

def post_sandbox_balance(broker_account_id, balance, currency='RUB'):
    """
        Выставление баланса по валютным позициям
    """
    api_url = '{0}/sandbox/currencies/balance'.format(api_url_base)
    params = {'brokerAccountId': broker_account_id}
    body = {"currency": currency, 'balance': balance}
    return requests.post(api_url, headers=api_headers, params=params, data=json.dumps(body))

def post_sandbox_instr(broker_account_id, figi, balance):
    """
        Выставление баланса по инструментным позициям
    """
    api_url = '{0}/sandbox/positions/balance'.format(api_url_base)
    params = {'brokerAccountId': broker_account_id}
    body = {"figi": figi, 'balance': balance}
    return requests.post(api_url, headers=api_headers, params=params, data=json.dumps(body))

def post_sandbox_remove(broker_account_id):
    """
        Удаление счета
    """
    api_url = '{0}/sandbox/remove'.format(api_url_base)
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
            print(str(datetime.datetime.now()) + ': ' + 'Not valid value!')
            print(r.json())
            current_frame = inspect.currentframe()
            print(current_frame)
            print('Ticker: {ticker}'.format(ticker))
            sys.exit(0)
    except:
        print(str(datetime.datetime.now()) + ': ' + 'API error!')
        print(r.json())
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
            print(str(datetime.datetime.now()) + ': ' + 'Not valid value!')
            print(r.json())
            current_frame = inspect.currentframe()
            print(current_frame)
            print('Ticker: {ticker}'.format(ticker))
            sys.exit(0)
    except:
        print(str(datetime.datetime.now()) + ': ' + 'API error!')
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
            print(str(datetime.datetime.now()) + ': ' + 'Not valid response!')
            print('Response code: {response_code}'.format(response_code=r.status_code))
            print(r.json())
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
            print(str(datetime.datetime.now()) + ': ' + 'Not valid response!')
            print('Response code: {response_code}'.format(response_code=r.status_code))
            print(r.json())
            current_frame = inspect.currentframe()
            print(current_frame)
            sys.exit(0)
    except:
        print('Not valid value!')
        print(r.json())
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
        print(str(datetime.datetime.now()) + ': ' + 'Not valid response!')
        print('Response code: {response_code}'.format(response_code=b.status_code))
        print(b.json())
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
        print(str(datetime.datetime.now()) + ': ' + 'Not valid response!')
        print('Response code: {response_code}'.format(response_code=r.status_code))
        print(r.json())
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
        print(str(datetime.datetime.now()) + ': ' + 'Not valid response!')
        print('Response code: {response_code}'.format(response_code=b.status_code))
        print(b.json())
        current_frame = inspect.currentframe()
        print(current_frame)
        sys.exit(0)

def post_sell_all_orders():
    """
        Продаем все позиции
    """
    broker_id = get_broker_account_id()
    r = get_portfolio(broker_id)
    l_pos = r.json()['payload']['positions']
    for pos in l_pos:
        status_code, b_json = post_market_order(pos['figi'], broker_id, pos['lots'], 'Sell')
        print(str(status_code) + '\n')
        print(str(b_json) + '\n\n')


### CANDLES ###

#### HOUR ####

def get_cur_high(ticker, interval):
    figi = get_figi_by_ticker(ticker)
    end_time = get_current_time_str()
    start_time = get_last_work_day_str()
    b = get_market_candles(figi, start_time, end_time, interval)
    return b[-1]['h']

def get_cur_candle(ticker, interval):
    figi = get_figi_by_ticker(ticker)
    end_time = get_current_time_str()
    start_time = get_last_work_day_str()
    b = get_market_candles(figi, start_time, end_time, interval)
    return b[-1]

def get_cur_candle_by_figi(figi, interval):
    end_time = get_current_time_str()

    start_time = get_last_work_day_str()
    b = get_market_candles(figi, start_time, end_time, interval)
    # print('start_time:' + start_time + '\n')
    # print('end_time: ' + end_time + '\n')
    # print(b)
    return b[-1]


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
        print(str(datetime.datetime.now()) + ': ' + 'Not valid response!')
        print('Response code: {response_code}'.format(response_code=r.status_code))
        print(r.json())
        current_frame = inspect.currentframe()
        print(current_frame)
        sys.exit(0)

def get_prev_work_days_candles(ticker, interval):
    """
        Use only for defining intervals
    """
    figi = get_figi_by_ticker(ticker)
    prev_day_1, prev_day_2 = get_previous_work_days_str() # define previous days strings
    return get_market_candles(figi, prev_day_2, prev_day_1, interval)

def get_prev_work_day_candles(ticker, interval):
    """
        Use for defining pin of last working day
    """
    figi = get_figi_by_ticker(ticker)
    prev_day_1, prev_day_2 = get_prev_work_day_str() # define previous days strings
    return get_market_candles(figi, prev_day_1, prev_day_2, interval)

def get_hour_interval(ticker, interval, tz):
    l_candles = get_prev_work_days_candles(ticker, interval)
    if len(l_candles) == 0:
        return None, None
    else:
        hour_start = int(l_candles[0]['time'].split('T')[-1].split(':')[0]) + tz
        hour_end = int(l_candles[-1]['time'].split('T')[-1].split(':')[0]) + tz
        return hour_start, hour_end


def get_next_4hour(hour_start, hour_finish, delta):
    cur_hour = datetime.datetime.now().hour
    for hour in range(hour_start, hour_finish, delta):
        if hour > cur_hour:
            return hour

def get_4hour_interval(ticker, interval, tz):
    """
        Получаем время начала 1-ой 4-часовой свечи и последней
    """
    l_4hour_candles = get_prev_work_days_4hour_candles(ticker, interval)
    hour_start = int(l_4hour_candles[0].time.split('T')[-1].split(':')[0]) + tz
    def_day = None
    prev_candle = Candle(dict())
    for l_candle in l_4hour_candles:
        l_day = int(l_candle.time.split('T')[0].split('-')[-1])
        if def_day == None:
            def_day = l_day

        else:
            if def_day != l_day:
                break
        prev_candle = l_candle
    hour_finish = int(prev_candle.time.split('T')[-1].split(':')[0]) + tz
    hour_start = get_next_4hour(hour_start, hour_finish, 4)
    return hour_start, hour_finish

#### 4 HOUR ####

def get_4hour_candles_from_api(l_candles):
    """
        Получаем список объектов свечей из json-списка
    """
    l_4hour = list()
    n = 0
    flag = False
    candle_4 = Candle(dict())
    cur_day = None
    for i in range(len(l_candles)):
        flag = False
        n = n + 1
        if cur_day == None:
            cur_day = int(l_candles[i]['time'].split('T')[0].split('-')[-1])
        candle_day = int(l_candles[i]['time'].split('T')[0].split('-')[-1])
        if candle_day != cur_day: # if day is changed -> add 4h candle and create new one
            l_4hour.append(candle_4)
            n = 1
            cur_day = candle_day
        if n == 1:
            candle_4 = Candle(l_candles[i])
        else:
            next_candle = Candle(l_candles[i])
            candle_4 = candle_4 + next_candle
        if n == 4:
            l_4hour.append(candle_4)
            flag = True
            n = 0
            continue
        if i == len(l_candles)-1 and flag == False:
            l_4hour.append(candle_4)
            break
    return l_4hour


def get_prev_work_days_4hour_candles(ticker, interval):
    l_candles = get_prev_work_day_candles(ticker, interval)
    l_4hour = get_4hour_candles_from_api(l_candles)
    return l_4hour

def get_cur_work_day_4hour_candles(figi, interval):
    """
        Получаем объекты 4часовиков за сегодня
    """
    cur_time = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S") + strftime("%z", gmtime()).strip('0') + ":00"
    start_time = datetime.datetime.today().replace(microsecond=0, second=0, minute=0, hour=0).strftime("%Y-%m-%dT%H:%M:%S") + strftime("%z", gmtime()).strip('0') + ":00"
    l_candles = get_market_candles(figi, start_time, cur_time, interval)
    return get_4hour_candles_from_api(l_candles)

def get_cur_day_4hour_candle(ticker, interval):
    """
        Берем последнюю свечу
    """
    figi = get_figi_by_ticker(ticker)
    l_4hour_candles = get_cur_work_day_4hour_candles(figi, interval)
    return l_4hour_candles[-1]

def get_cur_day_4hour_high(ticker, interval):
    figi = get_figi_by_ticker(ticker)
    l_4hour_candles = get_cur_work_day_4hour_candles(figi, interval)
    return l_4hour_candles[-1].high