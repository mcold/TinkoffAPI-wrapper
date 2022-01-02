# coding: utf-8

from market import Ticker, Candle, Order
import cx_Oracle
import api
import sys
import inspect
import pin

# TODO: for all procedures make try-except + log-population

dsn = """(DESCRIPTION =
            (ADDRESS_LIST =
            (ADDRESS = (PROTOCOL = TCP)(HOST = 127.0.0.1)(PORT = 1521))
            )
            (CONNECT_DATA =
            (SERVICE_NAME = XEPDB1)
            )
        )"""
user = 'TINKOFF'
password = '15151'


class Actions:
    act_list = list()
    
    def __init__(self):
        with cx_Oracle.connect(user=user, password=password,
                        dsn=dsn,
                        encoding="UTF-8") as connection:
            cursor = connection.cursor()
            for row in cursor.execute("SELECT id, type, ticker, lots, go_in, created, expire_time, do_time FROM ACTION"):
                self.act_list.append(Action(row))

    def __str__(self) -> str:
        v_str = ''
        for act in self.act_list: 
            v_str = v_str + act.__str__()
        return v_str

    def del_act_id(self, id):
        act_list = []
        for act in self.act_list:
            if act.id == id: 
                act.delete()
            else:
                act_list.append(act)
        self.act_list = act_list
    
class Action:

    def __init__(self, tup):
        self.id = tup[0]
        self.type = tup[1]
        self.ticker = tup[2]
        self.lots = tup[3]
        self.go_in = tup[4]
        self.created = tup[5]
        self.expire_time = tup[6]
        self.do_time = tup[7]
        
    def __str__(self) -> str:
        # return """{my_id}""".format(my_id=self.id)
        return """\n---------------------\n id : {my_id}\n type : {type}\n ticker : {ticker}\n lots: {lots}\n go_in : {go_in}\n expire_time : {expire_time}\n created : {created}\n do_time : {do_time}""".format(
            my_id=str(self.id),
            type=str(self.type),
            ticker=str(self.ticker),
            lots=str(self.lots),
            go_in=str(self.go_in),
            expire_time=str(self.expire_time),
            created=str(self.created),
            do_time=str(self.do_time)
            )

    def get_data(self, id):
        with cx_Oracle.connect(user=user, password=password,
                        dsn=dsn,
                        encoding="UTF-8") as connection:
            cursor = connection.cursor()
            for cur in cursor.execute("SELECT id, type, ticker, lots, go_in, created, expire_time, do_time FROM ACTION A WHERE ID = {id}".format(id=id)):
                self.id = cur[0]
                self.type = cur[1]
                self.ticker = cur[2]
                self.lots = cur[3]
                self.go_in = cur[4]
                self.created = cur[4]
                self.expire_time = cur[5]
                self.do_time = cur[6]

    def delete(self):
        with cx_Oracle.connect(user=user, password=password,
                        dsn=dsn,
                        encoding="UTF-8") as connection:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM ACTION WHERE ID = {id}".format(id=self.id))
            connection.commit()
            
### POP ###    
def pop_candle(t = Ticker):
    """
    """

def pop_order(interval, order, status, type='M'):
    """
        Order population
    """
    try:
        statement = "INSERT INTO TINKOFF.ORDERS(TICKER,ORDER_ID,ORDER_TYPE,OPERATION,STATUS,REJECT_REASON,REQUESTED_LOTS,EXECUTED_LOTS,CURRENCY,COMMISSION,OP_STATUS,TIME_INTERVAL) VALUES('{0}', '{1}','{2}','{3}', '{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}')".format(
                    order.ticker
                    , order.order_id
                    , type
                    , order.operation
                    , order.status
                    , order.reject_reason
                    , order.requested_lots
                    , order.lots
                    , order.currency
                    , order.commission
                    , status
                    , interval)
        with cx_Oracle.connect(user=user, password=password,
                            dsn=dsn,
                            encoding="UTF-8") as connection:
            cursor = connection.cursor()
            cursor.execute(statement)
            connection.commit()               
    except:
        
        print('Error in order population')
        print(order.ticker
                    , order.order_id
                    , type
                    , order.operation
                    , order.status
                    , order.reject_reason
                    , order.requested_lots
                    , order.lots
                    , order.currency
                    , order.commission
                    , status
                    , interval)
        current_frame = inspect.currentframe()
        print(current_frame)
        sys.exit(0)

def pop_portfolio():
    """
        Download portfolio positions
    """
    l = api.get_portfolio_list()
    if len(l) > 0:
        with cx_Oracle.connect(user=user, password=password,
                            dsn=dsn,
                            encoding="UTF-8") as connection:
            cursor = connection.cursor()
            cursor.execute('TRUNCATE TABLE PORTFOLIO')
            for pos in l:
                stmt = """INSERT INTO PORTFOLIO(FIGI,
                                               TICKER,
                                               ISIN,
                                               TYPE,
                                               BALANCE,
                                               LOTS,
                                               CURRENCY,
                                               NAME,
                                               AVG_PRICE, 
                                               EXP_YIELD)
                                    VALUES('{figi}',
                                            '{ticker}',
                                            '{isin}',
                                            '{type}',
                                            {balance},
                                            {lots},
                                            '{currency}',
                                            '{name}',
                                            {avg_price},
                                            {exp_yield}
                                            )""".format(
                                            figi=pos['figi']
                                            , ticker=pos['ticker']
                                            , isin=pos.get('isin')
                                            , type=pos['instrumentType']
                                            , balance=pos['balance']
                                            , lots=pos['lots']
                                            , currency=pos['expectedYield']['currency']
                                            , name=pos['name']
                                            , avg_price=pos['averagePositionPrice']['value']
                                            , exp_yield=pos['expectedYield']['value'])
                cursor.execute(stmt)
            connection.commit()

