import pandas as pd
import geopandas as gpd
import json

shapefile = 'data/countries/ne_110m_admin_0_countries.shp'

# Read shapefile using Geopandas
gdf = gpd.read_file(shapefile)[['ADMIN', 'ADM0_A3', 'geometry']]

# Rename columns
gdf.columns = ['country', 'country_code', 'geometry']

# Drop row corresponding to 'Antarctica'
gdf = gdf.drop(gdf.index[159])

datafile = 'data/vardata/share-of-adults-defined-as-obese.csv'

# Read the csv file using pandas
df = pd.read_csv(datafile, names=['entity', 'code', 'year', 'per_cent_obesity'], skiprows=1)

# Filter data for year 2016
df_2016 = df[df['year'] == 2016]

if False:
	# Merge dataframes gdf and df_2016
	merged = gdf.merge(df_2016, left_on='country_code', right_on='code')
# Perform left merge to preserve every row in gdf.
merged = gdf.merge(df_2016, left_on='country_code', right_on='code', how='left')
if False:
	# This is not really necessary; it's just to color missing countries in grey:
	
	# Replace NaN values to string 'No data'.
	merged.fillna('No data', inplace=True)

# Read data to json
merged_json = json.loads(merged.to_json())

# Convert to String like object.
json_data = json.dumps(merged_json)

from bokeh.io import show, output_file
from bokeh.plotting import figure
from bokeh.models import GeoJSONDataSource, LinearColorMapper, ColorBar
from bokeh.palettes import brewer

# Input GeoJSON source that contains features for plotting.
geosource = GeoJSONDataSource(geojson=json_data)

# Define a sequential multi-hue color palette.
palette = brewer['YlGnBu'][8]

# Reverse color order so that dark blue is highest obesity.
palette = palette[::-1]

# Instantiate LinearColorMapper that linearly maps numbers in a range, into a sequence of colors.
color_mapper = LinearColorMapper(palette=palette, low=0, high=40)

if False:
	# This is not really necessary; it's just to color missing countries in grey:

	# Instantiate LinearColorMapper that maps numbers in a range linearly into a sequence of colors. Input nan_color.
	color_mapper = LinearColorMapper(palette=palette, low=0, high=40, nan_color='#d9d9d9')

# Define custom tick labels for color bar.
tick_labels = {'0': '0%', '5': '5%', '10':'10%', '15':'15%', '20':'20%', '25':'25%', '30':'30%','35':'35%', '40': '>40%'}

# Create color bar.
color_bar = ColorBar(color_mapper=color_mapper, 
	label_standoff=8, 
	width=500, 
	height=20, 
	border_line_color=None, 
	location=(0, 0), 
	orientation='horizontal', 
	major_label_overrides=tick_labels)

# Create figure object
p = figure(title='Share of adults who are obese, 2016', 
	plot_height=600, 
	plot_width=950, 
	toolbar_location=None)

p.xgrid.grid_line_color=None
p.xgrid.grid_line_color=None

# Add patch renderer to figure.
p.patches('xs', 'ys', source=geosource, 
	fill_color={'field': 'per_cent_obesity', 'transform': color_mapper}, 
	line_color='black', 
	line_width=0.25, 
	fill_alpha=1)

# Specify figure layout.
p.add_layout(color_bar, 'below')

# Display figure.
show(p)