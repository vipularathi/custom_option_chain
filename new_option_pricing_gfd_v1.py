import pandas as pd
import numpy as np
import os
from common import data_dir, today, logger
import re
from progressbar import ProgressBar as pbar, Percentage, Bar, ETA



formatted_today = today.strftime('%d%m%Y')
# gfd_path = os.path.join(data_dir, f'GFDLNFO_CONTRACT_{formatted_today}.csv') #GFDLNFO_CONTRACT_06092024
gfd_path = os.path.join(data_dir, 'GFDLNFO_CONTRACT_06092024.csv') #GFDLNFO_CONTRACT_06092024

print(gfd_path)
if not os.path.isfile(gfd_path):
    raise RuntimeError('GFD file not found. Please upload the GFD file')

def change_format(gfd_path):
    logger.info("change_format called")
    df = pd.read_csv(gfd_path, index_col=False)

    # Define regular expressions
    pattern_options = r'^(?P<Symbol>[A-Z0-9&-]+)' \
                      r'(?P<Day>\d{2})(?P<Month>[A-Z]{3})(?P<Year>\d{2})' \
                      r'(?P<Strike>\d+(?:\.\d+)?)(?P<Opttype>[A-Z]{2})\.NFO$'

    # Extract details using vectorized string methods
    options_details = df['Ticker'].str.extract(pattern_options)

    # Create 'Expiry' column
    options_details['Expiry'] = options_details['Day'] + '-' + options_details['Month'] + '-' + options_details['Year']

    # Drop the 'Day', 'Month', 'Year' columns if not needed
    options_details.drop(['Day', 'Month', 'Year'], axis=1, inplace=True)

    # Merge the extracted details back into the original DataFrame
    df = df.join(options_details)

    # Write to CSV
    data_file_path = os.path.join(data_dir, f'converted_GFDLNFO_CONTRACT_{formatted_today}.csv')
    logger.info('Writing the data into csv file...')
    df.to_csv(data_file_path, index=False)
    logger.info('GFD file format changed to Data_NSEFO')

    return df


modified_gfd = change_format(gfd_path)
