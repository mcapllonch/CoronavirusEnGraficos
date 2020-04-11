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
plt.style.use('ggplot')


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
			data['dates'], data[variable] = get_single_time_series(df, variable, start_index, end_index)

		# Existing cases
		data['resolved'] = data['recovered'] + data['deaths']
		data['active'] = data['confirmed'] - data['resolved']

		# New in 7 days (average)

		data_n7d = get_new_7_days(start_index, end_index, variable, country=country, avg=True)
		data['new_7_days'] = data_n7d['new_7_days']
		data['date_keys'] = data_n7d['date']

		variables = variables + ['active']

		# Choose title
		title = "Casos confirmados, activos y nuevos en "
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
		colors = {
			'confirmed': 'navy', 
			'active': 'orange', 
			'new_7_days': 'red', 
		}
		labels = {
			'confirmed': 'Confirmados', 
			'active': 'Activos', 
			'new_7_days': 'Nuevos (prom. 7 días)', 
		}
		plots = {}
		for v, c in colors.items():
			plots[v] = p.circle('dates', v, source=data, size=5, color=c, alpha=0.5)
			p.line('dates', v, source=data, line_width=2, color=c, alpha=0.5, legend_label=labels[v])

		# Hover tools
		hover1 = HoverTool(renderers=[plots['confirmed']], tooltips=[('Fecha', '@date_keys'), ('Confirmados', '@confirmed')])
		hover2 = HoverTool(renderers=[plots['active']], tooltips=[('Fecha', '@date_keys'), ('Activos', '@active')])
		hover3 = HoverTool(renderers=[plots['new_7_days']], tooltips=[('Fecha', '@date_keys'), ('Nuevos (prom. 7 días)', '@new_7_days')])
		p.add_tools(hover1)
		p.add_tools(hover2)
		p.add_tools(hover3)

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

		# Choose title
		title = "Casos %s%s"%(ws.trans[variable], title_add)

		# Hover tool indicating the country
		hover = HoverTool(tooltips=[('País', '@country'), ('Fecha', '@date_key'), ('Casos %s'%ws.trans[variable], '@%s'%variable)])

		# Figure
		p = figure(
				plot_width=800, 
				plot_height=400, 
				x_axis_type="datetime", 
				title=title, 
				# tools=[hover], 
			)
		p.add_tools(hover)

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

def get_new_7_days(start_index, end_index, variable, country='world', avg=False):
		""" Get the new cases in the last 7 days for a country """

		# Get data for countries
		df = ws.data_countries_only
		# Choose country from the dataset
		if country != 'world':
			df = df[df['country_region'] == country]

		# Target size for the arrays to return
		target_size = end_index - start_index + 1

		# Number of days
		ndays = 7
		# Choose if the output is an average
		if avg:
			avg_div = ndays
		else:
			avg_div = 1

		# Data to return
		data = {}

		# Get confirmed and active cases
		# The time series need to span the whole time (or, at least, 7 days before start_index)
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
		data['new_7_days'] = new7days // avg_div

		data['country'] = len(data[variable]) * [country]

		# Now chop the elements in data from indshift
		data = {k: v[indshift:] for k, v in data.items()}

		return data

