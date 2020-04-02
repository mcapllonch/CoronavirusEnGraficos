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
import pandas as pd
from collections import Counter

import datahandler as dh
import read_time_series as rts
import workspace as ws
import tools as tls
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


def make_graphs():
	""" Make all the necessary graphs for the web site """

	df = ws.data
	ws.top_ten = tls.top_n(10)
	ws.ntop = len(ws.top_ten)
	
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

	# Count cases per province
	counter = {k: v for k, v in sorted(Counter(df['Departamento']).items(), key=lambda item: item[1], reverse=True)}

	# Create table to show
	dc = {'Departamento': counter.keys(), 'Confirmados': counter.values()}
	dfd = pd.DataFrame.from_dict(dc, orient='index').transpose()
	dfd.to_html(os.path.join(ws.folders['website/static/images'], 'departamentos.html'), index=False)

def run_analysis():
	""" Run a sample analysis """

	# Analyze it and generate products
	rts.read_daily_reports_JHU_CSSE()

	# Make graphs
	make_graphs()

	# Save numerical data for the web site
	num_data_for_website()

	# Process local data for countries
	da_colombia_specific()

if __name__ == "__main__":
	setup_folders()
	run_analysis()