# coding: utf-8

from market import Ticker, Candle, Order
import cx_Oracle
import api
import sys
import inspect

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

def pop_candle(t = Ticker):
    """
    """

def pop_order(interval, order, status, type='M'):
    """
        Order population
    """
    try:
        statement = "INSERT INTO TINKOFF.ORDERS VALUES('{0}', '{1}','{2}','{3}', '{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}','{12}')".format(
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