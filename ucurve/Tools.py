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

def _clamp(value, minval, maxval):
	if value < minval:
		return minval
	elif value > maxval:
		return maxval
	else:
		return value

class ExpressionTools(object):
	_EXPRESSION_PREDEFS = {
		"pow":		pow,
		"round":	round,
		"ceil":		math.ceil,
		"floor":	math.floor,
		"exp":		math.exp,
		"pi":		math.pi,
		"sin":		math.sin,
		"cos":		math.cos,
		"log":		math.log,
		"clamp":	_clamp,
	}

	@classmethod
	def eval_expression(cls, expression, env = None):
		if env is None:
			env = { }
		else:
			env = dict(env)

		forbidden_keywords = set(cls._EXPRESSION_PREDEFS) & set(env)
		if len(forbidden_keywords) > 0:
			raise Exception("Forbidden keywords used as variable names: %s" % (", ".join(sorted(forbidden_keywords))))
		env.update(cls._EXPRESSION_PREDEFS)
		return eval(expression, { }, env)

class CTypeTools(object):
	def _uint(bit):
		return (0, (2 ** bit) - 1)

	def _sint(bit):
		return (-(2 ** (bit - 1)), (2 ** (bit - 1)) - 1)

	_TYPES = [
		(_uint(8), "uint8_t"),
		(_sint(8), "int8_t"),
		(_uint(16), "uint16_t"),
		(_sint(16), "int16_t"),
		(_uint(32), "uint32_t"),
		(_sint(32), "int32_t"),
		(_uint(64), "uint64_t"),
		(_sint(64), "int64_t"),
	]

	@classmethod
	def get_type(cls, values):
		minval = min(values)
		maxval = max(values)
		for ((type_minval, type_maxval), typename) in cls._TYPES:
			if (type_minval <= minval <= type_maxval) and (type_minval <= maxval <= type_maxval):
				return typename
		raise Exception("No type found that fits values from %d to %d." % (minval, maxval))
