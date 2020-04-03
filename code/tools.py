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
import itertools
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from bokeh.plotting import figure, save
from bokeh.models import Slider, HoverTool, Range1d, NumeralTickFormatter, DatetimeTickFormatter, GeoJSONDataSource, LinearColorMapper, LogColorMapper, ColorBar, BasicTicker, LogTicker
from bokeh.io import show, output_file, curdoc
from bokeh.palettes import brewer, Spectral11, Category20, Category10
from bokeh.layouts import widgetbox, row, column

import workspace as ws
import utils as utl


plt.style.use('format001.mplstyle')


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
		data[variable] = df[df['country_region'] == country][df['Date'] == date][variable].sum()
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

def time_series_bokeh(start, end, country='world'):
		""" Show the time series of the world in a HTML graph """

		# Get data
		df = ws.data_countries_only
		if country != 'world':
			df = df[df['country_region'] == country]
		start_index, end_index = get_start_end(start, end)
		data = {}
		variables = ['confirmed', 'recovered', 'deaths']
		for variable in variables:
			dates_, data[variable] = get_single_time_series(df, variable, start_index, end_index)

		# Existing cases
		data['resolved'] = data['recovered'] + data['deaths']
		data['active'] = data['confirmed'] - data['resolved']

		variables = variables + ['active']

		# Choose title
		title = "Casos confirmados y activos en "
		if country == 'world':
			addstr = 'el mundo'
		elif country == 'Spain':
			addstr = 'España'
		elif country == 'Colombia':
			addstr = 'Colombia'
		title = title + addstr

		p = figure(
				plot_width=800, 
				plot_height=400, 
				x_axis_type="datetime", 
				title=title, 
				# x_range=(dates_[0], dates_[-1]), 
				# y_range=(data['confirmed'].min(), data['confirmed'].max()), 
			)

		# Add a circle renderer with a size, color and alpha
		p.circle(dates_, data['confirmed'], size=5, color="navy", alpha=0.5, legend_label='Confirmados')
		p.circle(dates_, data['active'], size=5, color="orange", alpha=0.5, legend_label='Activos')

		# Arrange figure
		p.xaxis.axis_label = 'Fecha'
		p.yaxis.axis_label = 'Número de casos'
		p.legend.location = 'top_left'
		p.xaxis.formatter = DatetimeTickFormatter(days="%d %B")
		p.yaxis.formatter = NumeralTickFormatter(format="0")
		p.toolbar.logo = None


		# Output to static HTML file
		output_file(os.path.join(ws.folders["website/static/images"], "%s_graph.html"%country.lower()))
		# show(p)
		save(p)

