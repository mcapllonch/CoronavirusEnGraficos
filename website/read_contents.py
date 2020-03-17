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

read_contents.py:
Reads the contents from text files and stores them in a dictionary.
"""
import os

import workspace as ws


def read_folders():
	""" Read the names of the folders and store them """

	ws.folders = {}

	cwd = os.getcwd()
	folders = [item for item in os.listdir(cwd) if os.path.isdir(item)]

	# Store all of them in a dictionary
	ws.folders["cwd"] = cwd
	for item in folders:
		ws.folders[item] = os.path.join(cwd, item)

	print(ws.folders)

def read_contents():
	""" Read the text contents for the web page """

	# Contents folder
	contents_folder = ws.folders["contents"]

	# Read and store them
	ws.contents = {}
	for filename in os.listdir(contents_folder):
		if ".txt" in filename:
			with open(os.path.join(contents_folder, filename), "r") as f:
				key = f.readline().replace("Key: ", "").replace("\n", "")
				print('KEY: %s'%key)
				content = f.read()
				ws.contents[key] = content

	print(ws.contents.keys())