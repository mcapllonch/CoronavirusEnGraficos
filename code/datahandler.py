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

datahandler.py:
Collects data from the GitHub repo of John Hopkins University
"""
import os
import subprocess

import workspace as ws



def update_data():
	# Move to the data directory
	os.chdir(ws.folders['data/covid'])
	# Pull data from the repo
	pullprocess = subprocess.Popen("git pull origin master", shell=True, stdout=subprocess.PIPE)
	pullprocess.wait()
	print('pullprocess.returncode:', pullprocess.returncode)
	# Back to the analysis directory
	os.chdir(ws.folders['analysis'])