def compare_countries(start, end, variable='confirmed', countries=None, label='', title_add=''):
		""" Show the time series of the world in a HTML graph """
			
		# Get data
		df = ws.data_countries_only
		# Date range
		start_index, end_index = get_start_end(start, end)

		# Translation keys for the variables
		trans = {
			'active': 'activos', 
			'confirmed': 'confirmados', 
		}
		# Choose title
		title = "Casos %s%s"%(trans[variable], title_add)

		# Hover tool indicating the country
		hover = HoverTool(tooltips=[('País', '@country'), ('Fecha', '@date_key'), ('Casos %s'%trans[variable], '@%s'%variable)])

		# Figure
		p = figure(
				plot_width=800, 
				plot_height=400, 
				x_axis_type="datetime", 
				title=title, 
				tools=[hover], 
			)

		if countries is None:
			countries = []

		# Choose graph options depending on the number of countries
		ncountries = len(countries)
		# category20 = list(Category20.values())
		category20 = Category20[20]
		category10 = Category10[10]
		many_countries = ncountries > len(category20)

		alpha = 1.
		legend = True
		add_text = False
		if many_countries:
			colors = ncountries * ['black']
			alpha = 0.2
			legend = False
			add_text = True
		elif ncountries > len(Spectral11):
			colors = category20[:]
		elif ncountries > len(category10):
			colors = Spectral11[:]
		else:
			colors = category10[:]

		# Iterate over countries
		for i, country in enumerate(countries):

			# Get data for the country
			df_ = df[df['country_region'] == country]
			data = {}
			data['date_obj'], data[variable] = get_single_time_series(df_, variable, start_index, end_index)
			# data['date_key'] = [x.strftime("%d/%m/%Y") for x in data['date_obj']]
			data['date_key'] = ws.dates_keys[start_index:end_index + 1]
			data['country'] = len(data[variable]) * [country]

			# Plot data
			if not many_countries:
				p.circle('date_obj', variable, source=data, color=colors[i], size=5, alpha=alpha, legend_label=country)
				p.line('date_obj', variable, source=data, color=colors[i], line_width=2, alpha=alpha, legend_label=country)
			else:
				p.circle('date_obj', variable, source=data, color=colors[i], size=5, alpha=alpha)
				p.line('date_obj', variable, source=data, color=colors[i], line_width=2, alpha=alpha)
				# p.text(x=data['date_obj'], y=data[variable], text=[country],text_baseline="middle", text_align="left")
				p.text(x=data['date_obj'][-1], y=data[variable][-1], text=[country])

		# Arrange figure
		p.xaxis.axis_label = 'Fecha'
		p.yaxis.axis_label = 'Número de casos'
		if legend:
			p.legend.location = 'top_left'
		p.xaxis.formatter = DatetimeTickFormatter(days="%d %B")
		p.yaxis.formatter = NumeralTickFormatter(format="0")
		p.toolbar.logo = None

		# Output to static HTML file
		output_file(os.path.join(ws.folders["website/static/images"], "%s_%s_time_series.html"%(label, variable)))
		# show(p)
		save(p)

def world_map():
	"""
	Interactive world map in bokeh figure
	"""

	shapefile = os.path.join(ws.folders['data/misc'], 'countries/ne_110m_admin_0_countries.shp')

	# Read shapefile using Geopandas
	gdf = gpd.read_file(shapefile)[['ADMIN', 'ADM0_A3', 'geometry']]
	# print(gdf.head())

	# Rename columns
	gdf.columns = ['country', 'country_code', 'geometry']
	# print(gdf.head())

	# Drop row corresponding to 'Antarctica'
	gdf = gdf.drop(gdf.index[159])
	# print(gdf.head())

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

	print('')
	print(merged)
	
	# Read data to json
	merged_json = json.loads(merged.to_json())

	# Convert to String like object.
	json_data = json.dumps(merged_json)
	# print('')
	# print('merged_json:')
	# print(merged_json['features'].__dict__.keys())

	# Input GeoJSON source that contains features for plotting.
	geosource = GeoJSONDataSource(geojson=json_data)

	# print('')
	# print(geosource)
	
	# Define a sequential multi-hue color palette.
	order = int(np.log10(df_last_date['active'].max()))
	palette = brewer['Reds'][order + 1]
	
	# Reverse color order so that dark blue is highest obesity.
	palette = palette[::-1]
	
	# Instantiate LinearColorMapper that linearly maps numbers in a range, into a sequence of colors. Input nan_color.
	color_mapper = LinearColorMapper(palette=palette, low=0, high=df_last_date['active'].max())
	# color_mapper_log = LogColorMapper(palette=palette, low=1, high=df_last_date['active'].max())
	color_mapper_log = LogColorMapper(palette=palette, low=1, high=10**(order+1))
	# color_mapper_log = LogColorMapper(palette=palette, low=1, high=1e5+1)
	# color_mapper = LinearColorMapper(palette = palette, low = 0, high = 40, nan_color = '#d9d9d9')
	
	# Define custom tick labels for color bar.
	tick_labels = dict([('%i'%i, '%i'%i) for i in np.arange(90000)])
	tick_labels_log = dict([('%i'%i, '%i'%i) for i in np.logspace(0, order, order + 1)])
	# print(tick_labels_log)

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
			width = 500, 
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
			fill_color = {'field' :'active', 'transform' : color_mapper_log}, 
			line_color = 'black', 
			line_width = 0.25, 
			fill_alpha = 1
		)

	#Specify layout
	p.add_layout(color_bar_log, 'below')

	# Display plot

	# Save file
	output_file(os.path.join(ws.folders["website/static/images"], "world_map.html"))
	# show(p)
	save(p)

