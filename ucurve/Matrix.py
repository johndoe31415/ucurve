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

class MatrixException(Exception): pass
class SolveException(MatrixException): pass
class InvalidParametersException(SolveException): pass
class SingularEquationSystemException(SolveException): pass
class InvalidArgumentException(MatrixException): pass

class Matrix(object):
	def __init__(self, values):
		self._data = list(list(row) for row in values)
		self._m = len(self._data)
		self._n = len(self._data[0])
		assert(len(row) == self._n for row in self._data)

	@property
	def m(self):
		return self._m

	@property
	def n(self):
		return self._n

	@property
	def row_count(self):
		return self.m

	@property
	def col_count(self):
		return self.n

	def __getitem__(self, value):
		(i, j) = value
		return self._data[i - 1][j - 1]

	def vmul(self, vector):
		if len(vector) != self.n:
			raise InvalidArgumentException("Tried to multiply a vector of length %d with a %d x %d matrix (need a %d element vector)." % (len(vector), self.m, self.n, self.n))
		result = [ ]
		for i in range(1, self.m + 1):
			value = 0
			for j in range(1, self.n + 1):
				value += self[(i, j)] * vector[j - 1]
			result.append(value)
		return result

	def dump(self):
		print("m x n = %d x %d %s:" % (self.m, self.n, self.__class__.__name__))
		for i in range(1, self.m + 1):
			line = [ ]
			for j in range(1, self.n + 1):
				line.append(self[(i, j)])
			print(" ".join("%8.3f" % (value) for value in line))
		print()

class TridiagonalMatrix(Matrix):
	def __init__(self, n):
		self._m = n
		self._n = n
		self._data = [ [ 0, 0, 0 ] for i in range(self._n) ]

	@classmethod
	def from_data(cls, matrix_data):
		if len(matrix_data) != len(matrix_data[0]):
			raise InvalidArgumentException("Not a square matrix.")
		matrix = cls(len(matrix_data))
		for i in range(1, matrix.n + 1):
			rowdata = matrix_data[i - 1][max(0, i - 2) : i + 1]
			matrix.set_row(i, rowdata)
		return matrix

	def set_row(self, i, values):
		if len(values) == 2:
			if i == 1:
				self._data[i - 1] = [ 0, values[0], values[1] ]
			elif i == self.n:
				self._data[i - 1] = [ values[0], values[1], 0 ]
			else:
				raise InvalidArgumentException("2 values given for rows different than first and last.")
		else:
			if len(values) != 3:
				raise InvalidArgumentException("Expected three values, got %d." % (len(values)))
			self._data[i - 1] = list(values)
		return self

	def solve(self, rhs):
		"""Apply Tridiagonal Matrix Algorithm (Thomas-Algorithm). Modifies
		matrix data itself."""
		if len(rhs) != self.m:
			raise InvalidParametersException("RHS vector with %d entries given, expected %d." % (len(rhs), self.m))
		rhs = list(rhs)

		for (i, ((a, b, c), d)) in enumerate(zip(self._data, rhs)):
			if i > 0:
				cprev = self._data[i - 1][2]
				dprev = rhs[i - 1]
			else:
				cprev = 0
				dprev = 0

			cx = c / (b - cprev * a)
			dx = (d - (dprev * a)) / (b - (cprev * a))
			self._data[i][2] = cx
			rhs[i] = dx


		for i in reversed(range(len(rhs) - 1)):
			c = self._data[i][2]
			rhs[i] = rhs[i] - (c * rhs[i + 1])

		return rhs

	def __getitem__(self, value):
		(i, j) = value
		if abs(i - j) <= 1:
			return self._data[i - 1][j - i + 1]
		else:
			return 0

if __name__ == "__main__":
	import random

	M = Matrix([[ 1, 2, 3 ], [ 4, 5, 6 ] ])
	M.dump()
	assert(M.row_count == 2)
	assert(M.col_count == 3)
	assert(M[(1, 1)] == 1)
	assert(M[(1, 2)] == 2)
	assert(M[(2, 1)] == 4)
	assert(M.vmul([ -11, 13, -17 ]) == [ -36, -81 ])

	mdata = [
		[ 1, 2, 0, 0, 0 ],
		[ 4, 9, 2, 0, 0 ],
		[ 0, 1, 3, 5, 0 ],
		[ 0, 0, 9, 4, 2 ],
		[ 0, 0, 0, 3, 3 ],
	]
	T = TridiagonalMatrix.from_data(mdata)
	T.dump()
	sol = T.solve([ 3, 5, 7, 9, 11 ])

	T = TridiagonalMatrix.from_data(mdata)
	print(T.vmul(sol))