def new_vs_active(start, end, x_range=None, y_range=None, variable='active', country='world', use_top_n=False, log=False):
	""" Show graph of new cases vs. active """

	# Start and end indices
	start_index, end_index = get_start_end(start, end)
	
	# Choose title
	title = "Casos nuevos vs. casos %s en "%ws.trans[variable]
	if country == 'world':
		addstr = 'el mundo'
	elif country == 'Spain':
		addstr = 'España'
	elif country == 'Colombia':
		addstr = 'Colombia'
	title = title + addstr

	data = get_new_7_days(start_index, end_index, variable, country=country, avg=True)

	# Bokeh figure for the country

	# Add hover tool
	hover = HoverTool(tooltips=[('Fecha', '@date'), ('Casos %s'%ws.trans[variable], '@%s'%variable), ('Casos nuevos (últ. 7d)', '@new_7_days')])

	# Figure
	p = figure(
			plot_width=800, 
			plot_height=400, 
			x_axis_type="datetime", 
			title=title, 
			# tools = [hover]
		)
	p.add_tools(hover)

	# Add a circle renderer with a size, color and alpha
	p.circle(variable, 'new_7_days', source=data, size=5, color="black", alpha=0.5)
	p.line(variable, 'new_7_days', source=data, line_width=2, color="black", alpha=0.5)

	# Arrange figure
	p.xaxis.axis_label = 'Casos %s'%ws.trans[variable]
	p.yaxis.axis_label = 'Casos nuevos en los últimos 7 días'
	p.yaxis.axis_label = 'Casos nuevos (promedio de 7 días)'
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
		hover_copy = HoverTool(tooltips=[('Fecha', '@date'), ('Casos %s'%ws.trans[variable], '@%s'%variable), ('Casos nuevos (últ. 7d)', '@new_7_days')])

		# Hover tool indicating the country
		hover2 = HoverTool(tooltips=[('País', '@country'), ('Fecha', '@date'), ('Casos %s'%ws.trans[variable], '@%s'%variable), ('Casos nuevos (últ. 7d)', '@new_7_days')])

		# Figure
		if log:
			p = figure(
					plot_width=800, 
					plot_height=400, 
					x_axis_type="log", 
					y_axis_type="log", 
					title="Casos nuevos vs. casos %s. Ejes en escala logarítmica"%ws.trans[variable], 
					# tools = [hover2], 
				)
		else:
			p = figure(
					plot_width=800, 
					plot_height=400, 
					title="Casos nuevos vs. casos %s"%ws.trans[variable], 
					# tools = [hover2], 
				)
		p.add_tools(hover2)
		if x_range is not None:
			p.x_range = Range1d(*x_range)
		if y_range is not None:
			p.y_range = Range1d(*y_range)

		df = ws.data_countries_only
		countries = set(df.country_region)
		if use_top_n:
			countries = ws.top_ten
		for country in countries:

			data = get_new_7_days(start_index, end_index, variable, country=country, avg=True)
			
			# Add a circle renderer with a size, color and alpha
			p.circle(variable, 'new_7_days', source=data, size=5, color="black", alpha=0.2)
			p.line(variable, 'new_7_days', source=data, line_width=2, color="black", alpha=0.2)
			# Last circle indicating the country
			data_last = {k: [v[-1]] for k, v in data.items()}
			data_last['country'] = [country]
			p.circle(variable, 'new_7_days', source=data_last, size=10, color="magenta", alpha=1.)
			p.text(x=data_last[variable], y=data_last['new_7_days'], text=[country],text_baseline="middle", text_align="left")

		# Arrange figure
		p.xaxis.axis_label = 'Casos %s'%ws.trans[variable]
		p.yaxis.axis_label = 'Casos nuevos en los últimos 7 días'
		p.yaxis.axis_label = 'Casos nuevos (promedio de 7 días)'
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

def top_n(df, n=10, groupby=['country_region']):
	""" Find top n countries/regions by confirmed cases.
	Spans the whole COVID-19 period """

	top_n = df.sort_values(by='confirmed', ignore_index=True, ascending=False).groupby(groupby, sort=False)['confirmed'].max().index[:n]
	return top_n.tolist()

