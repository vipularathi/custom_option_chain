import pandas as pd
import numpy as np
import os
from common import data_dir, today, logger
import re
from progressbar import ProgressBar as pbar, Percentage, Bar, ETA

gfd_columns = ['Date', 'Symbol', 'Strike', 'Expiry', 'Opttype', 
            'Close', 'Open Interest', 'Volume']

gfd_columns_dict = {'Strike':'Strike_Price', 'Expiry':'Expiry_Date',
                'Opttype':'Option_Type', 'Close':'Close_Price', 
                'Open Interest': 'OI'}

formatted_today = today.strftime('%d%m%Y')
gfd_path = os.path.join(data_dir, f'GFDLNFO_CONTRACT_{formatted_today}.csv') #GFDLNFO_CONTRACT_06092024
data_file_path = os.path.join(data_dir, f'converted_GFDLNFO_CONTRACT_{formatted_today}.csv')
if not os.path.isfile(gfd_path):
    logger.info('file found')
    raise RuntimeError('GFD file not found. Please upload the GFD file')


def change_format(gfd_path):
    if not os.path.isfile(data_file_path):
        df = pd.read_csv(gfd_path, index_col=False)
        # ----------------------------------------------------------------
        # Integrating ProgressBar
        # bar = pbar(max_value=100)
        df_rows = len(df)
        # increment = 100/df_rows
        # def update_row(row):
        #     bar.update(min(bar.value + increment, 100))
        #     return pd.Series(extract_ticker_info(row['Ticker']))
        # bar = pbar(widgets=[Percentage(), Bar(), ETA()], max_value=df_rows).start()
        bar = pbar(widgets=[Percentage(), Bar(marker='█', fill=' ', left='[', right=']'), ETA()], max_value=df_rows).start()

        def update_row(row, idx):
            # Update the progress bar with each row processed
            bar.update(idx + 1)
            return pd.Series(extract_ticker_info(row['Ticker']))

        # ----------------------------------------------------------------
        # df[['Symbol', 'Expiry', 'Strike', 'Opttype']] = df.apply(update_row, axis=1)
        df[['Symbol', 'Expiry', 'Strike', 'Opttype']] = [update_row(row, idx) for idx, row in df.iterrows()]
        # new_df = df[df['Time'] != '15:30:59']

        # data_file_path = os.path.join(data_dir, f'converted_GFDLNFO_CONTRACT_{formatted_today}.csv')
        logger.info(f'Writing the data into csv file . . . ')
        df.to_csv(data_file_path, index=False)
        logger.info('GFD file format changed to bhavcopy format')
        bar.finish()
        return df
    else:
        df = pd.read_csv(data_file_path, index_col=False)
        return df

def extract_ticker_info(ticker):
    # pattern = r'([A-Z]+)(\d{2})([A-Z]{3})(\d{2})(\d+(\.\d+)?)([A-Z]{2})\.NFO'
    pattern = r'([A-Z0-9&-]+)(\d{2})([A-Z]{3})(\d{2})(\d+(\.\d+)?)([A-Z]{2})\.NFO'
    match = re.match(pattern, ticker)
    # print('Extracting the GFD data to DATA')
    if match:
        symbol, day, month, year, strike, _, opttype = match.groups()
        expiry = f"{day}-{month}-{year}"
        #         print(symbol, expiry, strike, opttype)
        return symbol, expiry, strike, opttype
    elif 'FUT' in ticker:
        pattern = r'([A-Z0-9&-]+)(\d{2})([A-Z]{3})(\d{2})FUT\.NFO'
        match = re.match(pattern, ticker)
        if match:
            symbol, day, month, year = match.groups()
            expiry = f"{day}-{month.capitalize()}-{year}"
            return symbol, expiry, None, 'XX'

modified_gfd = change_format(gfd_path)
