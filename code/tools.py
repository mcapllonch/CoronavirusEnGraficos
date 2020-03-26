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
import json
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from bokeh.plotting import figure, output_file, show, save
from bokeh.models import Slider, HoverTool, Range1d, NumeralTickFormatter, DatetimeTickFormatter, GeoJSONDataSource, LinearColorMapper, LogColorMapper, ColorBar, BasicTicker, LogTicker
from bokeh.io import show, output_file, curdoc
from bokeh.palettes import brewer
from bokeh.layouts import widgetbox, row, column

import workspace as ws
import utils as utl


plt.style.use('format001.mplstyle')
# plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y'))


def cases_per_day(x):
	""" Compute the new cases per day of x """
	return x[1:] - x[:-1]

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
	for date in ws.dates_keys[start_index:end_index + 1]:
		data.append(df[df['date_key'] == date][variable].sum())
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

	# Existing cases
	data['resolved'] = data['recovered'] + data['deaths']
	data['existing'] = data['confirmed'] - data['resolved']

	variables = variables + ['existing']
	for variable in variables:
		ax.plot(dates_, data[variable], c=ws.varcolors[variable], label=variable)

	# Date ticks
	months = mdates.MonthLocator()  # every month
	days = mdates.DayLocator()  # every month
	month_fmt = mdates.DateFormatter('%m')
	# format the ticks
	if False:
		ax.xaxis.set_major_locator(months)
		ax.xaxis.set_major_formatter(month_fmt)
		ax.xaxis.set_minor_locator(days)
	plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y'))
	utl.configure_axes(ax, xlims=(dates_[0], dates_[-1]), xlabel='Date', ylabel='Cases')
	ax.set_ylim(0, data['confirmed'].max())

	fig.savefig(os.path.join(ws.folders['website/static/images'], 'world.png'), bbox_inches='tight')
	# plt.show()

def show_cases_per_day(start, end, df):
	""" Show the time series of the growth rate of the virus as new cases per day """
	fig, ax = plt.subplots()
	start_index, end_index = get_start_end(start, end)
	data = {}
	variables = ['confirmed', 'recovered', 'deaths']
	for variable in variables:
		dates_, x = get_single_time_series(df, variable, start_index, end_index)
		data[variable] = cases_per_day(x)

		ax.plot(dates_[1:], data[variable], 'o-', c=ws.varcolors[variable], label=variable)

	# Second graph: only recovered and deaths, in log scale
	fig2, ax2 = plt.subplots()
	ax2.plot(dates_[1:], data['recovered'], 'o-', c=ws.varcolors['recovered'], label='recovered')
	ax2.plot(dates_[1:], data['deaths'], 'o-', c=ws.varcolors['deaths'], label='deaths')
	ax2.set_yscale('log')
	utl.configure_axes(ax2, xlims=(dates_[1], dates_[-1]), xlabel='Date', ylabel='New Cases per Day')

	# Date ticks
	months = mdates.MonthLocator()  # every month
	days = mdates.DayLocator()  # every month
	month_fmt = mdates.DateFormatter('%m')
	plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y'))
	utl.configure_axes(ax, xlims=(dates_[1], dates_[-1]), xlabel='Date', ylabel='New Cases per Day')

	fig.savefig(os.path.join(ws.folders['website/static/images'], 'cases_per_day.png'), bbox_inches='tight')
	# plt.show()

def show_country(country, variables, start, end, df, fig=None, ax=None):
	""" Plot the time series of 'variable' from 'start' to 'end', and for 'country' """
	if fig is None and ax is None:
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
		ax.plot(dates_, data, c=ws.varcolors[variable], label=variable)

	utl.configure_axes(ax, xlims=(dates_[0], dates_[-1]), xlabel='Date', ylabel='Cases')
	ax.set_title(country)
	# ax.set_yscale('log')

	fig.savefig(os.path.join(ws.folders['website/static/images'], '%s_nolog.png'%country.replace(' ', '_').lower()), bbox_inches='tight')
	# plt.show()