def get_new_7_days(start_index, end_index, variable, country='world'):
		""" Get the new cases in the last 7 days for a country """

		df = ws.data_countries_only
		# Choose country from the dataset
		if country != 'world':
			df = df[df['country_region'] == country]

		# Target size for the arrays to return
		target_size = end_index - start_index + 1

		# Data to return
		data = {}

		# Get confirmed and active cases
		# The time series need to span the whole time (or, at least, 7 days before start_index)
		ndays = 7
		if start_index >= ndays:
			start_index_ = start_index - (ndays - 1)
		else:
			start_index_ = 0
		# Index shift
		indshift = start_index - start_index_
		# Get time series
		for variable in ['confirmed', 'active']:
			dates_, data[variable] = get_single_time_series(df, variable, start_index_, end_index)

		# Format dates to strings
		data['date'] = []
		data['date_obj'] = []
		for date in dates_:
			date_str = date.strftime('%d/%m/%Y')
			data['date'].append(date_str)
			data['date_obj'].append(ws.dates[date_str])

		# To array
		data['date_obj'] = np.array(data['date_obj'])

		c = data['confirmed']
		new = np.zeros_like(data['confirmed'])
		data['new_7_days'] = np.zeros_like(c)
		new[1:] = c[1:] - c[:-1]
		data['new'] = new

		new7days = np.zeros_like(new)
		for i in range(ndays - 1):
			new7days[i] += new[:i+1].sum()
		for i in range(ndays - 1, len(new), 1):
			new7days[i] += new[i-(ndays-1):i+1].sum()
		data['new_7_days'] = new7days

		data['country'] = len(data[variable]) * [country]

		# Now chop the elements in data from indshift
		data = {k: v[indshift:] for k, v in data.items()}

		return data

