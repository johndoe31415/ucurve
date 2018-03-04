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
from ucurve.Matrix import TridiagonalMatrix
from ucurve.Polynomial import Polynomial

class Interpolator(object):
	def __init__(self, points):
		if len(points) < 2:
			raise Exception("Need at least two points for interpolation.")
		self._points = list(sorted(points))
		self._calculate()

	def _calculate(self):
		raise Exception(NotImplemented)

	def __getitem__(self, x):
		raise Exception(NotImplemented)

class PiecewisePolynomialInterpolator(Interpolator):
	_PolyStartingAt = collections.namedtuple("PolyStartingAt", [ "xoffset", "poly" ])

	def __init__(self, points):
		self._polys = [ ]
		self._last_poly_idx = None
		Interpolator.__init__(self, points)
		self._polys.sort(key = lambda x: x.xoffset)

	def _add_poly(self, xoffset, poly):
		self._polys.append(self._PolyStartingAt(xoffset = xoffset, poly = poly))

	def __index_eval(self, x, index):
		poly = self._polys[index]
		if index == 0:
			# First poly
			if x < poly.xoffset:
				# Found
				return 0
			else:
				# Search greater
				return 1
		elif index == len(self._polys) - 1:
			if x >= poly.xoffset:
				# Found
				return 0
			else:
				# Search smaller
				return -1
		else:
			next_poly = self._polys[index + 1]
			if poly.xoffset <= x < next_poly.xoffset:
				# Found
				return 0
			elif x < poly.xoffset:
				# Search smaller
				return -1
			else:
				# Search greater
				return 1

	def __find_poly_idx(self, x):
		if (self._last_poly_idx is not None) and (self.__index_eval(x, self._last_poly_idx) == 0):
			return self._last_poly_idx
		if len(self._polys) == 1:
			return 0

		minguess = 0
		maxguess = len(self._polys) - 1
		while minguess != maxguess:
			guess = (minguess + maxguess) // 2
			cmp_result = self.__index_eval(x = x, index = guess)
			if cmp_result == 0:
				return guess
			elif cmp_result == -1:
				maxguess = guess - 1
			else:
				minguess = guess + 1
		return minguess

	def __getitem__(self, x):
		self._last_poly_idx = self.__find_poly_idx(x)
		(xoffset, poly) = self._polys[self._last_poly_idx]
		return poly[x]

class LinearInterpolator(PiecewisePolynomialInterpolator):
	def _calculate(self):
		for (pt0, pt1) in zip(self._points, self._points[1:]):
			poly = Polynomial.create_linear(pt0, pt1)
			self._add_poly(pt0[0], poly)

class CSplineInterpolator(PiecewisePolynomialInterpolator):
	def _calculate(self):
		h = [ ]
		g = [ ]
		for i in range(1, len(self._points)):
			h.append(self._points[i][0] - self._points[i - 1][0])

		M = TridiagonalMatrix(len(self._points) - 2)
		for i in range(2, len(self._points)):
			g.append(3 * (((self._points[i][1] - self._points[i - 1][1]) / h[i-1]) - ((self._points[i - 1][1] - self._points[i - 2][1]) / h[i - 2])))
			row = [ h[i - 2], 2 * (h[i - 2] + h[i - 1]), h[i - 1] ]
			M.set_row(i - 1, row)

		cs = M.solve(g)
		cs.insert(0, 0)
		cs.append(0)

		for i in range(1, len(self._points)):
			a = self._points[i - 1][1]
			b = ((self._points[i][1] - self._points[i - 1][1]) / h[i - 1]) - (h[i - 1] * (2 * cs[i - 1] + cs[i]) / 3)
			c = cs[i - 1]
			d = (cs[i] - cs[i - 1]) / (3 * h[i - 1])

			xoffset = self._points[i - 1][0]
			poly = Polynomial([ a, b, c, d ], xoffset = -xoffset)
			self._add_poly(xoffset, poly)

if __name__ == "__main__":
#	interp = LinearInterpolation([ (1, 10), (2, 20) ])
#	assert(interp[0] == 0)
#	assert(interp[3] == 30)
#	assert(interp[10] == 100)
#
#	interp = LinearInterpolation([ (5, 3), (6, -3) ])
#	assert(interp[5] == 3)
#	assert(interp[6] == -3)
#	assert(interp[5.4] > 0)
#	assert(interp[5.5] == 0)
#	assert(interp[5.6] < 0)
#
#	interp = CubicSpline([ (5, 3), (6, -3), (4, 4) ])

	points = [
		(1, 8),
		(7, 10),
		(12, 7),
		(15, 8),
		(19, 7),
	]
	csi = CSplineInterpolator(points)
	for i in range(25):
		print(csi[i])
