#	ucurve - Minify and generate X/Y tables into microcontroller code.
#	Copyright (C) 2017-2017 Johannes Bauer
#
#	This file is part of ucurve.
#
#	ucurve is free software; you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation; this program is ONLY licensed under
#	version 3 of the License, later versions are explicitly excluded.
#
#	ucurve is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with ucurve; if not, write to the Free Software
#	Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#	Johannes Bauer <JohannesBauer@gmx.de>

import math

class Sweeper(object):
	def __init__(self, minval, maxval, stepcnt, logarithmic = False):
		self._minval = minval
		self._maxval = maxval
		self._stepcnt = stepcnt
		if not logarithmic:
			self._method = self._sweep_lin
		else:
			self._method = self._sweep_log

	def _sweep_lin(self):
		step = (self._maxval - self._minval) / (self._stepcnt - 1)
		for i in range(self._stepcnt):
			yield self._minval + (step * i)

	def _sweep_log(self):
		lspan = math.log(self._maxval - self._minval + 1)
		for i in range(self._stepcnt):
			yield self._minval - 1 + math.exp(lspan / (self._stepcnt - 1) * i)

	def __iter__(self):
		return self._method()

if __name__ == "__main__":
	for value in Sweeper(1, 10, 4):
		print(value)

	for value in Sweeper(1, 1000, 4, logarithmic = True):
		print(value)
