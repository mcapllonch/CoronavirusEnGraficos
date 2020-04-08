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
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from bokeh.plotting import figure, save
from bokeh.models import Slider, HoverTool, Range1d, NumeralTickFormatter, DatetimeTickFormatter, GeoJSONDataSource, LinearColorMapper, LogColorMapper, ColorBar, BasicTicker, LogTicker
from bokeh.io import show, output_file, curdoc
from bokeh.palettes import brewer, Spectral11, Category20, Category10
from bokeh.layouts import widgetbox, row, column

import workspace as ws
import utils as utl



def colombia_map():
	"""
	Interactive Colombian map in bokeh figure
	"""

	shapefile = os.path.join(ws.folders['data/misc'], 'departamentos_colombia/departamentos_colombia.shp')
	# shapefile = os.path.join(ws.folders['data/misc'], 'departamentos_colombia/departamentos_colombia.geojson')

	# Read shapefile using Geopandas
	# gdf = gpd.read_file(shapefile)[['ADMIN', 'ADM0_A3', 'geometry']]
	gdf = gpd.read_file(shapefile)
	print(gdf.head())
	print(gdf.columns)

	gdf = gdf[['cartodb_id', 'departamen', 'geometry']]

	# Remove 'None' values
	gdf = gdf[~gdf['geometry'].isnull()]

	# Rename columns
	gdf.columns = ['cartodb_id', 'departamento', 'geometry']

	# # Remove accents
	# columns = gdf.select_dtypes(include=[np.object]).columns
	# gdf[columns] = gdf[columns].apply(lambda x: x.str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8'))

	# Make columns with lowered and 'normalized' values
	gdf['departamento_normalized'] = gdf['departamento'].str.lower().str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8').str.replace(' ', '').str.replace('.', '')

	# Lower the strings in 'departamento'
	# gdf['departamento'] = gdf['departamento'].str.lower()
	print(gdf.head())

	# Point to the Colombian COVID-19 dataframe
	df = ws.data_specific['Colombia']

	# Change nans with 0
	# df.fillna(0, inplace=True)

	# Merge the data frames
	# dfgdf = df[['departamento', 'confirmed']]
	# merged = gdf.merge(dfgdf, left_on='departamento', right_on='departamento', how='left')
	# merged = gdf.merge(df, left_on='departamento_normalized', right_on='departamento_normalized', how='left')
	print(df.dtypes)
	print(gdf.dtypes)
	df.cartodb_id = df.cartodb_id.astype(int)
	gdf.cartodb_id = gdf.cartodb_id.astype(int)
	merged = gdf.merge(df, left_on='cartodb_id', right_on='cartodb_id', how='left')
	# merged.fillna('No data', inplace=True)
	
	print('')
	print('Merged:')
	print(merged)
	# Read data to json
	merged_json = json.loads(merged.to_json())

	# Convert to String like object.
	json_data = json.dumps(merged_json)

	# json_data = json.dumps(json.loads(gdf.to_json()))
	# shapefile = os.path.join(ws.folders['data/misc'], 'departamentos_colombia/departamentos_colombia.geojson')
	# with open(shapefile, 'r') as f:
	# 	json_data = json.dumps(json.load(f))
	# geojson = gpd.read_file(shapefile).to_json()
	# print('')
	# print('merged_json:')
	# print(merged_json['features'].__dict__.keys())

	# Input GeoJSON source that contains features for plotting.
	geosource = GeoJSONDataSource(geojson=json_data)
	# geosource = GeoJSONDataSource(geojson=geojson)


	
	# Define a sequential multi-hue color palette.
	order = int(np.log10(df['confirmed'].max()))
	palette = brewer['Reds'][order + 1]
	
	# Reverse color order so that dark blue is highest obesity.
	palette = palette[::-1]
	
	# Instantiate LinearColorMapper that linearly maps numbers in a range, into a sequence of colors. Input nan_color.
	color_mapper = LinearColorMapper(palette=palette, low=0, high=df['confirmed'].max())
	# color_mapper_log = LogColorMapper(palette=palette, low=1, high=dfgdf['confirmed'].max())
	color_mapper_log = LogColorMapper(palette=palette, low=1, high=10**(order+1))
	# color_mapper_log = LogColorMapper(palette=palette, low=1, high=1e5+1)
	# color_mapper = LinearColorMapper(palette = palette, low = 0, high = 40, nan_color = '#d9d9d9')
	
	# Define custom tick labels for color bar.
	tick_labels = dict([('%i'%i, '%i'%i) for i in np.arange(90000)])
	tick_labels_log = dict([('%i'%i, '%i'%i) for i in np.logspace(0, order, order + 1)])
	# print(tick_labels_log)

	# Add hover tool
	hover = HoverTool(tooltips=[('Departamento', '@departamento_x'), ('Casos', '@confirmed')])

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
			title = 'Casos confirmados en Colombia, %s'%ws.dates_keys[-1], 
			plot_height = 500, 
			plot_width = 400, 
			# aspect_ratio="auto", 
			# aspect_scale=1, 
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
			fill_color = {'field' :'confirmed', 'transform' : color_mapper_log}, 
			line_color = 'black', 
			# line_width = 0.25, 
			line_width = 1, 
			fill_alpha = 1
		)

	#Specify layout
	p.add_layout(color_bar_log, 'below')

	# Save file
	output_file(os.path.join(ws.folders["website/static/images"], "colombia_map.html"))
	show(p)
	save(p)