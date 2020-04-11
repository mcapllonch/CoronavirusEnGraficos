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

automated_main.py:
Automated script that updates the data and performs data analysis every certian number of hours
"""
import os
import sys
import time
from datetime import datetime

import datahandler as dh
import analysis_main as am


def update_all():
	""" Update all data """

	# Set up folders
	am.setup_folders()

	# Download CSSE data
	dh.update_csse()

	# Update Spanish data from ISCIII
	dh.update_spain_isciii()

	# Download Colombian data from INS
	# Not yet, because the web scraping does not update the data
	# dh.update_colombia_ins()

	# Run analysis
	am.run_analysis()

if __name__ == "__main__":

	# 6 hours in seconds
	sleep_time = 6 * 3600

	while True:
		print('')
		print(datetime.now())
		# Update all data
		update_all()
		# Sleep
		time.sleep(sleep_time)