def new_vs_active(start, end, x_range=None, y_range=None, variable='active', country='world', use_top_n=False, log=False):
	""" Show graph of new cases vs. active """

	# Translation keys for the variables
	trans = {
		'active': 'activos', 
		'confirmed': 'confirmados', 
	}

	# Start and end indices
	start_index, end_index = get_start_end(start, end)
	
	# Choose title
	title = "Casos nuevos vs. casos %s en "%trans[variable]
	if country == 'world':
		addstr = 'el mundo'
	elif country == 'Spain':
		addstr = 'España'
	elif country == 'Colombia':
		addstr = 'Colombia'
	title = title + addstr

	data = get_new_7_days(start_index, end_index, variable, country=country)

	# Bokeh figure for the country

	# Add hover tool
	hover = HoverTool(tooltips=[('Fecha', '@date'), ('Casos %s'%trans[variable], '@%s'%variable), ('Casos nuevos (últ. 7d)', '@new_7_days')])

	# Figure
	p = figure(
			plot_width=800, 
			plot_height=400, 
			x_axis_type="datetime", 
			title=title, 
			tools = [hover]
		)

	# Add a circle renderer with a size, color and alpha
	p.circle(variable, 'new_7_days', source=data, size=5, color="black", alpha=0.5)
	p.line(variable, 'new_7_days', source=data, line_width=2, color="black", alpha=0.5)

	# Arrange figure
	p.xaxis.axis_label = 'Casos %s'%trans[variable]
	p.yaxis.axis_label = 'Casos nuevos en los últimos 7 días'
	p.xaxis.formatter = NumeralTickFormatter(format="0")
	p.yaxis.formatter = NumeralTickFormatter(format="0")
	p.toolbar.logo = None

	# Output to static HTML file
	output_file(os.path.join(ws.folders["website/static/images"], "new_vs_%s_last7days_%s.html"%(variable, country.lower())))

	# show(p)
	save(p)

	######################################
	# Bokeh figure for all the countries

	if country == 'world':

		# Copy previous hover tool
		hover_copy = HoverTool(tooltips=[('Fecha', '@date'), ('Casos %s'%trans[variable], '@%s'%variable), ('Casos nuevos (últ. 7d)', '@new_7_days')])

		# Hover tool indicating the country
		hover2 = HoverTool(tooltips=[('País', '@country'), ('Fecha', '@date'), ('Casos %s'%trans[variable], '@%s'%variable), ('Casos nuevos (últ. 7d)', '@new_7_days')])

		# Figure
		if log:
			p = figure(
					plot_width=800, 
					plot_height=400, 
					x_axis_type="log", 
					y_axis_type="log", 
					title="Casos nuevos vs. casos %s. Ejes en escala logarítmica"%trans[variable], 
					tools = [hover2], 
				)
		else:
			p = figure(
					plot_width=800, 
					plot_height=400, 
					title="Casos nuevos vs. casos %s"%trans[variable], 
					tools = [hover2], 
				)
		if x_range is not None:
			p.x_range = Range1d(*x_range)
		if y_range is not None:
			p.y_range = Range1d(*y_range)

		df = ws.data_countries_only
		countries = set(df.country_region)
		if use_top_n:
			countries = ws.top_ten
		for country in countries:

			data = get_new_7_days(start_index, end_index, variable, country=country)
			
			# Add a circle renderer with a size, color and alpha
			p.circle(variable, 'new_7_days', source=data, size=5, color="black", alpha=0.2)
			p.line(variable, 'new_7_days', source=data, line_width=2, color="black", alpha=0.2)
			# Last circle indicating the country
			data_last = {k: [v[-1]] for k, v in data.items()}
			data_last['country'] = [country]
			# print(data_last)
			p.circle(variable, 'new_7_days', source=data_last, size=10, color="magenta", alpha=1.)
			p.text(x=data_last[variable], y=data_last['new_7_days'], text=[country],text_baseline="middle", text_align="left")

		# Arrange figure
		p.xaxis.axis_label = 'Casos %s'%trans[variable]
		p.yaxis.axis_label = 'Casos nuevos en los últimos 7 días'
		p.xaxis.formatter = NumeralTickFormatter(format="0")
		p.yaxis.formatter = NumeralTickFormatter(format="0")
		p.toolbar.logo = None


		# Output to static HTML file
		use_log_str = 'logscale' if log else ''
		if use_top_n:
			output_file(os.path.join(ws.folders["website/static/images"], "new_vs_%s_last7days_top_n%01i_%s.html"%(variable, ws.ntop, use_log_str)))
		else:
			output_file(os.path.join(ws.folders["website/static/images"], "	new_vs_%s_last7days_whole_world_%s.html"%(variable, use_log_str)))

		# show(p)
		save(p)

def top_n(n=10):
	""" F-ind top n countries by confirmed cases.
	Spans the whole COVID-19 period """

	df = ws.data_countries_only

	top_n = df.sort_values(by='confirmed', ignore_index=True, ascending=False).groupby(['country_region'], sort=False)['confirmed'].max().index[:n]
	return top_n

