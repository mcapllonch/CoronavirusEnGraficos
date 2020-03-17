"""
Contain useful functions
"""
from datetime import datetime


def str2date(s, format_):
	""" Convert a date from str to datetime.date object """
	return datetime.strptime(s, format_).date()