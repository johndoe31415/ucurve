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

class Polynomial(object):
	def __init__(self, coeffs, xoffset = None):
		self._coeffs = tuple(coeffs)
		self._xoffset = xoffset

	@classmethod
	def create_linear(cls, pt0, pt1):
		(x0, y0) = pt0
		(x1, y1) = pt1
		b = (y1 - y0) / (x1 - x0)
		a = y0
		return cls([ a, b ])

	def __getitem__(self, x):
		if self._xoffset is not None:
			x += self._xoffset
		result = 0
		for (exponent, coeff) in enumerate(self._coeffs):
			result += coeff * (x ** exponent)
		return result

	def diff(self):
		return Polynomial([ (coeff * (exponent + 1)) for (exponent, coeff) in enumerate(self._coeffs[1:])])

	@classmethod
	def _varname(cls, number, first_var = "a", index = None):
		if index is None:
			return chr(ord("a") + number)
		else:
			return chr(ord("a") + number) + "_%d" % (index)

	@classmethod
	def equals(cls, degree, x, y, index = None, diffed = 0):
		lhs = { }
		if y is not None:
			# Have a concrete RHS value for Y
			for exponent in range(degree + 1 - diffed):
				varname = cls._varname(exponent + diffed, index = index)
				coeff = 1
				for i in range(diffed):
					coeff *= exponent + i + 1
				lhs[varname] = coeff * x ** exponent
			rhs = y
		else:
			# Poly equals poly
			if index is None:
				index = 0

			# Create sub-polys
			lhs_eqn = cls.equals(degree = degree, x = x, y = 0, index = index, diffed = diffed)
			rhs_eqn = cls.equals(degree = degree, x = x, y = 0, index = index + 1, diffed = diffed)

			# Merge
			for (varname, coeff) in lhs_eqn[0].items():
				lhs[varname] = coeff
			for (varname, coeff) in rhs_eqn[0].items():
				lhs[varname] = -coeff
			rhs = 0
		return (lhs, rhs)

	@staticmethod
	def _flt_fmt(value):
		return "%.3f" % (value)

	def __repr__(self):
		elements = [ ]
		first = True
		for (exponent, value) in reversed(list(enumerate(self._coeffs))):
			if value == 0:
				continue

			if not first:
				if value < 0:
					sign = " - "
				else:
					sign = " + "
			else:
				if value < 0:
					sign = "-"
				else:
					sign = ""
				first = False

			if exponent > 1:
				varbl = "x^%d" % (exponent)
			elif exponent == 1:
				varbl = "x"
			else:
				varbl = ""
			value = abs(value)
			if (value == 1) and (exponent != 0):
				value = ""
			else:
				value = self._flt_fmt(value)
			elements.append("%s%s%s" % (sign, value, varbl))
		if len(elements) == 0:
			elements = [ "0" ]
		poly = "".join(elements)
		return poly