def new_time_series(start, end, y_range=None, country='world', variable='new', use_top_n=False, log=False):
	""" Show the time series of new cases.
	variable = 'new_7_days' means we are using the last cases in the last week for each day """

	# Translation keys for the variables
	trans = {
		'active': 'activos', 
		'confirmed': 'confirmados', 
	}

	# Explanatory text for each variable
	variable_str = {
		'new': '', 
		'new_7_days': 'en los últimos 7 días'
	}

	# Start and end indices
	start_index, end_index = get_start_end(start, end)
	
	# Choose title
	title = "Casos nuevos %s en "%variable_str[variable]
	if country == 'world':
		addstr = 'el mundo'
	elif country == 'Spain':
		addstr = 'España'
	elif country == 'Colombia':
		addstr = 'Colombia'
	title = title + addstr

	data = get_new_7_days(start_index, end_index, variable, country=country)

	# Bokeh figure for the country

	# Figure
	if log:
		p = figure(
				plot_width=800, 
				plot_height=400, 
				x_axis_type="datetime", 
				title=title, 
				y_axis_type="log", 
			)
	else:
		p = figure(
				plot_width=800, 
				plot_height=400, 
				x_axis_type="datetime", 
				title=title, 
			)
	if y_range is not None:
		p.y_range = Range1d(*y_range)

	# Add a circle renderer with a size, color and alpha
	p.circle('date_obj', variable, source=data, size=5, color="black", alpha=0.5)
	p.line('date_obj', variable, source=data, line_width=2, color="black", alpha=0.5)

	# Arrange figure
	# p.x_range = Range1d(data['date_obj'][0], data['date_obj'][-1])
	p.xaxis.axis_label = 'Fecha'
	p.yaxis.axis_label = 'Casos nuevos en los últimos 7 días'
	p.xaxis.formatter = DatetimeTickFormatter(days="%d %B")
	p.yaxis.formatter = NumeralTickFormatter(format="0")
	p.toolbar.logo = None

	# Output to static HTML file
	output_file(os.path.join(ws.folders["website/static/images"], "%s_vs_date_%s.html"%(variable, country.lower())))

	# show(p)
	save(p)

	######################################
	# Bokeh figure for all the countries

	if country == 'world':

		# Hover tool indicating the country
		hover2 = HoverTool(tooltips=[('País', '@country'), ('Fecha', '@date'), ('Casos nuevos (últ. 7d)', '@new_7_days')])

		# Figure
		if log:
			p = figure(
					plot_width=800, 
					plot_height=400,
					x_axis_type="datetime", 
					title="Casos nuevos %s en los %i países con más casos confirmados"%(variable_str[variable], ws.ntop), 
					tools = [hover2], 
					y_axis_type="log", 
				)
		else:
			p = figure(
					plot_width=800, 
					plot_height=400,
					x_axis_type="datetime", 
					title="Casos nuevos %s en los %i países con más casos confirmados"%(variable_str[variable], ws.ntop), 
					tools = [hover2], 
				)
		if y_range is not None:
			p.y_range = Range1d(*y_range)

		df = ws.data_countries_only
		countries = set(df.country_region)
		if use_top_n:
			countries = ws.top_ten
		for i, country in enumerate(countries):

			data = get_new_7_days(start_index, end_index, variable, country=country)
			
			# Add a circle renderer with a size, color and alpha
			p.circle('date_obj', variable, source=data, color=Spectral11[i], size=5, alpha=1., legend_label=country)
			p.line('date_obj', variable, source=data, color=Spectral11[i], line_width=2, alpha=1., legend_label=country)

		# Arrange figure
		# p.x_range = Range1d(data['date_obj'][0], data['date_obj'][-1])
		p.xaxis.axis_label = 'Fecha'
		p.yaxis.axis_label = 'Casos nuevos %s'%variable_str[variable]
		p.xaxis.formatter = DatetimeTickFormatter(days="%d %B")
		p.yaxis.formatter = NumeralTickFormatter(format="0")
		p.legend.location = 'top_left'
		p.toolbar.logo = None

		# Output to static HTML file
		use_log_str = 'logscale' if log else ''
		if use_top_n:
			output_file(os.path.join(ws.folders["website/static/images"], "%s_vs_date_top_n%01i_%s.html"%(variable, ws.ntop, use_log_str)))
		else:
			output_file(os.path.join(ws.folders["website/static/images"], "	%s_vs_date_whole_world_%s.html"%(variable_str[variable], use_log_str)))

		# show(p)
		save(p)