def pop_log(ticker, b_json, code, desc, type='INFO'):
    """
        Log population
    """
    stmt = "INSERT INTO LOGS(TICKER, TYPE, LOG, CODE, DESCRIPTION) VALUES('{ticker}', '{type}', '{json}', {code}, '{description}')".format(ticker=ticker, type=type, json=b_json, code=code, description=desc)
    try:
        with cx_Oracle.connect(user=user, password=password,
                            dsn=dsn,
                            encoding="UTF-8") as connection:
            cursor = connection.cursor()
            cursor.execute(stmt)
            connection.commit()
    except:
        print('Error in log population')
        print(ticker, type, b_json, code, desc)
        current_frame = inspect.currentframe()
        print(current_frame)
        sys.exit(0)

def clear_table(cursor):
    cursor.execute('TRUNCATE TABLE TINKOFF.TICKER')

def pop_ticker(d_ticker, cursor):
    """
        Ticker population into TINKOFF.TICKER   
    """
    try:
        statement = "INSERT INTO TINKOFF.TICKER VALUES('{0}', '{1}', '{2}', {3}, {4}, '{5}', '{6}', '{7}')".format(
                            d_ticker["figi"] if d_ticker.get("figi") != None else 'NULL'
                            , d_ticker["ticker"] if d_ticker.get("ticker") != None else 'NULL'
                            , d_ticker["isin"] if d_ticker.get("isin") != None else 'NULL'
                            , d_ticker["minPriceIncrement"] if d_ticker.get("minPriceIncrement") != None else 'NULL'
                            , d_ticker["lot"] if d_ticker.get("lot") != None else 'NULL'
                            , d_ticker["currency"] if d_ticker.get("currency") != None else 'NULL'
                            , d_ticker["name"].replace("'", '') if d_ticker.get("name") != None else 'NULL'
                            , d_ticker["type"] if d_ticker.get("type") != None else 'NULL')
        cursor.execute(statement)                       
    except:
        print(statement)

def pop_ticker_table():
    """
        Tickers population into TINKOFF.TICKER
    """
    l_instr = api.get_tickers()
    
    with cx_Oracle.connect(user=user, password=password,
                        dsn=dsn,
                        encoding="UTF-8") as connection:
        cursor = connection.cursor()
        clear_table(cursor)
        for i in range(len(l_instr)):
            pop_ticker(l_instr[i], cursor)
        connection.commit()

def pop_ticker_hour_ru():
    """
        Заполняем часы для тикров (только РФ)
    """
    l = list()
    with cx_Oracle.connect(user=user, password=password,
                        dsn=dsn,
                        encoding="UTF-8") as connection:
        cursor = connection.cursor()
        for row in cursor.execute("SELECT ticker FROM TICKER T WHERE t.currency = 'RUB'"):
            l.append(row[0])
        for ticker in l:
            try:
                hour_start, hour_finish = api.get_hour_interval(ticker, 'hour', 3)
                cursor.execute("""
                                UPDATE TICKER
                                SET hour_start = {start}
                                    , hour_finish = {finish}
                                WHERE ticker = '{ticker}'
                            """.format(start = hour_start, finish = hour_finish, ticker=ticker))
            except:
                continue
        connection.commit()

def pop_4h_pin_ru():
    """
        Записываем последние 4часовые пины
    """
    l_ticker = ['AGRO'
        , 'CHMF'
        , 'GAZP'
        , 'GCHE'
        , 'LKOH'
        , 'NLMK'
        , 'PHOR'
        , 'ROSN'
        , 'RTKM'
        , 'SBER'
        , 'SGZH'
        ]
    
    with cx_Oracle.connect(user=user, password=password,
                        dsn=dsn,
                        encoding="UTF-8") as connection:
        cursor = connection.cursor()
        cursor.execute("""
                INSERT INTO PIN_ARCHIVE(TICKER, TYPE, HIGH, LOW)
                SELECT TICKER, TYPE, HIGH, LOW FROM PIN;
        """)
        connection.commit()
        cursor.execute("""TRUNCATE TABLE PIN""")
        for ticker in l_ticker:
            b, high, low = pin.is_prev_4hour_pin(ticker, 'hour')
            if b:
                cursor.execute("""INSERT INTO PIN(TICKER, TYPE, HIGH, LOW) 
                                VALUES('{ticker}', '4H', {high}, {low})""".format(
                                   ticker = ticker
                                   , high = high
                                   , low = low     
                                ))
        connection.commit()
