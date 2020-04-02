"""
Coronavirus en Gráficos: un sitio web donde entender la evolución de la pandemia.
Copyright (C) 2020  Miguel Capllonch Juan

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

Read and understand all the time series
"""
import os
import csv
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from collections import OrderedDict

import utils as utl
import tools as tls
import workspace as ws



def read_time_series_01():
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

	# Show the time series for the whole world
	ws.dates_keys = list(dates.keys())
	ws.date_indices = date_indices
	ws.dates = dates

	# Save the dataframe in the workspace
	ws.data = ds_new

def read_daily_reports_JHU_CSSE():
	""" Read daily reports from John Hopkins University's GitHub repo """	

	# Folder where the time series are stored
	folder = os.path.join(ws.folders['data/covid'], 'csse_covid_19_data/csse_covid_19_daily_reports/')

	files = sorted([os.path.join(folder, item) for item in os.listdir(folder) if '.csv' in item])

	# # Columns that the datasets will have
	# columns = []

	# Dictionary for the data
	data = OrderedDict()

	# Dictionaries for the dates
	dates = OrderedDict()
	date_indices = OrderedDict()

	# New data with re-arranged information

	for dr in files:
		# Get the date from the file name
		date_str = dr.split('/')[-1].split('.')[0]
		# print(date_str, dr)
		# Name of the variable (confirmed, deaths or recovered)
		with open(dr, 'r') as f:
			dataframe = pd.read_csv(dr)
			# Add date
			date = datetime.strptime(date_str, '%m-%d-%Y').date()
			date_key = date.strftime('%d/%m/%Y')
			dataframe['date'] = date
			dataframe['date_key'] = date_key

			# Rename columns
			dataframe.rename(columns=
					{
						'Province/State': 'province_state', 
						'Country/Region': 'country_region', 
						'Last Update': 'last_update', 
						'Lat': 'latitude', 
						'Long_': 'longitude'
					}, 
					inplace=True
				)
			# Lower case all the column names
			dataframe.rename(columns=dict([(s, s.lower()) for s in dataframe.columns]), inplace=True)

			# Save dataframe in dictionary
			data[date_str] = dataframe

			# Save date
			dates[date_key] = date
			date_indices[date_key] = len(dates) - 1

	# Concatenate all the dataframes
	ds_new = pd.concat(data, ignore_index=True).sort_values(by=['country_region', 'province_state'], ignore_index=True)

	# Clean the data

	# Rename certain countries to avoid duplicity
	ds_new.replace('Mainland China', 'China', inplace=True)
	ds_new.replace('US', 'United States of America', inplace=True)
	ds_new.replace('UK', 'United Kingdom', inplace=True)
	ds_new.replace('Korea, South', 'South Korea', inplace=True)
	ds_new.replace('Republic of Korea', 'South Korea', inplace=True)
	ds_new.replace('Iran (Islamic Republic of)', 'Iran', inplace=True)
	ds_new.replace('Hong Kong SAR', 'Hong Kong', inplace=True)
	ds_new.replace('Macao SAR', 'Macao', inplace=True)
	ds_new.replace(' Azerbaijan', 'Azerbaijan', inplace=True)

	# Update 'active' column
	ds_new['closed'] = ds_new['recovered'] + ds_new['deaths']
	ds_new['active'] = ds_new['confirmed'] - ds_new['closed']

	# New dataframe containing countries only (i.e., excluding provinces)
	ds_countries = ds_new.groupby(['country_region', 'date', 'date_key']).sum().reset_index()

	# Show the time series for the whole world
	ws.dates_keys = list(dates.keys())
	ws.date_indices = date_indices
	ws.dates = dates

	# Save the dataframe in the workspace
	ws.data = ds_new
	ws.data_countries_only = ds_countries