def countries_dayn(n, countries):
	""" Show countries from the day they reached or surpassed n cases """

	# Get data
	df = ws.data_countries_only

	# Parameters
	linewidths = {k: 1 for k in countries}
	linewidths['Colombia'] = 2
	end = '01/04/2020'

	# Create figures
	fig1, ax1 = plt.subplots()
	fig2, ax2 = plt.subplots()
	fig3, ax3 = plt.subplots()

	# Iterate over countries to plot data
	for country in countries:

		# Find the day when n cases were reached for each country
		# First, get the whole time series
		dates_, x = get_single_time_series(df[df['country_region'] == country], 'confirmed', 0, ws.date_indices['01/04/2020'])
		# Find where the country reached the n cases
		date_index = np.where(x >= n)[0][0]
		start = ws.dates_keys[date_index]
		start_index, end_index = get_start_end(start, end)

		data = {}

		daysmin = 1e99
		daysmax = -1e99

		dates_, x = get_single_time_series(df[df['country_region'] == country], 'confirmed', start_index, end_index)
		data['confirmed'] = x[:]

		# Get new cases in 7 days
		data_n7d = get_new_7_days(start_index, end_index, 'confirmed', country=country)

		# Days
		days = np.arange(len(dates_))
		daysmin = min(days.min(), daysmin)
		daysmax = max(days.max(), daysmax)

		# CASOS CONFIRMADOS
		ax1.plot(days, data['confirmed'], 'o-', lw=linewidths[country], label=country)

		# VELOCIDAD
		c = data['confirmed']
		velocidad = c[1:] - c[:-1]
		velocidad = data_n7d['new_7_days'] / 7.
		# ax2.plot(days[1:], velocidad, 'o-', lw=linewidths[country], label=country)
		ax2.plot(days, velocidad, 'o-', lw=linewidths[country], label=country)

		# ACELERACIÓN
		aceleracion = velocidad[1:] - velocidad[:-1]
		# ax3.plot(days[2:], aceleracion, 'o-', lw=linewidths[country], label=country)
		ax3.plot(days[1:], aceleracion, 'o-', lw=linewidths[country], label=country)

	# Arrange figures
	# 1
	ax1.set_ylim(0, 1100)
	# ax1.set_yscale('log')
	utl.configure_axes(ax1, xlims=(daysmin, 14), xlabel='Días después de alcanzar %i casos'%n, ylabel='Casos confirmados')
	ax1.set_title('Casos confirmados')
	# 2
	# ax2.set_ylim(0, 500)
	ax2.set_ylim(0, 250)
	# ax2.set_yscale('log')
	utl.configure_axes(ax2, xlims=(daysmin, 14), xlabel='Días después de alcanzar %i casos'%n, ylabel='Velocidad (casos confirmados nuevos diarios)')
	utl.configure_axes(ax2, xlims=(daysmin, 14), xlabel='Días después de alcanzar %i casos'%n, ylabel='Velocidad (casos confirmados nuevos diarios;\npromedio de 7 días)')
	ax2.set_title('Velocidad')
	# 3
	# ax3.set_ylim(-10, 100)
	ax3.set_ylim(-10, 50)
	# ax3.set_yscale('log')
	ax3.axhline(y=0, ls='--', c='grey')
	utl.configure_axes(ax3, xlims=(daysmin, 14), xlabel='Días después de alcanzar %i casos'%n, ylabel='Aceleración (aumento diario de casos confirmados nuevos)')
	utl.configure_axes(ax3, xlims=(daysmin, 14), xlabel='Días después de alcanzar %i casos'%n, ylabel='Aceleración (aumento diario de casos confirmados nuevos;\npromedio de 7 días)')
	ax3.set_title('Aceleración')

	# Save figures
	fig1.savefig(os.path.join(ws.folders['website/static/images'], 'custom_casos_%i_%s_v2.png'%(n, ''.join([c[0] for c in countries]))), bbox_inches='tight', dpi=300)
	fig2.savefig(os.path.join(ws.folders['website/static/images'], 'custom_velocidad_%i_%s_v4.png'%(n, ''.join([c[0] for c in countries]))), bbox_inches='tight', dpi=300)
	fig3.savefig(os.path.join(ws.folders['website/static/images'], 'custom_aceleracion_%i_%s_v2.png'%(n, ''.join([c[0] for c in countries]))), bbox_inches='tight', dpi=300)
	# plt.show()
