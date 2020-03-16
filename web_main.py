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

web_main.py:
Main script to run the web app.
"""
import os
import time
import flask

# from forms import ParamsForm
import config
import read_contents
import workspace as ws


# Preliminary settings:

# Application
app = flask.Flask(__name__)
# Security
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# Read contents
read_contents.read_folders()
read_contents.read_contents()

# Flag. If True, this is for development
# If False, it's for actual use. So False by default
development = True

# Construct the app

# Home page
@app.route('/', methods=['GET', 'POST'])
def home():

	if development:
		# Read contents
		read_contents.read_folders()
		read_contents.read_contents()

	return flask.render_template('home.html', content=ws.contents["Introduction"])

# Graphs page
@app.route('/graphs_page', methods=['GET', 'POST'])
def graphs_page():

	if development:
		# Read contents
		read_contents.read_folders()
		read_contents.read_contents()

	return flask.render_template('graphs.html', content=ws.contents["graphs"])

if __name__ == '__main__':
	app.run(debug=True)