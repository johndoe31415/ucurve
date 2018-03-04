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

class MinMax(object):
	_Point = collections.namedtuple("Point", [ "x", "y", "info" ])

	def __init__(self):
		self._ysum = 0
		self._valcnt = 0
		self._xmin = None
		self._xmax = None
		self._ymin = None
		self._ymax = None
		self._yabsmin = None
		self._yabsmax = None

	@property
	def have_data(self):
		return self._valcnt > 0

	@property
	def yavg(self):
		return self._ysum / self._valcnt

	@property
	def xmin(self):
		return self._xmin

	@property
	def xmax(self):
		return self._xmax

	@property
	def ymin(self):
		return self._ymin

	@property
	def ymax(self):
		return self._ymax

	@property
	def yabsmin(self):
		return self._yabsmin

	@property
	def yabsmax(self):
		return self._yabsmax

	def feed(self, iteratable):
		for (x, y) in iteratable:
			self.add(x, y)
		return self

	def _eval(self, oldpt, newpt, evalfunction):
		if evalfunction(oldpt, newpt):
			return newpt
		else:
			return oldpt

	def add(self, x, y, info = None):
		point = self._Point(x = x, y = y, info = info)
		if not self.have_data:
			self._xmin = point
			self._xmax = point
			self._ymin = point
			self._ymax = point
			self._yabsmin = point
			self._yabsmax = point
		else:
			self._xmin = self._eval(self._xmin, point, lambda old, new: new.x < old.x)
			self._xmax = self._eval(self._xmax, point, lambda old, new: new.x > old.x)
			self._ymin = self._eval(self._ymin, point, lambda old, new: new.y < old.y)
			self._ymax = self._eval(self._ymax, point, lambda old, new: new.y > old.y)
			self._yabsmin = self._eval(self._yabsmin, point, lambda old, new: abs(new.y) < abs(old.y))
			self._yabsmax = self._eval(self._yabsmax, point, lambda old, new: abs(new.y) > abs(old.y))

		self._ysum += y
		self._valcnt += 1
