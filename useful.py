# coding: utf-8

import datetime
from time import gmtime, strftime

def get_current_time_str():
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%dT%H:%M:%S") + strftime("%z", gmtime()).strip('0') + ":00"

def get_round_current_time(interval):
    if interval == '1min':
        now = datetime.datetime.now().replace(microsecond=0, second=0)
    if interval == '2min':
        now = datetime.datetime.now().replace(microsecond=0, second=0)
        now = now.replace(minute=int(now.minute/2)*2)
    if interval == '3min':
        now = datetime.datetime.now().replace(microsecond=0, second=0)
        now = now.replace(minute=int(now.minute/3)*3)
    if interval == '5min':
        now = datetime.datetime.now().replace(microsecond=0, second=0)
        now = now.replace(minute=int(now.minute/5)*5)        
    if interval == '10min':
        now = datetime.datetime.now().replace(microsecond=0, second=0)
        now = now.replace(minute=int(now.minute/10)*10)
    if interval == '15min':
        now = datetime.datetime.now().replace(microsecond=0, second=0)
        now = now.replace(minute=int(now.minute/15)*15)
    if interval == '30min':
        now = datetime.datetime.now().replace(microsecond=0, second=0)
        now = now.replace(minute=int(now.minute/30)*30)
    if interval == 'hour':
        now = datetime.datetime.now().replace(microsecond=0, second=0, minute=0)
    if interval == 'day':
        now = datetime.datetime.now().replace(microsecond=0, second=0, minute=0, hour=0)
    # TODO: write for week
    return now

def get_round_current_time_str(interval):
    if interval == '1min':
        now = datetime.datetime.now().replace(microsecond=0, second=0)
    if interval == '2min':
        now = datetime.datetime.now().replace(microsecond=0, second=0)
        now = now.replace(minute=int(now.minute/2)*2)
    if interval == '3min':
        now = datetime.datetime.now().replace(microsecond=0, second=0)
        now = now.replace(minute=int(now.minute/3)*3)
    if interval == '5min':
        now = datetime.datetime.now().replace(microsecond=0, second=0)
        now = now.replace(minute=int(now.minute/5)*5)        
    if interval == '10min':
        now = datetime.datetime.now().replace(microsecond=0, second=0)
        now = now.replace(minute=int(now.minute/10)*10)
    if interval == '15min':
        now = datetime.datetime.now().replace(microsecond=0, second=0)
        now = now.replace(minute=int(now.minute/15)*15)
    if interval == '30min':
        now = datetime.datetime.now().replace(microsecond=0, second=0)
        now = now.replace(minute=int(now.minute/30)*30)
    if interval == 'hour':
        now = datetime.datetime.now().replace(microsecond=0, second=0, minute=0)
    if interval == 'day':
        now = datetime.datetime.now().replace(microsecond=0, second=0, minute=0, hour=0)
    # TODO: write for week
    return now.strftime("%Y-%m-%dT%H:%M:%S") + strftime("%z", gmtime()).strip('0') + ":00"

def get_prev_time_str(interval):
    if interval == '1min':
        prev_time = get_round_current_time(interval) - datetime.timedelta(minutes=1)
        return prev_time.strftime("%Y-%m-%dT%H:%M:%S") + strftime("%z", gmtime()).strip('0') + ":00"
    if interval == '2min':
        prev_time = get_round_current_time(interval) - datetime.timedelta(minutes=2)
        return prev_time.strftime("%Y-%m-%dT%H:%M:%S") + strftime("%z", gmtime()).strip('0') + ":00"
    if interval == '3min':
        prev_time = get_round_current_time(interval) - datetime.timedelta(minutes=3)
        return prev_time.strftime("%Y-%m-%dT%H:%M:%S") + strftime("%z", gmtime()).strip('0') + ":00"
    if interval == '5min':
        prev_time = get_round_current_time(interval) - datetime.timedelta(minutes=5)
        return prev_time.strftime("%Y-%m-%dT%H:%M:%S") + strftime("%z", gmtime()).strip('0') + ":00"
    if interval == '10min':
        prev_time = get_round_current_time(interval) - datetime.timedelta(minutes=10)
        return prev_time.strftime("%Y-%m-%dT%H:%M:%S") + strftime("%z", gmtime()).strip('0') + ":00"
    if interval == '15min':
        prev_time = get_round_current_time(interval) - datetime.timedelta(minutes=15)
        return prev_time.strftime("%Y-%m-%dT%H:%M:%S") + strftime("%z", gmtime()).strip('0') + ":00"
    if interval == '30min':
        prev_time = get_round_current_time(interval) - datetime.timedelta(minutes=30)
        return prev_time.strftime("%Y-%m-%dT%H:%M:%S") + strftime("%z", gmtime()).strip('0') + ":00"
    if interval == 'hour':
        prev_time = get_round_current_time(interval) - datetime.timedelta(hours=1)
        return prev_time.strftime("%Y-%m-%dT%H:%M:%S") + strftime("%z", gmtime()).strip('0') + ":00"
    if interval == 'day':
        prev_time = get_round_current_time(interval) - datetime.timedelta(days=1)
        return prev_time.strftime("%Y-%m-%dT%H:%M:%S") + strftime("%z", gmtime()).strip('0') + ":00"
    if interval == 'week':
        prev_time = get_round_current_time(interval) - datetime.timedelta(weeks=1)
        return prev_time.strftime("%Y-%m-%dT%H:%M:%S") + strftime("%z", gmtime()).strip('0') + ":00"


        
def get_prev_work_day(delta = 0, def_day = datetime.datetime.today().replace(microsecond=0, second=0, minute=0, hour=0)):
    new_day = def_day
    while True:
        if datetime.date.weekday(new_day) < 5:
            if delta == 0:
                return new_day
            else:
                return get_prev_work_day(delta - 1, new_day - datetime.timedelta(days=1))
        else:
            new_day = new_day - datetime.timedelta(days=1)
        

def get_last_work_day_str(delta=0):
    date = get_prev_work_day(delta)
    return date.strftime("%Y-%m-%dT%H:%M:%S") + strftime("%z", gmtime()).strip('0') + ":00"

def get_previous_work_days_str():
    """
        Use only for defining intervals
    """
    prev_1 = get_last_work_day_str(1)
    prev_2 = get_last_work_day_str(2)
    return prev_1, prev_2

def get_prev_work_day_str():
    """
        Use for defining pin of last working day
    """
    prev_1 = datetime.datetime.now().replace(microsecond=0, second=0, minute=0, hour=0).strftime("%Y-%m-%dT%H:%M:%S") + strftime("%z", gmtime()).strip('0') + ":00"
    prev_2 = get_last_work_day_str(0)
    return prev_1, prev_2

def get_prev_work_day_str():
    """
        Use for defining pin of current working day
    """
    prev_2 = datetime.datetime.now().replace(microsecond=0, second=0, minute=0).strftime("%Y-%m-%dT%H:%M:%S") + strftime("%z", gmtime()).strip('0') + ":00"
    prev_1 = get_last_work_day_str(1)
    return prev_1, prev_2