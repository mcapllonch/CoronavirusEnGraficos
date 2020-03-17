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
"""
import os
import numpy as np
import matplotlib.pyplot as plt

import workspace as ws



def get_start_end(start, end):
	""" Get the numerical indices for 'start' and 'end' """
	start_index = ws.date_indices[start]
	end_index = ws.date_indices[end]
	return start_index, end_index

def get_country_date(country, date):
	""" Get the data for a country and a date """
	data = {}
	
	for variable in ['confirmed', 'recovered', 'deaths']:
		data[variable] = df[df['Country/Region'] == country][df['Date'] == date][variable].sum()
	return data

def get_single_time_series(df, variable, start_index, end_index):
	""" Get the time series for 'variable' in 'df', from 'start_index' to 'end_index'.
	Return the dates and values (data) as numpy arrays """
	dates_ = []
	data = []
	for date in ws.dates_keys[start_index:end_index]:
		data.append(df[df['Date Key'] == date][variable].sum())
		dates_.append(ws.dates[date])
	return np.array(dates_), np.array(data)

def show_world_time_series(start, end, df):
	""" Show the time series of the world """
	fig, ax = plt.subplots()
	start_index, end_index = get_start_end(start, end)
	data = {}
	variables = ['confirmed', 'recovered', 'deaths']
	for variable in variables:
		dates_, data[variable] = get_single_time_series(df, variable, start_index, end_index)

	for variable in variables:
		ax.plot(dates_, data[variable], label=variable)

	ax.legend()

	fig.savefig(os.path.join(ws.folders['website/static/images'], 'world.png'))
	# plt.show()

def show_country(country, variables, start, end, df):
	""" Plot the time series of 'variable' from 'start' to 'end', and for 'country' """
	fig, ax = plt.subplots()
	start_index, end_index = get_start_end(start, end)

	# Select the data for 'country'
	df_ = df[df['Country/Region'] == country]

	# 'variables' can be either one string or a list
	if isinstance(variables, list):
		pass
	elif isinstance(variables, str):
		# Turn it into a list
		variables = [variables]
	else:
		print('ERROR: argument \'variables\' needs to be a string or list of strings')
		return

	for variable in variables:
		data = []
		dates_ = []
		dates_, data = get_single_time_series(df_, variable, start_index, end_index)

		# Show time series
		ax.plot(dates_, data, label=variable)

	ax.legend()
	ax.set_title(country)

	fig.savefig(os.path.join(ws.folders['website/static/images'], '%s.png'%country.replace(' ', '_').lower()))
	# plt.show()

