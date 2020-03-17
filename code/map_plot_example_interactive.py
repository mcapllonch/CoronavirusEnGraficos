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

Interactive map
"""
import pandas as pd
import geopandas as gpd
import json

shapefile = 'other_data/countries/ne_110m_admin_0_countries.shp'

# Read shapefile using Geopandas
gdf = gpd.read_file(shapefile)[['ADMIN', 'ADM0_A3', 'geometry']]

# Rename columns
gdf.columns = ['country', 'country_code', 'geometry']

# Drop row corresponding to 'Antarctica'
gdf = gdf.drop(gdf.index[159])

datafile = '../COVID-19/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv'

# Read the csv file using pandas
# df = pd.read_csv(datafile, names=['entity', 'code', 'year', 'per_cent_obesity'], skiprows=1)
df = pd.read_csv(datafile)

from bokeh.io import show, curdoc
from bokeh.models import Slider, HoverTool, GeoJSONDataSource, LinearColorMapper, ColorBar
from bokeh.plotting import figure
from bokeh.layouts import widgetbox, row, column
from bokeh.palettes import brewer

# Define function that returns json_data for year selected by user.

def json_data(selectedDate):
	d = selectedDate
	df_d = df[df['date'] == d]
	merged = gdf.merge(df_d, left_on='country_code', right_on='code', how='left')
	merged.fillna('No data', inplace=True)
	merged_json = json.loads(merged.to_json())
	json_data = json.dumps(merged_json)
	return json_data

# Input GeoJSON source that contains features for plotting.
geosource = GeoJSONDataSource(geojson = json_data('3/7/20'))

# Define a sequential multi-hue color palette.
palette = brewer['YlGnBu'][8]

# Reverse color order so that dark blue is highest obesity.
palette = palette[::-1]

# Instantiate LinearColorMapper that linearly maps numbers in a range, into a sequence of colors. Input nan_color.
color_mapper = LinearColorMapper(palette = palette, low = 0, high = 40, nan_color = '#d9d9d9')

#Define custom tick labels for color bar.
# tick_labels = {'0': '0%', '5': '5%', '10':'10%', '15':'15%', '20':'20%', '25':'25%', '30':'30%','35':'35%', '40': '>40%'}

# Add hover tool
hover = HoverTool(tooltips=[('Coutry/Region', '@country'), ('% obesity', '@per_cent_obesity')])

#Create color bar. 
# color_bar = ColorBar(color_mapper=color_mapper, label_standoff=8,width = 500, height = 20, border_line_color=None,location = (0,0), orientation = 'horizontal', major_label_overrides = tick_labels)
color_bar = ColorBar(color_mapper=color_mapper, label_standoff=8,width = 500, height = 20, border_line_color=None,location = (0,0), orientation = 'horizontal')

#Create figure object.
p = figure(title = 'Confirmed cases of coronavirus', plot_height = 600 , plot_width = 950, toolbar_location = None, tools = [hover])
p.xgrid.grid_line_color = None
p.ygrid.grid_line_color = None

#Add patch renderer to figure. 
p.patches('xs','ys', source = geosource,fill_color = {'field' :'per_cent_obesity', 'transform' : color_mapper},
          line_color = 'black', line_width = 0.25, fill_alpha = 1)

#Specify layout
p.add_layout(color_bar, 'below')

# Display plot
# show(layout)
show(p)