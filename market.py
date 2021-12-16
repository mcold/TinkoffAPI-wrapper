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
        self.open =d['o'] if d.get('o') != None else 0
        self.close =d['c'] if d.get('c') != None else 0
        self.high =d['h'] if d.get('h') != None else 0
        self.low =d['l'] if d.get('l') != None else 0
        self.volume =d['v'] if d.get('v') != None else 0
        self.time = d['time'] if d.get('time') != None else ''
        self.interval = d['interval'] if d.get('interval') != None else ''
        self.figi = d['figi'] if d.get('figi') != None else ''
    
    def __add__(self, other):
        self.close = other.close
        if self.high < other.high:
            self.high = other.high
        if self.low > other.low:
            self.low = other.low
        self.volume = self.volume + other.volume
        return self

    def __str__(self):
        # return '{0}'.format(self.open)#: {figi}'.format(self.figi)
        return (' figi: {0} \n open: {1} \n close: {2} \n high: {3} \n low: {4} \n volume: {5} \n time: {6} \n interval: {7} \n\n'.format(self.figi, str(self.open), str(self.close), str(self.high), str(self.low), str(self.volume), str(self.time), self.interval))

class Ticker:
    figi = None
    ticker = None
    isin = None
    min_price_increment = None
    lot = None
    currency = None
    name = None
    type = None

    def __init__(self, d):
        self.figi = d['figi'] if d.get('figi') != None else ''
        self.ticker = d['ticker'] if d.get('ticker') != None else ''
        self.isin = d['isin'] if d.get('isin') != None else ''
        self.min_price_increment = d['minPriceIncrement'] if d.get('minPriceIncrement') != None else 0
        self.lot = d['lot'] if d.get('lot') != None else 0
        self.currency = d['currency'] if d.get('currency') != None else ''
        self.name = d['name'] if d.get('name') != None else ''
        self.type = d['type'] if d.get('type') != None else ''

    def __str__(self) -> str:
        return """\n\t\t{ticker_str}{ticker}
                {figi_str}{figi}
                {isin_str}{isin}
                {name_str}{name}
                {min_str}{min_price_increment}
                {lot_str}{lot}
                {cur_str}{currency}
                {type_str}{type}\n\n""".format(
                    ticker_str='ticker:'.ljust(25, ' '),
                    ticker=self.ticker, 
                    figi_str='figi:'.ljust(25, ' '),
                    figi=self.figi, 
                    isin_str='sin:'.ljust(25, ' '),
                    isin=self.isin, 
                    name_str='name:'.ljust(25, ' '),
                    name=self.name, 
                    min_str='price_increment:'.ljust(25, ' '),
                    min_price_increment=self.min_price_increment, 
                    lot_str='lot:'.ljust(25, ' '),
                    lot=self.lot, 
                    cur_str='currency:'.ljust(25, ' '),
                    currency=self.currency, 
                    type_str='type:'.ljust(25, ' '),
                    type=self.type)
        

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
        return ('Found order: {ticker} {lots}'.format(ticker=self.ticker, lots=self.lots))

    def __eq__(self, other):
        if self.ticker == other.ticker and self.order_id == other.order_id and self.operation == other.operation and self.lots == other.lots:
            return True
        else:
            return False

    