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
	if False:
		tls.show_world_time_series(ws.dates_keys[0], ws.dates_keys[-1], ws.data)
		tls.show_world_death_ratio_I(ws.dates_keys[0], ws.dates_keys[-1], ws.data)
		tls.show_country('Spain', ['confirmed', 'recovered', 'deaths'], ws.dates_keys[0], ws.dates_keys[-1], ws.data)
		tls.show_country('Colombia', ['confirmed', 'recovered', 'deaths'], ws.dates_keys[0], ws.dates_keys[-1], ws.data)
		tls.show_cases_per_day(ws.dates_keys[0], ws.dates_keys[-1], ws.data)
		tls.show_balance_per_day(ws.dates_keys[0], ws.dates_keys[-1], ws.data)
		tls.stackplot(ws.dates_keys[0], ws.dates_keys[-1], ws.data)
		
		# More analysis
		tls.analysis_01(ws.dates_keys[10], ws.dates_keys[-1], ws.data)
		tls.analysis_02(ws.dates_keys[10], ws.dates_keys[-1], ws.data)
		tls.analysis_03(ws.dates_keys[10], ws.dates_keys[-1], ws.data)

		print(ws.dates_keys, dates)
		tls.show_news('Spain', ['confirmed'], ws.dates_keys[0], ws.dates_keys[-1], ws.data)

	tls.world_bokeh(ws.dates_keys[0], ws.dates_keys[-1], ws.data)

def num_data_for_website():
	""" Save numerical data for the web site """

	# Date of last update
	last_date = list(ws.dates.keys())[-1]
	print('Last update: %s'%last_date)
	with open(os.path.join(ws.folders['website/static/data'], 'last_update.txt'), 'w') as f:
		f.write(last_date)

def run_analysis():
	""" Run a sample analysis """

	# Analyze it and generate products
	rts.test_analysis()

	# Make graphs
	make_graphs()

	# Save numerical data for the web site
	num_data_for_website()

if __name__ == "__main__":
	setup_folders()
	run_analysis()