def show_world_death_ratio_I(start, end, df, country='world'):
	""" Show the time series of the death ratios """

	fig, ax = plt.subplots()
	start_index, end_index = get_start_end(start, end)
	data = {}
	variables = ['confirmed', 'recovered', 'deaths']
	for variable in variables:
		dates_, data[variable] = get_single_time_series(df, variable, start_index, end_index)

	# Variable 'death ratio'
	data['resolved'] = data['recovered'] + data['deaths']
	data['deaths over total'] = data['deaths'] / data['confirmed']
	data['deaths over resolved'] = data['deaths'] / data['resolved']

	ax.plot(dates_, data['deaths over total'], c=ws.varcolors['deaths'], ls='-', label='deaths over total')
	ax.plot(dates_, data['deaths over resolved'], c=ws.varcolors['deaths'], ls='--', label='deaths over closed cases')

	# Date ticks
	months = mdates.MonthLocator()  # every month
	days = mdates.DayLocator()  # every month
	month_fmt = mdates.DateFormatter('%m')
	# format the ticks
	if False:
		ax.xaxis.set_major_locator(months)
		ax.xaxis.set_major_formatter(month_fmt)
		ax.xaxis.set_minor_locator(days)
	plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y'))
	utl.configure_axes(ax, xlims=(dates_[0], dates_[-1]), xlabel='Date', ylabel='Ratios')

	fig.savefig(os.path.join(ws.folders['website/static/images'], 'world_death_ratio_I.png'), bbox_inches='tight')
	# plt.show()

def show_balance_per_day(start, end, df):
	""" Show the time series of the world: balance per day """

	fig, ax = plt.subplots()
	fig2, ax2 = plt.subplots()
	start_index, end_index = get_start_end(start, end)
	data = {}
	variables = ['confirmed', 'recovered', 'deaths']
	for variable in variables:
		dates_, x = get_single_time_series(df, variable, start_index, end_index)
		data[variable] = cases_per_day(x)

	data['resolved'] = data['recovered'] + data['deaths']
	data['balance'] = data['confirmed'] - data['resolved']
	for variable in ['confirmed', 'resolved', 'balance']:
		ax.plot(dates_[1:], data[variable], 'o-', c=ws.varcolors[variable], label=variable)
	ax.plot(dates_[1:], data['confirmed'], 'o-', c=ws.varcolors['confirmed'], label='confirmed')
	ax.plot(dates_[1:], data['resolved'], 'o-', c=ws.varcolors['resolved'], label='resolved')

	# Date ticks
	months = mdates.MonthLocator()  # every month
	days = mdates.DayLocator()  # every month
	month_fmt = mdates.DateFormatter('%m')
	plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y'))

	utl.configure_axes(ax, xlims=(dates_[1], dates_[-1]),
		xlabel='Date', ylabel='New Cases per Day')
	ax.axhline(y=0, ls='--', c='gray')

	utl.configure_axes(ax2, xlims=(dates_[1], dates_[-1]),
		xlabel='Date', ylabel='New Cases per Day')
	ax2.axhline(y=0, ls='--', c='gray')
	ax2.set_ylim(0, data['confirmed'].max())

	fig.savefig(os.path.join(ws.folders['website/static/images'], 'balance_per_day.png'), bbox_inches='tight')
	fig2.savefig(os.path.join(ws.folders['website/static/images'], 'balance_per_day_cleaner.png'), bbox_inches='tight')
	# plt.show()

def stackplot(start, end, df):
	""" Row-stack graph of the infection """

	# Over confirmed

	# Absolute
	fig, ax = plt.subplots()
	start_index, end_index = get_start_end(start, end)
	data = {}
	variables = ['confirmed', 'recovered', 'deaths']
	for variable in variables:
		dates_, data[variable] = get_single_time_series(df, variable, start_index, end_index)
	data['resolved'] = data['recovered'] + data['deaths']
	data['existing'] = data['confirmed'] - data['resolved']
	wanted_variables = ('deaths', 'recovered', 'existing')
	values = np.row_stack(
			np.array([data[k] for k in wanted_variables])
		)
	ax.stackplot(
			dates_, 
			values, 
			colors=[ws.varcolors[k] for k in wanted_variables], 
			labels=wanted_variables, 
		)
	ax.plot(dates_, data['confirmed'], c=ws.varcolors['confirmed'], ls='-', label='confirmed')
	utl.configure_axes(ax, xlims=(dates_[0], dates_[-1]), xlabel='Date', ylabel='Cases', title='Evolution over Confirmed')
	fig.savefig(os.path.join(ws.folders['website/static/images'], 'stackplot.png'), bbox_inches='tight')

	# Percentage
	fig2, ax2 = plt.subplots()
	start_index, end_index = get_start_end(start, end)
	data = {}
	variables = ['confirmed', 'recovered', 'deaths']
	for variable in variables:
		dates_, data[variable] = get_single_time_series(df, variable, start_index, end_index)
	data['resolved'] = data['recovered'] + data['deaths']
	data['existing'] = data['confirmed'] - data['resolved']
	values = np.row_stack(
			np.array([data['deaths'], data['recovered'], data['existing']]) * (100. / data['confirmed'])
		)
	ax2.stackplot(
			dates_, 
			values, 
			colors=[ws.varcolors[k] for k in wanted_variables], 
			labels=wanted_variables, 
		)
	ax2.set_ylim(0, 100)
	utl.configure_axes(ax2, xlims=(dates_[0], dates_[-1]), xlabel='Date', ylabel='Cases (%)', title='Evolution over Confirmed')
	fig2.savefig(os.path.join(ws.folders['website/static/images'], 'stackplot_percentages.png'), bbox_inches='tight')

	# plt.show()

