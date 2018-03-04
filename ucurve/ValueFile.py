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

import collections

class ValueFile(object):
	def __init__(self, filename):
		self._filename = filename
		self._values = self._read_values()

	def _read_values(self):
		values = collections.OrderedDict()
		with open(self._filename) as f:
			for line in f:
				line = line.strip()
				if line.startswith("#") or (line == ""):
					continue
				(x, y) = line.split()
				x = float(x)
				y = float(y)
				values[x] = y
		return values

	@property
	def points(self):
		return list(self)

	def __iter__(self):
		return iter(self._values.items())

	def __len__(self):
		return len(self._values)

	def __str__(self):
		return "Values<%s, %d points>" % (self._filename, len(self))
