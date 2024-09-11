# NOT WORKING

import bhavcopy
from datetime import datetime
import os
from common import logger, data_dir
import pandas as pd


# Define working directory, where files would be saved
os.chdir(data_dir)

# Define start and end dates, and convert them into date format
start_date = datetime(2024, 9, 4)
end_date = datetime(2024, 9, 5)

# Define wait time in seconds to avoid getting blocked
wait_time = [1, 2]
#
# # Instantiate bhavcopy class for equities, indices, and derivatives
nse = bhavcopy('indices', start_date, end_date, data_dir, wait_time)
nse.get_data()
#
# nse = bhavcopy(“equities”, start_date, end_date, data_storage, wait_time)
# nse.get_data()
#
# nse = bhavcopy(“derivatives”, start_date, end_date, data_storage, wait_time)
# nse.get_data()