def analysis_01(start, end, df):
	""" Exclusivo para Heath Cube """

	countries = ['Spain', 'Italy', 'Colombia']

	fig, ax = plt.subplots()

	colors = {
		'Spain': 'k', 
		'Colombia': 'r', 
		'Italy': 'b'
	}

	linewidths = {
		'Spain': 1, 
		'Colombia': 2, 
		'Italy': 1
	}

	start_by_country = {
		'Spain': ws.dates_keys[10], 
		'Colombia': ws.dates_keys[44], 
		'Italy': ws.dates_keys[9]
	}

	for country in countries:

		start = start_by_country[country]
		start_index, end_index = get_start_end(start, end)

		data = {}
		variables = ['confirmed']

		daysmin = 1e99
		daysmax = -1e99

		for variable in variables:
			dates_, x = get_single_time_series(df[df['Country/Region'] == country], variable, start_index, end_index)
			data[variable] = cases_per_day(x)

			days = np.arange(len(dates_) - 1)
			daysmin = min(days.min(), daysmin)
			daysmax = max(days.max(), daysmax)

			ax.plot(days, data[variable], 'o-', lw=linewidths[country], c=colors[country], alpha=0.5, label=country)


	# Date ticks
	months = mdates.MonthLocator()  # every month
	days = mdates.DayLocator()  # every month
	month_fmt = mdates.DateFormatter('%m')

	utl.configure_axes(ax, xlims=(daysmin, 20), xlabel='Days after First Case', ylabel='New Cases per Day')
	ax.set_ylim(0, 40)
	ax.set_title('Growth Rate (New Cases per Day)')

	fig.savefig(os.path.join(ws.folders['website/static/images'], 'ritmos_01.png'), bbox_inches='tight')
	# plt.show()

def analysis_02(start, end, df):
	""" Exclusivo para Heath Cube """

	countries = ['Spain', 'Italy', 'Colombia']

	fig, ax = plt.subplots()
	fig2, ax2 = plt.subplots()

	colors = {
		'Spain': 'k', 
		'Colombia': 'r', 
		'Italy': 'b'
	}

	linewidths = {
		'Spain': 1, 
		'Colombia': 2, 
		'Italy': 1
	}

	start_by_country12 = {
		'Spain': ws.dates_keys[10], 
		'Colombia': ws.dates_keys[44], 
		'Italy': ws.dates_keys[9]
	}

	for country in countries:

		start = start_by_country12[country]
		start_index, end_index = get_start_end(start, end)

		data = {}
		variables = ['confirmed', 'deaths', 'recovered']

		daysmin = 1e99
		daysmax = -1e99

		for variable in variables:
			dates_, x = get_single_time_series(df[df['Country/Region'] == country], variable, start_index, end_index)
			data[variable] = x[:]

		# Existing cases
		data['resolved'] = data['recovered'] + data['deaths']
		data['existing'] = data['confirmed'] - data['resolved']

		days = np.arange(len(dates_))
		daysmin = min(days.min(), daysmin)
		daysmax = max(days.max(), daysmax)

		ax.plot(days, data['existing'], 'o-', lw=linewidths[country], c=colors[country], alpha=0.5, label=country)
		ax2.plot(days, data['existing'], 'o-', lw=linewidths[country], c=colors[country], alpha=0.5, label=country)

	utl.configure_axes(ax, xlims=(daysmin, 20), xlabel='Days after First Case', ylabel='New Cases per Day')
	utl.configure_axes(ax2, xlims=(daysmin, 30), xlabel='Days after First Case', ylabel='New Cases per Day')

	ax.set_ylim(0, 40)
	ax.set_title('Existing Cases')
	# fig.savefig(os.path.join(ws.folders['website/static/images'], 'activos_01.png'), bbox_inches='tight')

	ax2.set_ylim(0, 40)
	ax2.set_title('Existing Cases')
	# fig2.savefig(os.path.join(ws.folders['website/static/images'], 'activos_02.png'), bbox_inches='tight')
	# plt.show()


