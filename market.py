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

class Order:
    ticker = ''
    order_id = ''
    operation = ''
    status = ''
    reject_reason = ''
    message = ''
    requested_lots = 0
    lots = 0
    commission = 0
    currency = ''
    bar_number = 0
    level = 0

    def __init__(self, d, level=0, ticker=''):
        self.ticker = ticker if ticker != None else ''
        self.order_id = d['orderId'] if d.get('orderId') != None else ''
        self.operation = d['operation'] if d.get('operation') != None else ''
        self.status = d['status'] if d.get('status') else ''
        self.reject_reason = d['rejectReason'] if d.get('rejectReason') != None else ''
        self.message = d['message'] if d.get('message') != None else ''
        self.requested_lots = d['requestedLots'] if d.get('requestedLots') != None else 0
        self.lots = d['executedLots'] if d.get('executedLots') != None else 0
        self.commission = d['commission']['value'] if d.get('commission') != None else 0
        self.currency = d['commission']['currency'] if d.get('commission') != None else ''
        self.bar_number = 2
        self.level = level
    
    def __str__(self) -> str:
        return ('Found order: {ticker} {lots}')