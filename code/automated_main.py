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
Automated script that updates the data and performs data analysis every hour
"""
import os

import datahandler as dh
import read_time_series as rts
import workspace as ws



# Analysis folder
cwd = os.getcwd()
pardir = os.path.join(cwd, os.pardir)
ws.folders = {
	'analysis': cwd, 
	'data': os.path.join(pardir, 'data'), 
	'website': os.path.join(pardir, 'website')
}
ws.folders['website/static'] = os.path.join(ws.folders['website'], 'static')
ws.folders['website/static/images'] = os.path.join(ws.folders['website/static'], 'images')

# Update data
dh.update_data()

# Analyze it and generate products
rts.test_analysis()