def analysis_03(start, end, df):
	""" Exclusivo para Heath Cube """

	countries = ['Spain', 'Italy', 'Colombia']
	countries = ['Spain', 'Italy', 'Colombia', 'Korea, South', 'France']

	fig3, ax3 = plt.subplots()

	colors = {
		'Spain': 'k', 
		'Colombia': 'r', 
		'Italy': 'b', 
		'Korea, South': 'g', 
		'France': 'orange', 
	}

	linewidths = {
		'Spain': 1, 
		'Colombia': 2, 
		'Korea, South': 1, 
		'Italy': 1, 
		'France': 1, 
	}

	start_by_country3 = {
		'Spain': ws.dates_keys[33], 
		'Colombia': ws.dates_keys[47], 
		'Italy': ws.dates_keys[29], 
		'Korea, South': ws.dates_keys[28], 
		'France': ws.dates_keys[34], 
	}

	for country in countries:

		start = start_by_country3[country]
		start_index, end_index = get_start_end(start, end)

		data = {}
		variables = ['confirmed', 'deaths', 'recovered']

		daysmin = 1e99
		daysmax = -1e99

		for variable in variables:
			dates_, x = get_single_time_series(df[df['Country/Region'] == country], variable, start_index, end_index)
			data[variable] = x[:]

		# Existing cases
		data['resolved'] = data['recovered'] + data['deaths']
		data['existing'] = data['confirmed'] - data['resolved']

		days = np.arange(len(dates_))
		daysmin = min(days.min(), daysmin)
		daysmax = max(days.max(), daysmax)

		ax3.plot(days, data['existing'], 'o-', lw=linewidths[country], c=colors[country], alpha=0.5, label=country)

	utl.configure_axes(ax3, xlims=(daysmin, 15), xlabel='Days after Growth Rate Departure', ylabel='New Cases per Day')

	ax3.set_ylim(0, 1000)
	ax3.set_title('Existing Cases')
	fig3.savefig(os.path.join(ws.folders['website/static/images'], 'activos_05_02.png'), bbox_inches='tight')
	# plt.show()

def show_news(country, variables, start, end, df):
	""" Show the news for a country, along with the curve of the virus """

	fig, ax = plt.subplots(figsize=(20, 40))

	with open('../../news/spain.json', 'r') as f:
		news = json.load(f)

	if False:
		for i, n in enumerate(news):
			print(i, n["title"])

	# Interesting news
	interesting_news = [0, 2, 5, 8, 10, 12, 14, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 32, 33]
	interesting_news = [0, 2, 5, 19, 22, 23, 24, 25, 26, 27, 28, 29, 33]

	# List dates
	dates = []
	for i in interesting_news:
		n = news[i]
		dates.append(ws.dates[n["date"]])
	# Sort them
	dates, interesting_news = utl.sort_by_date(dates, interesting_news)

	for j, i in enumerate(interesting_news):
		# Add 1 just to make it human-understandable
		j += 1

		n = news[i]
		print(i, n["date"], n["title"])
		# ax.text(ws.dates[n["date"]], 1, j)
		ax.text(dates[j - 1], 1, j)
		ax.axvline(x=ws.dates[n["date"]], c='k', label="%i: %s"%(j, n["title"]))
		# ax.text(ws.dates[date], df[df['Country/Region'] == country][df['Date'] == date], i)

	show_country('Spain', variables, start, end, df, fig=fig, ax=ax)
	# plt.show()

def world_bokeh(start, end, df):
		""" Show the time series of the world in a HTML graph """

		# Get data
		start_index, end_index = get_start_end(start, end)
		data = {}
		variables = ['confirmed', 'recovered', 'deaths']
		for variable in variables:
			dates_, data[variable] = get_single_time_series(df, variable, start_index, end_index)

		# Existing cases
		data['resolved'] = data['recovered'] + data['deaths']
		data['active'] = data['confirmed'] - data['resolved']

		variables = variables + ['active']

		p = figure(
				plot_width=800, 
				plot_height=400, 
				x_axis_type="datetime", 
				title="Casos confirmados y activos en el mundo", 
				# x_range=(dates_[0], dates_[-1]), 
				# y_range=(data['confirmed'].min(), data['confirmed'].max()), 
			)

		# Add a circle renderer with a size, color and alpha
		p.circle(dates_, data['confirmed'], size=5, color="navy", alpha=0.5, legend_label='Confirmados')
		p.circle(dates_, data['active'], size=5, color="yellow", alpha=0.5, legend_label='Activos')

		# Arrange figure
		p.xaxis.axis_label = 'Fecha'
		p.yaxis.axis_label = 'Número de casos'
		p.legend.location = 'top_left'
		p.xaxis.formatter = DatetimeTickFormatter(days="%d %B")
		p.yaxis.formatter = NumeralTickFormatter(format="0")
		p.toolbar.logo = None

		# show(p)

		# Output to static HTML file
		output_file(os.path.join(ws.folders["website/static/images"], "world_graph.html"))
		save(p)

