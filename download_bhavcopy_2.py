import pandas as pd
import os
from datetime import datetime
import requests
import io
import zipfile
from common import data_dir, today, yesterday, logger

def nse_download(date,bhav='fo'):
    bhav_dict={
        'fo':"https://nsearchives.nseindia.com/content/fo/",
        'cm':"https://nsearchives.nseindia.com/content/cm/"
    }
    file_dict={
        'fo':'BhavCopy_NSE_FO_0_0_0_',
        'cm':'BhavCopy_NSE_CM_0_0_0_'
    }
    base_url = bhav_dict[bhav]
    file_url=file_dict[bhav]
    date_str = date.strftime('%Y%m%d').upper()  # Format: 01JAN2024
    print('date_str - ',date_str)

    final_url = f'{base_url}{file_url}{date_str}_F_0000.csv.zip' # Sample - https://nsearchives.nseindia.com/content/fo/BhavCopy_NSE_FO_0_0_0_2024SEP06_F_0000.csv.zip
    print('final_url - ',final_url)

    folder_name = f'{file_url}{date_str}_F_0000'
    print('file_name - ',folder_name)

    # save_dir = data_dir
    # os.makedirs(, exist_ok=True)
    file_path = os.path.join(data_dir, folder_name)
    print('file_path - ',file_path)

    headers = {
            'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.55 Safari/537.36' ,
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8'
            }
    response = requests.get(final_url, headers = headers)
    zip_data = io.BytesIO(response.content)
    with zipfile.ZipFile(zip_data, 'r') as zip_ref:
        zip_ref.extractall(file_path)
    print(f'Bhavcopy downloaded and extracted. File path is {file_path}')
    # print(f'file name is ')
    # a = os.scandir(file_path)
    # for entry in a:
    #     if entry.is_file():
    #         print(f'file name at the specified path is {entry.name}')

    for entry_ in os.listdir(file_path):
        if entry_.endswith('.csv'):
            print(f'file name found using listdir is {entry_}')
        else:
            raise RuntimeError('Bhavcopy not downloaded. Check the time of download.')
    bhav_file = [entry_ for entry_ in os.listdir(file_path) if entry_.endswith('.csv')][0]
    logger.info(bhav_file)
    df = pd.read_csv(os.path.join(file_path, bhav_file), index_col=False)
    return df

bhav_df = nse_download(yesterday)
# print(bhav_df)