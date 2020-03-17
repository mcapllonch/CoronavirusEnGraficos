"""
Read and understand all the daily reports
"""
import os
import csv
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from collections import OrderedDict



# Folder where the daily reports are stored
folder = '../COVID-19/csse_covid_19_data/csse_covid_19_daily_reports/'
# List of daily reports
dreports = [os.path.join(folder, item) for item in os.listdir(folder) if '.csv' in item]

# Dictionary for the data
data = OrderedDict()

for dr in dreports:
	dr_name = dr.split('/')[-1]
	date = dr_name.split('.')[0]
	with open(dr, 'r') as f:
		data[date] = pd.read_csv(dr)