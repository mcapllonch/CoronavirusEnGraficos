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
import csv
import requests, bs4, json, re
import urllib.request as ur
from datetime import datetime
from shutil import copyfile

import workspace as ws



def update_csse():
	# Move to the data directory
	os.chdir(ws.folders['data/covid'])
	# Pull data from the repo
	print('')
	pullprocess = subprocess.Popen("git pull origin master", shell=True, stdout=subprocess.PIPE)
	pullprocess.wait()
	print('pullprocess.returncode:', pullprocess.returncode)
	# Back to the analysis directory
	os.chdir(ws.folders['analysis'])
	print('\tCSSE data successfully downloaded')
	print('')

def update_spain_isciii():
	""" Download/update Spanish data from https://covid19.isciii.es/ """
	now = datetime.now()
	url = "https://covid19.isciii.es/resources/serie_historica_acumulados.csv"
	filename = os.path.join(ws.folders['data/spain_specific'], 'datos_spain_%s.csv'%now.strftime("%Y-%m-%d_%H-%M"))
	ur.urlretrieve(url, filename)

	# Copy to 'data_last'
	copyfile(filename, os.path.join(ws.folders['data/spain_specific'], 'data_last.csv'))
	print('\tSpain\'s data successfully downloaded')

def update_colombia_ins():
	""" Download/update Colombian data from https://www.ins.gov.co/Noticias/Paginas/Coronavirus.aspx
	This requires a lot of data scrapping because the link to download the csv file is not available to requests or urllib """

	# url = "https://covid19.isciii.es/resources/serie_historica_acumulados.csv"
	url = "https://e.infogram.com/01266038-4580-4cf0-baab-a532bd968d0c?parent_url=https%3A%2F%2Fwww.ins.gov.co%2FNoticias%2FPaginas%2FCoronavirus.aspx&src=embed#"
	r = requests.get(url)
	# soup = bs4.BeautifulSoup(r.content, 'html5lib')
	# soup = bs4.BeautifulSoup(r.content, 'html.parser')
	# scripts = soup.findAll('script')
	p = re.compile(r'window\.infographicData=(.*);')
	data = json.loads(p.findall(r.text)[0])
	data = data['elements']['content']['content']
	entities = data['entities']
	datos = list(entities.values())[0]['props']['chartData']['data'][0]
	# # String to list
	# datos = list(datos)

	# Save to csv
	now = datetime.now()
	filename = os.path.join(ws.folders['data/colombia_specific'], 'datos_colombia_%s.csv'%now.strftime("%Y-%m-%d_%H-%M"))
	with open(filename, 'w') as f:
		fw = csv.writer(f)
		for row in datos:
			fw.writerow(row)

	# Copy to 'data_last'
	copyfile(filename, os.path.join(ws.folders['data/colombia_specific'], 'data_last.csv'))
	print('\tColombia\'s data successfully downloaded')