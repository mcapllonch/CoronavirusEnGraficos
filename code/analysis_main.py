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

analysis_main.py:
Just run all the possible analyses
"""
import os
import sys
import numpy as np
import pandas as pd
from collections import Counter

import datahandler as dh
import read_time_series as rts
import workspace as ws
import tools as tls
import tools_testing as tt
import utils as utl


def setup_folders():
	""" Set up the necessary folders for analysis """
	# Analysis folder
	cwd = os.getcwd()
	pardir = cwd.replace('/code', '')
	ws.folders = {
		'analysis': cwd, 
		'data': os.path.join(pardir, 'data'), 
		'website': os.path.join(pardir, 'website')
	}

	# Covid and misc data
	# for s in ['covid', 'misc']:
	for s in ['covid', 'colombia_specific', 'spain_specific']:
		ws.folders['data/%s'%s] = os.path.join(ws.folders['data'], '%s'%s)
	ws.folders['data/misc'] = os.path.join(pardir, 'data_misc')


	# Static
	ws.folders['website/static'] = os.path.join(ws.folders['website'], 'static')
	# Folders for data and images on the web site
	for s in ['data', 'images']:
		ws.folders['website/static/%s'%s] = os.path.join(ws.folders['website/static'], '%s'%s)

	# Colors by variable
	ws.varcolors = {
		'confirmed': 'r', 
		'recovered': 'g', 
		'deaths': 'gray', 
		'resolved': 'b', 
		'balance': 'k', 
		'existing': 'orange', 
	}

	# Set up the specific datasets for each country
	ws.data_specific = {}


def make_graphs():
	""" Make all the necessary graphs for the web site """

	df = ws.data
	ws.top_ten = tls.top_n(10).tolist()
	ws.ntop = len(ws.top_ten)

	# Map for Colombia
	tt.colombia_map()
	# sys.exit()

	# Time series starting from 'Day 100' for several countries
	if False:
		# Custom countries
		custom_countries = [
				'Colombia', 
				'Spain', 
				'Italy', 
				'Ecuador', 
				'South Korea', 
				'Brazil', 
			]
		tls.countries_dayn(100, custom_countries)
	else:
		# Custom countries #2
		custom_countries = [
				'Colombia', 
				'Peru', 
				'Argentina', 
				'Ecuador', 
				'Chile', 
			]
		tls.countries_dayn(100, custom_countries)
	# print(ws.top_ten, ws.top_ten + ['Colombia'])
	# tls.countries_dayn(100, ws.top_ten + ['Colombia'])
	# sys.exit()
	
	# New vs. active
	tls.new_vs_active(
			ws.dates_keys[0], 
			ws.dates_keys[-1], 
			x_range=(1e3, 3e5), 
			y_range=(1e2, 2e5), 
			variable='active', 
			use_top_n=True, 
			log=True
		)
	# Time series for the growth
	# Top ten
	tls.new_time_series(
			ws.dates_keys[0], 
			ws.dates_keys[-1], 
			variable='new_7_days', 
			use_top_n=True, 
		)
	# In log-scale
	tls.new_time_series(
			'15/02/2020', 
			ws.dates_keys[-1], 
			y_range=(10, 2e5), 
			variable='new_7_days', 
			use_top_n=True, 
			log=True, 
		)
	# Time series for the world
	tls.time_series_bokeh(ws.dates_keys[0], ws.dates_keys[-1])
	# Time series for Spain and Colombia
	tls.time_series_bokeh('01/03/2020', ws.dates_keys[-1], country='Spain')
	tls.time_series_bokeh('01/03/2020', ws.dates_keys[-1], country='Colombia')
	# Time series for Latin America
	ws.south_american_countries = sorted([
				'Argentina', 
				'Brazil', 
				'Bolivia', 
				'Chile', 
				'Colombia',
				'Venezuela', 
				'Guyana', 
				'French Guiana', 
				'Suriname', 
				'Ecuador' ,
				'Peru', 
				'Paraguay', 
				'Uruguay', 
			])
	ws.latin_american_countries = sorted(ws.south_american_countries + [
				'Costa Rica' 
				'Cuba', 
				'Haiti', 
				'Nicaragua', 
				'Dominican Republic', 
				'Mexico',
				'Guatemala', 
				'Honduras',
				'El Salvador', 
				'Panama', 
			])
	tls.compare_countries(
			'12/03/2020', 
			ws.dates_keys[-1], 
			variable='confirmed', 
			countries=ws.latin_american_countries, 
			label='paises_latinoamericanos', 
			title_add=' en los países latinoamericanos', 
		)
	tls.compare_countries(
			'12/03/2020', 
			ws.dates_keys[-1], 
			variable='confirmed', 
			countries=ws.south_american_countries, 
			label='paises_suramericanos', 
			title_add=' en los países de Sur América', 
		)
	# World map
	tls.world_map()
	if False:
		tls.new_vs_active(ws.dates_keys[0], ws.dates_keys[-1], variable='active', country='Spain')
		tls.new_vs_active(ws.dates_keys[0], ws.dates_keys[-1], variable='active', country='Colombia')

def num_data_for_website():
	""" Save numerical data for the web site """

	# Date of last update
	last_date = list(ws.dates.keys())[-1]
	with open(os.path.join(ws.folders['website/static/data'], 'last_update.txt'), 'w') as f:
		f.write(last_date)

def da_colombia_specific():
	""" Specific data analysis for Colombia """

	# Open Colombia's data
	df = pd.read_csv(os.path.join(ws.folders['data/colombia_specific'], 'data_last.csv'))

	# Now open the data 'translator'
	dt = pd.read_csv(os.path.join(ws.folders['data/misc'], 'departamentos_colombia/data_and_map_translator.csv'))

	# Do some processing on the data

	# Lower case columns
	df.columns = [c.lower().replace(' ', '_') for c in df.columns]
	dt.columns = [c.lower().replace(' ', '_') for c in dt.columns]

	# Rename some columns
	df.rename(columns={'departamento_o_distrito': 'departamento'}, inplace=True)

	# Make columns with lowered and 'normalized' values
	df['departamento_normalized'] = df['departamento'].str.lower().str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8').str.replace(' ', '').str.replace('.', '')
	dt['departamento_normalized'] = dt['departamento'].str.lower().str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8').str.replace(' ', '').str.replace('.', '')
	dt['capitales_normalized'] = dt['capitales'].str.lower().str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8').str.replace(' ', '').str.replace('.', '')

	# Some provinces in df carry the names of their capital cities, so this needs to be sorted out
	dt_short = dt[~dt['capitales'].isnull()]
	capitales = {k: {'norm': a, 'departamento': b[:-1]} if b[-1] == ' ' else b for k, a, b in zip(dt_short['capitales'], dt_short['capitales_normalized'], dt_short['departamento'])}
	for c, d in capitales.items():
		a = d['norm']
		b = d['departamento']
		df.loc[df['departamento_normalized'] == a, 'departamento'] = b

	# Make a column with lowered and 'normalized' values, again, since some province names have been changed
	df['departamento_normalized'] = df['departamento'].str.lower().str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8').str.replace(' ', '').str.replace('.', '')

	# Merged the two into df
	df = df.merge(dt, left_on="departamento_normalized", right_on="departamento_normalized", how="left")

	# Dictionary with province codes and names
	dep_iso_dic = {k: {'norm': a, 'departamento': b[:-1] if b[-1] == ' ' else b} for k, a, b in zip(dt.iso, dt.departamento_normalized, dt.departamento)}

	# Count cases per province
	counter = {k: v for k, v in sorted(Counter(df['iso']).items(), key=lambda item: item[1], reverse=True)}

	# Create table to show
	dc = {
			'cartodb_id': [dt[dt['iso'] == k]['cartodb_id'] for k in counter.keys()], 
			'iso': counter.keys(), 
			'departamento': [dep_iso_dic[k]['departamento'] for k in counter.keys()], 
			'departamento_normalized': [dep_iso_dic[k]['norm'] for k in counter.keys()], 
			'confirmed': counter.values(), 
		}
	dfd = pd.DataFrame.from_dict(dc, orient='index').transpose()
	dfd.to_html(os.path.join(ws.folders['website/static/images'], 'departamentos.html'), index=False)

	print(df.head())

	print(dt.head())

	# Save it to the work space
	# ws.data_specific['Colombia'] = dfd
	ws.data_specific['Colombia'] = dfd
	print('')
	print(dfd)
	print('')

def run_analysis():
	""" Run a sample analysis """

	# Analyze it and generate products
	rts.read_daily_reports_JHU_CSSE()

	# Save numerical data for the web site
	num_data_for_website()

	# Process local data for countries
	da_colombia_specific()

	# Make graphs
	make_graphs()

if __name__ == "__main__":
	setup_folders()
	run_analysis()