def world_map():
	""" World map in bokeh figure """
	"""
	Interactive map
	"""

	shapefile = os.path.join(ws.folders['data/misc'], 'countries/ne_110m_admin_0_countries.shp')

	# Read shapefile using Geopandas
	gdf = gpd.read_file(shapefile)[['ADMIN', 'ADM0_A3', 'geometry']]
	print(gdf.head())

	# Rename columns
	gdf.columns = ['country', 'country_code', 'geometry']
	print(gdf.head())

	# Drop row corresponding to 'Antarctica'
	gdf = gdf.drop(gdf.index[159])
	print(gdf.head())

	# Folder containing daily reports
	folder = os.path.join(ws.folders['data/covid'], 'csse_covid_19_data/csse_covid_19_daily_reports/')

	# Point to the global dataframe (no provinces)
	df = ws.data_countries_only

	# Change nans with 0
	# df.fillna(0, inplace=True)

	# Merge the data frames
	df_last_date = df[df['date_key'] == ws.dates_keys[-1]][['country_region', 'active']]
	merged = gdf.merge(df_last_date, left_on='country', right_on='country_region', how='left')
	# merged.fillna('No data', inplace=True)
	
	# Read data to json
	merged_json = json.loads(merged.to_json())

	# Convert to String like object.
	json_data = json.dumps(merged_json)

	# Input GeoJSON source that contains features for plotting.
	geosource = GeoJSONDataSource(geojson=json_data)
	
	# Define a sequential multi-hue color palette.
	palette = brewer['Reds'][8]
	
	# Reverse color order so that dark blue is highest obesity.
	palette = palette[::-1]
	
	# Instantiate LinearColorMapper that linearly maps numbers in a range, into a sequence of colors. Input nan_color.
	color_mapper = LinearColorMapper(palette=palette, low=0, high=df_last_date['active'].max())
	color_mapper_log = LogColorMapper(palette=palette, low=1, high=df_last_date['active'].max())
	# color_mapper_log = LogColorMapper(palette=palette, low=1, high=1e5+1)
	# color_mapper = LinearColorMapper(palette = palette, low = 0, high = 40, nan_color = '#d9d9d9')
	
	# Define custom tick labels for color bar.
	tick_labels = dict([('%i'%i, '%i'%i) for i in np.arange(90000)])
	order = 5
	tick_labels_log = dict([('%i'%i, '%i'%i) for i in np.logspace(0, order, order + 1)])
	print(tick_labels_log)

	# Add hover tool
	hover = HoverTool(tooltips=[('País', '@country'), ('Casos', '@active')])

	#Create color bar. 
	color_bar = ColorBar(
			color_mapper=color_mapper, 
			label_standoff=8, 
			width = 500, 
			height = 20,
			border_line_color=None, 
			location = (0,0), 
			orientation = 'horizontal', 
			major_label_overrides = tick_labels
		)
	color_bar_log = ColorBar(
			color_mapper=color_mapper_log, 
			label_standoff=8, 
			width = 400, 
			height = 10,
			border_line_color=None, 
			location = (0,0), 
			orientation = 'horizontal', 
			ticker=LogTicker(), 
		)

	# Create figure object.
	p = figure(
			title = 'Casos reportados como activos en el mundo, %s'%ws.dates_keys[-1], 
			plot_height = 500, 
			plot_width = 800, 
			toolbar_location = None, 
			tools = [hover]
		)

	p.xgrid.grid_line_color = None
	p.ygrid.grid_line_color = None

	# Add patch renderer to figure. 
	p.patches(
			'xs', 
			'ys', 
			source = geosource, 
			# fill_color = {'field' :'active', 'transform' : color_mapper}, 
			fill_color = {'field' :'active', 'transform' : color_mapper_log}, 
			line_color = 'black', 
			line_width = 0.25, 
			fill_alpha = 1
		)

	#Specify layout
	# p.add_layout(color_bar, 'below')
	p.add_layout(color_bar_log, 'below')

	# Display plot
	# show(p)

	# Save file
	print(os.path.join(ws.folders["website/static/images"], "world_map.html"))
	output_file(os.path.join(ws.folders["website/static/images"], "world_map.html"))
	save(p)