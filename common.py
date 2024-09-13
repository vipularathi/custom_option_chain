import logging
import os
import sys
from datetime import datetime, timedelta
from logging.handlers import TimedRotatingFileHandler
import pandas as pd
import pytz
from dateutil.relativedelta import relativedelta

root_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(root_dir, 'data/')
logs_dir = os.path.join(root_dir, 'logs/')
dirs = [data_dir, logs_dir]
status = [os.makedirs(_dir, exist_ok=True) for _dir in dirs if not os.path.exists(_dir)]

# holidays_23 = ['2023-01-26', '2023-03-07', '2023-03-30', '2023-04-04', '2023-04-07', '2023-04-14', '2023-05-01', '2023-06-29', '2023-08-15', '2023-09-19', '2023-10-02', '2023-10-24', '2023-11-14', '2023-11-27', '2023-12-25']
# holidays_24 = ['2024-01-22', '2024-01-26', '2024-03-08', '2024-03-25', '2024-03-29', '2024-04-11', '2024-04-17', '2024-05-01', '2024-06-17', '2024-07-17', '2024-08-15', '2024-10-02', '2024-11-01', '2024-11-15', '2024-12-25']
# holidays = holidays_23 + holidays_24  # List of date objects
# b_days = pd.bdate_range(start=datetime.now()-relativedelta(months=3), end=datetime.now(), freq='C', weekmask='1111100',
#                         holidays=holidays)
# b_days = b_days.append(pd.DatetimeIndex([pd.Timestamp(year=2024, month=1, day=20)]))
# b_days = b_days[b_days <= datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)].drop_duplicates().sort_values()
# today, yesterday = pd.to_datetime(datetime.now().date()), pd.to_datetime(datetime.now().date() - timedelta(days=1))
today, yesterday = pd.to_datetime(pd.Timestamp(year = 2024, month=9, day=6)), pd.to_datetime(pd.Timestamp(year = 2024, month=9, day=5))
def define_logger():
    # Logging Definitions
    log_lvl = logging.DEBUG
    console_log_lvl = logging.INFO
    _logger = logging.getLogger('arathi')
    # logger.setLevel(log_lvl)
    _logger.setLevel(console_log_lvl)
    log_file = os.path.join(logs_dir, f'logs_arathi_{datetime.now().strftime("%Y%m%d")}.log')
    handler = TimedRotatingFileHandler(log_file, when='D', delay=True)
    handler.setLevel(log_lvl)
    console = logging.StreamHandler(stream=sys.stdout)
    console.setLevel(console_log_lvl)
    # formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')  #NOSONAR
    # formatter = logging.Formatter('%(asctime)s %(levelname)s %(filename)s %(funcName)s %(message)s')
    formatter = logging.Formatter('%(asctime)s %(levelname)s <%(funcName)s> %(message)s')
    handler.setFormatter(formatter)
    console.setFormatter(formatter)
    _logger.addHandler(handler)  # Comment to disable file logs
    _logger.addHandler(console)
    # logger.propagate = False  # Removes AWS Level Logging as it tracks root propagation as well
    return _logger

def calc_business_days(today_date, exp_date, fut:bool=False):
    holidays_23 = ['2023-01-26', '2023-03-07', '2023-03-30', '2023-04-04', '2023-04-07', '2023-04-14', '2023-05-01',
                   '2023-06-29', '2023-08-15', '2023-09-19', '2023-10-02', '2023-10-24', '2023-11-14', '2023-11-27',
                   '2023-12-25']
    holidays_24 = ['2024-01-22', '2024-01-26', '2024-03-08', '2024-03-25', '2024-03-29', '2024-04-11', '2024-04-17',
                   '2024-05-01', '2024-05-20', '2024-06-17', '2024-07-17', '2024-08-15', '2024-10-02', '2024-11-01',
                   '2024-11-15', '2024-12-25']
    holidays = holidays_23 + holidays_24

    holidays = pd.to_datetime(holidays)  # Convert string dates to datetime objects
    excluded_dates = ['2024-01-20', '2024-03-02', '2024-05-04', '2024-05-18', '2024-06-01', '2024-07-06', '2024-08-03',
                      '2024-09-14', '2024-10-05', '2024-11-09', '2024-12-07']
    excluded_dates = pd.to_datetime(excluded_dates)
    holidays = holidays[~holidays.isin(excluded_dates)]

    # if isinstance(today_date, pd.Series) and isinstance(exp_date, pd.Series):
    #     today_date = today_date[0].tolist()
    #     exp_date = exp_date[0].tolist()
    business_day_list = []
    i = 0
    while i < len(today_date[0]):
        logger.info(i)
        if fut:
            t_d = pd.to_datetime(today_date[0].values[i])
            ex_d = pd.to_datetime(exp_date[0].values[i])
        else:
            t_d = pd.to_datetime(today_date[0][i])
            ex_d = pd.to_datetime(exp_date[0][i])
        business_days_left = pd.bdate_range(start=t_d, end=ex_d, holidays=holidays, freq='C', weekmask='1111100')
        actual_bus_days = len(business_days_left) - 1
        business_day_list.append(actual_bus_days)
        i += 1
    return business_day_list

    # for t_d, ex_d in zip(today_date, exp_date):
    #     ex_d = pd.to_datetime(ex_d)
    #     t_d = pd.to_datetime(t_d)
    #     business_days_left = pd.bdate_range(start=t_d, end=ex_d, holidays=holidays, freq='C', weekmask='1111100')
    #     actual_bus_days = len(business_days_left) - 1
    #     business_day_list.append(actual_bus_days)
    # return business_day_list

logger = define_logger()
