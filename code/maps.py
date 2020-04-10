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

tools_testing: As the name says, this is a module for testing new tools
"""
import os
import json
import itertools
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from bokeh.plotting import figure, save
from bokeh.models import Slider, HoverTool, Range1d, NumeralTickFormatter, DatetimeTickFormatter, GeoJSONDataSource, LinearColorMapper, LogColorMapper, ColorBar, BasicTicker, LogTicker, FixedTicker
from bokeh.io import show, output_file, curdoc
from bokeh.palettes import brewer, Spectral11, Category20, Category10
from bokeh.layouts import widgetbox, row, column

import workspace as ws
import utils as utl



def colombia_map(variable='confirmed', logscale=False):
	"""
	Interactive Colombian map in bokeh figure
	"""

	shapefile = os.path.join(ws.folders['data/misc'], 'departamentos_colombia/departamentos_colombia.shp')

	# Read shapefile using Geopandas
	gdf = gpd.read_file(shapefile)

	gdf = gdf[['cartodb_id', 'departamen', 'geometry']]

	# Remove 'None' values
	gdf = gdf[~gdf['geometry'].isnull()]

	# Rename columns
	gdf.columns = ['cartodb_id', 'departamento', 'geometry']

	# Make columns with lowered and 'normalized' values
	gdf['departamento_normalized'] = gdf['departamento'].str.lower().str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8').str.replace(' ', '').str.replace('.', '')

	# Lower the strings in 'departamento'

	# Point to the Colombian COVID-19 dataframe
	df = ws.data_specific['Colombia']

	# Change cartodb_id to int so that the dataframes can be merged
	df.cartodb_id = df.cartodb_id.astype(int)
	gdf.cartodb_id = gdf.cartodb_id.astype(int)

	# Merge the dataframes
	merged = gdf.merge(df, left_on='cartodb_id', right_on='cartodb_id', how='left')
	
	# Read data to json
	merged_json = json.loads(merged.to_json())

	# Convert to String like object.
	json_data = json.dumps(merged_json)

	# Input GeoJSON source that contains features for plotting.
	geosource = GeoJSONDataSource(geojson=json_data)
	
	# Define a sequential multi-hue color palette.
	order = int(np.log10(df[variable].max()))
	max_value = df[variable].max()
	max_rounded = utl.round_up_order(max_value, order)
	nlinticks = max_rounded // (10 ** order) + 1

	if logscale:
		palette = brewer['Reds'][order + 1]
	else:
		try:
			palette = brewer['Reds'][nlinticks - 1]
		except KeyError:
			# nlinticks is too large; use a matplotlib colormap
			cm = plt.cm.hot(mpl.colors.Normalize()(np.arange(nlinticks - 1))) * 255
			palette = ["#%02x%02x%02x"%(int(r), int(g), int(b)) for r, g, b, _ in cm]

	# Reverse color order so that dark blue is highest obesity.
	palette = palette[::-1]
	
	# Instantiate LinearColorMapper that linearly maps numbers in a range, into a sequence of colors. Input nan_color.
	color_mapper = LinearColorMapper(palette=palette, low=0, high=max_rounded)
	color_mapper_log = LogColorMapper(palette=palette, low=1, high=10**(order+1))

	# Define custom tick labels for color bar.
	tick_labels = dict([('%i'%i, '%i'%i) for i in np.linspace(0, max_rounded, nlinticks)])
	# Make tick labels numbers
	tick_labels = [int(v) for v in tick_labels.values()]
	tick_labels_log = dict([('%i'%i, '%i'%i) for i in np.logspace(0, order, order + 1)])

	# Add hover tool
	hover = HoverTool(tooltips=[('Departamento', '@departamento_x'), ('Casos', '@confirmed')])

	#Create color bar. 
	color_bar = ColorBar(
			color_mapper=color_mapper, 
			label_standoff=8, 
			width = 300, 
			height = 10,
			border_line_color=None, 
			location = (0,0), 
			orientation = 'horizontal', 
			ticker=FixedTicker(ticks=tick_labels), 
		)
	color_bar_log = ColorBar(
			color_mapper=color_mapper_log, 
			label_standoff=8, 
			width = 300, 
			height = 10,
			border_line_color=None, 
			location = (0,0), 
			orientation = 'horizontal', 
			ticker=LogTicker(), 
		)

	# Create figure object.
	p = figure(
			title = 'Casos confirmados en Colombia, %s'%ws.dates_keys[-1], 
			plot_height = 500, 
			plot_width = 400, 
			# aspect_ratio="auto", 
			# aspect_scale=1, 
			toolbar_location = None, 
			# tools = [hover]
		)
	p.add_tools(hover)

	p.xgrid.grid_line_color = None
	p.ygrid.grid_line_color = None

	# Add patch renderer to figure. 
	p.patches(
			'xs', 
			'ys', 
			source = geosource, 
			fill_color = {'field' :variable, 'transform' : color_mapper_log}, 
			line_color = 'black', 
			line_width = 1, 
			fill_alpha = 1
		)

	#Specify layout
	if logscale:
		p.add_layout(color_bar_log, 'below')
	else:
		p.add_layout(color_bar, 'below')

	# Save file
	if logscale:
		output_file(os.path.join(ws.folders["website/static/images"], "colombia_map_log.html"))
	else:
		output_file(os.path.join(ws.folders["website/static/images"], "colombia_map.html"))
	# show(p)
	save(p)

def world_map(variable='confirmed', logscale=False):
	"""
	Interactive world map in bokeh figure
	"""

	shapefile = os.path.join(ws.folders['data/misc'], 'countries/ne_110m_admin_0_countries.shp')

	# Read shapefile using Geopandas
	gdf = gpd.read_file(shapefile)[['ADMIN', 'ADM0_A3', 'geometry']]

	# Rename columns
	gdf.columns = ['country', 'country_code', 'geometry']

	# Drop row corresponding to 'Antarctica'
	gdf = gdf.drop(gdf.index[159])

	# Folder containing daily reports
	folder = os.path.join(ws.folders['data/covid'], 'csse_covid_19_data/csse_covid_19_daily_reports/')

	# Point to the global dataframe (no provinces)
	df = ws.data_countries_only

	# Merge the data frames
	df_last_date = df[df['date_key'] == ws.dates_keys[-1]][['country_region', variable]]
	merged = gdf.merge(df_last_date, left_on='country', right_on='country_region', how='left')
	
	# Read data to json
	merged_json = json.loads(merged.to_json())

	# Convert to String like object.
	json_data = json.dumps(merged_json)


	# Input GeoJSON source that contains features for plotting.
	geosource = GeoJSONDataSource(geojson=json_data)

	
	# Define a sequential multi-hue color palette.
	order = int(np.log10(df[variable].max()))
	max_value = df[variable].max()
	max_rounded = utl.round_up_order(max_value, order)
	nlinticks = max_rounded // (10 ** order) + 1
	if logscale:
		palette = brewer['Reds'][order + 1]
	else:
		palette = brewer['Reds'][nlinticks - 1]
	# Reverse color order so that dark blue is highest obesity.
	palette = palette[::-1]
	
	# Instantiate LinearColorMapper that linearly maps numbers in a range, into a sequence of colors. Input nan_color.
	max_value = df_last_date[variable].max()
	max_rounded = utl.round_up_order(max_value, order)
	color_mapper = LinearColorMapper(palette=palette, low=0, high=max_rounded)
	color_mapper_log = LogColorMapper(palette=palette, low=1, high=10**(order+1))

	# Define custom tick labels for color bar.
	tick_labels = dict([('%i'%i, '%i'%i) for i in np.linspace(0, max_rounded, nlinticks)])
	# Make tick labels numbers
	tick_labels = [int(v) for v in tick_labels.values()]
	tick_labels_log = dict([('%i'%i, '%i'%i) for i in np.logspace(0, order, order + 1)])

	# Add hover tool
	hover = HoverTool(tooltips=[('País', '@country'), ('Casos', '@active')])

	#Create color bar. 
	color_bar = ColorBar(
			color_mapper=color_mapper, 
			label_standoff=8, 
			width = 450, 
			height = 20,
			border_line_color=None, 
			location = (0,0), 
			orientation = 'horizontal', 
			ticker=FixedTicker(ticks=tick_labels), 
		)
	color_bar_log = ColorBar(
			color_mapper=color_mapper_log, 
			label_standoff=8, 
			width = 450, 
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
			# tools = [hover]
		)
	p.add_tools(hover)

	p.xgrid.grid_line_color = None
	p.ygrid.grid_line_color = None

	# Add patch renderer to figure. 
	p.patches(
			'xs', 
			'ys', 
			source = geosource, 
			fill_color = {'field' :variable, 'transform' : color_mapper_log}, 
			line_color = 'black', 
			line_width = 0.25, 
			fill_alpha = 1
		)

	#Specify layout
	if logscale:
		p.add_layout(color_bar_log, 'below')
	else:
		p.add_layout(color_bar, 'below')

	# Display plot

	# Save file
	if logscale:
		output_file(os.path.join(ws.folders["website/static/images"], "world_map_log.html"))
	else:
		output_file(os.path.join(ws.folders["website/static/images"], "world_map.html"))
	# show(p)
	save(p)