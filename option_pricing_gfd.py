import pandas as pd
import numpy as np
import os
from common import data_dir, today, logger
import re
from progressbar import ProgressBar as pbar


bar = pbar(max_value=100)
formatted_today = today.strftime('%d%m%Y')
gfd_path = os.path.join(data_dir, f'GFDLNFO_CONTRACT_{formatted_today}.csv') #GFDLNFO_CONTRACT_06092024
if not os.path.isfile(gfd_path):
    raise RuntimeError('GFD file not found. Please upload the GFD file')

def change_format(gfd_path):
    df = pd.read_csv(gfd_path, index_col=False)
    df[['Symbol', 'Expiry', 'Strike', 'Opttype']] = df['Ticker'].apply(lambda row: pd.Series(extract_ticker_info(row)))
    # new_df = df[df['Time'] != '15:30:59']
    data_file_path = os.path.join(data_dir, f'converted_GFDLNFO_CONTRACT_{formatted_today}.csv')
    df.to_csv(data_file_path, index=False)
    logger.info('GFD file format changed to Data_NSEFO')
    return df

def extract_ticker_info(ticker):
    bar.update(20)
    # pattern = r'([A-Z]+)(\d{2})([A-Z]{3})(\d{2})(\d+(\.\d+)?)([A-Z]{2})\.NFO'
    pattern = r'([A-Z0-9&-]+)(\d{2})([A-Z]{3})(\d{2})(\d+(\.\d+)?)([A-Z]{2})\.NFO'
    match = re.match(pattern, ticker)
    # print('Extracting the GFD data to DATA')
    if match:
        symbol, day, month, year, strike, _, opttype = match.groups()
        expiry = f"{day}-{month.capitalize()}-{year}"
        #         print(symbol, expiry, strike, opttype)
        bar.update(20)
        return symbol, expiry, strike, opttype
    elif 'FUT' in ticker:
        pattern = r'([A-Z0-9&-]+)(\d{2})([A-Z]{3})(\d{2})FUT\.NFO'
        match = re.match(pattern, ticker)
        if match:
            symbol, day, month, year = match.groups()
            expiry = f"{day}-{month.capitalize()}-{year}"
            bar.update(20)
            return symbol, expiry, None, 'XX'

normal_gfd = change_format(gfd_path)
print(normal_gfd)