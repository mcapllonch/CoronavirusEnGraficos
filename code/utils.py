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

Contain useful functions
"""
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt


def str2date(s, format_):
	""" Convert a date from str to datetime.date object """
	return datetime.strptime(s, format_).date()

def sort_by_date(dates, x):
	""" Sort a list/array of indices or data by their corresponding dates """
	dates_ = sorted(dates)
	print(dates)
	print('')
	print(dates_)
	print('')
	argsort = np.argsort(dates)
	print(argsort)
	print('')
	dates_ = []
	x_ = []
	for i in argsort:
		dates_.append(dates[i])
		x_.append(x[i])
	print(dates_)
	print('')
	return dates_, x_

def configure_axes(ax, xlims, xlabel=None, ylabel=None, title=None):
	""" Do the most common tasks of preparing an axes frame for a figure """
	plt.xticks(rotation=45)
	ax.set_xlabel(xlabel)
	ax.set_ylabel(ylabel)
	ax.legend()
	ax.set_xlim(*xlims)
	ax.grid(True, color='#D3D3D3')
	ax.set_title(title)