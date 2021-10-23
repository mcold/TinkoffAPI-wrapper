# coding: utf-8

"""
    Contains classes for marketing
"""

class Account:
    broker_account_type = ''
    broker_account_id = 0

    def __init__(self, d):
        self.broker_account_type = d['brokerAccountType']
        self.broker_account_id = d['brokerAccountId']

class Candle:
    open = 0
    close = 0
    high = 0
    low = 0
    volume = 0
    time = ''
    interval = ''
    figi = ''
    
    def __init__(self, d):
        self.open =d['o']
        self.close =d['c']
        self.high =d['h']
        self.low =d['l']
        self.volume =d['v']
        self.time = d['time']
        self.interval = d['interval']
        self.figi = d['figi']


class Ticker:
    figi = ''
    ticker = ''
    isin = ''
    min_price_increment = 0
    lot = 0
    currency = ''
    name = ''
    type = ''

    def __init__(self, d):
        self.figi = d['figi']
        self.ticker = d['ticker']
        self.isin = d['isin']
        self.min_price_increment = d['minPriceIncrement']
        self.lot = d['lot']
        self.currency = d['currency']
        self.name = d['name']
        self.type = d['type']
