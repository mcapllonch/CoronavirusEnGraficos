"""
Read and understand all the time series
"""
import os
import csv
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from collections import OrderedDict

import utils as utl
import tools as tls
import workspace as ws



def test_analysis():
	""" This is a test data analysis that will be improved later on """

	# Folder where the time series are stored
	folder = '../data/csse_covid_19_data/csse_covid_19_time_series/'

	files = [os.path.join(folder, item) for item in os.listdir(folder) if '.csv' in item]
	# List of time series

	# Dictionary for the data
	data = {}

	# New data with re-arranged information

	for dr in files:
		dr_name = dr.split('/')[-1]
		# Name of the variable (confirmed, deaths or recovered)
		varname = dr_name.split('.')[0].split('-')[-1].lower()
		with open(dr, 'r') as f:
			dataframe = pd.read_csv(dr)
			# dataframe.set_index('Country/Region', inplace=True)
			data[varname] = dataframe

	# Find the date key list
	data_columns = dataframe.columns
	dates = OrderedDict()
	date_indices = OrderedDict()
	previous_keys = []
	for col_name in data_columns:
		try:
			date = utl.str2date(col_name, '%m/%d/%y')
		except Exception as e:
			pass
		else:
			date_key = date.strftime('%d/%m/%Y')
			dates[date_key] = date
			previous_keys.append(col_name)
			date_indices[date_key] = len(dates) - 1
	# Number of dates
	ndates = len(dates)

	# Store dates in ws
	ws.dates = dates

	# Dictionary with the provinces for each country
	provinces = OrderedDict()
	nlocations = dataframe.shape[0]
	for i in range(nlocations):
		dfi = dataframe.loc[i]
		try:
			provinces[dfi['Country/Region']].append(dfi['Province/State'])
		except KeyError:
			provinces[dfi['Country/Region']] = [dfi['Province/State']]


	# Create new dataset that rearranges the data
	columns = ['Country/Region', 'Province/State', 'Lat', 'Long', 'Date Key', 'Date Value', 'confirmed', 'deaths', 'recovered']
	ds_new = pd.DataFrame(index=np.arange(nlocations * ndates), columns=columns)

	# Set up the ds_new from the information in the last dataframe
	# j = 0
	end = -1
	for i in range(nlocations):
		dfi = dataframe.loc[i]
		# print(i)
		start = end + 1
		end = start - 1 + ndates
		ds_new.loc[start:end, 'Country/Region'] = dfi['Country/Region']
		ds_new.loc[start:end, 'Province/State'] = dfi['Province/State']
		ds_new.loc[start:end, 'Lat'] = dfi['Lat']
		ds_new.loc[start:end, 'Long'] = dfi['Long']
		ds_new.loc[start:end, 'Date Key'] = list(dates.keys())
		ds_new.loc[start:end, 'Date Value'] = list(dates.values())
		for variable in ['confirmed', 'recovered', 'deaths']:
			ds_new.loc[start:end, variable] = data[variable].loc[i][previous_keys].tolist()

	# print(ds_new)
	# Show the time series for China
	country = 'Mainland China'

	# Show the time series for the whole world
	ws.dates_keys = list(dates.keys())
	ws.date_indices = date_indices
	ws.dates = dates
	tls.show_world_time_series(ws.dates_keys[0], ws.dates_keys[-1], ds_new)
	tls.show_country('Spain', ['confirmed', 'recovered', 'deaths'], ws.dates_keys[0], ws.dates_keys[-1], ds_new)
	tls.show_country('Colombia', ['confirmed', 'recovered', 'deaths'], ws.dates_keys[0], ws.dates_keys[-1], ds_new)