def new_time_series(start, end, y_range=None, country='world', variable='new', use_top_n=False, log=False):
	""" Show the time series of new cases.
	variable = 'new_7_days' means we are using the last cases in the last week for each day """

	# Explanatory text for each variable
	variable_str = {
		'new': '', 
		# 'new_7_days': 'en los últimos 7 días'
		'new_7_days': '(promedio de 7 días)'
	}

	# Start and end indices
	start_index, end_index = get_start_end(start, end)
	
	# Choose title
	title = "Casos nuevos %s en "%variable_str[variable]
	title = "Casos nuevos (%s) en "%variable_str[variable]
	if country == 'world':
		addstr = 'el mundo'
	elif country == 'Spain':
		addstr = 'España'
	elif country == 'Colombia':
		addstr = 'Colombia'
	title = title + addstr

	data = get_new_7_days(start_index, end_index, variable, country=country, avg=True)

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
	# p.yaxis.axis_label = 'Casos nuevos en los últimos 7 días'
	p.yaxis.axis_label = 'Casos nuevos (promedio de 7 días)'
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
		# hover2 = HoverTool(tooltips=[('País', '@country'), ('Fecha', '@date'), ('Casos nuevos (últ. 7d)', '@new_7_days')])
		hover2 = HoverTool(tooltips=[('País', '@country'), ('Fecha', '@date'), ('Casos nuevos (prom. 7 días)', '@new_7_days')])

		# Figure
		if log:
			p = figure(
					plot_width=800, 
					plot_height=400,
					x_axis_type="datetime", 
					title="Casos nuevos %s en los %i países con más casos confirmados"%(variable_str[variable], ws.ntop), 
					# tools = [hover2], 
					y_axis_type="log", 
				)
		else:
			p = figure(
					plot_width=800, 
					plot_height=400,
					x_axis_type="datetime", 
					title="Casos nuevos %s en los %i países con más casos confirmados"%(variable_str[variable], ws.ntop), 
					# tools = [hover2], 
				)
		p.add_tools(hover2)
		if y_range is not None:
			p.y_range = Range1d(*y_range)

		df = ws.data_countries_only
		countries = set(df.country_region)
		if use_top_n:
			countries = ws.top_ten
		for i, country in enumerate(countries):

			data = get_new_7_days(start_index, end_index, variable, country=country, avg=True)
			
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
		data_n7d = get_new_7_days(start_index, end_index, 'confirmed', country=country, avg=True)

		# Days
		days = np.arange(len(dates_))
		daysmin = min(days.min(), daysmin)
		daysmax = max(days.max(), daysmax)

		# CASOS CONFIRMADOS
		ax1.plot(days, data['confirmed'], 'o-', lw=linewidths[country], label=country)

		# VELOCIDAD
		c = data['confirmed']
		velocidad = c[1:] - c[:-1]
		velocidad = data_n7d['new_7_days']
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

def horizontal_bar_plot(variable, df, country='world'):
	""" Make a horizontal bar plot of the provinces of a country """

	df = df.loc[:10][::-1]
	series = df.loc[:, variable]
	names = df.loc[:, 'departamento'].tolist()

	# Hover tool
	hover = HoverTool(tooltips=[('Departamento', '@departamento'), ('Casos confirmados', '@confirmed')])

	# Figure
	p = figure(
			width=500, 
			height=300, 
			y_range=names, 
			title="Casos confirmados en los\n10 departamentos más afectados"
		)
	# p.add_tools(hover)
	p.toolbar.logo = None

	p.grid.grid_line_alpha=1.0
	p.grid.grid_line_color = "white"

	p.xaxis.axis_label = 'Casos confirmados'
	# p.yaxis.axis_label = 'Departamento o distrito'

	j = 0
	for k, v in series.iteritems():
	  p.rect(x=v/2, y=j+0.5, width=abs(v), height=0.4,color=(76,114,176), width_units="data", height_units="data")
	  # p.rect(x=v/2, y=j+0.5, source=df, width=abs(v), height=0.4,color=(76,114,176), width_units="data", height_units="data")
	  j += 1

	output_file(os.path.join(ws.folders["website/static/images"], "%s_hbarplot.html"%country.lower()))
	# show(p)
	save(p)

def top_n_time_series(df, n=10, key_groupby='country_region', dates='date', variable='confirmed', label='country_region', title='', region_label='world', logscale=False):
	""" Show time series of the top 5 countries/regions/provinces in a dataset """

	# Show the top 10 provinces
	top_5 = top_n(df, n=5, groupby=[key_groupby])

	# Show graph
	plt.close('all')
	width = 8
	fig, ax = plt.subplots(figsize=(width, width * 0.61803398874988))

	for key in top_5:
		# Select the part of the dataframe I want
		data = df[df[key_groupby] == key]
		ax.plot(data[dates], data[variable], label=data[label].tolist()[0])

	ax.set_xlabel('Fecha')
	ax.set_ylabel('Casos %s'%ws.trans[variable])
	ax.legend()
	ax.set_title(title)
	plt.xticks(rotation=45)
	if logscale:
		ax.set_yscale('log')
	# plt.show()
	logstrings = {
		True: 'logscale', 
		False: ''
	}
	filename = '%s_time_series_%s_v1.png'%(region_label.lower(), logstrings[logscale])
	fig.savefig(os.path.join(ws.folders['website/static/images'], filename), bbox_inches='tight', dpi=300)