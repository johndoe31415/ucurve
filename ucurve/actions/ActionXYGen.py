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

from ucurve.Sweeper import Sweeper
from ucurve.Tools import ExpressionTools

class ActionXYGen(object):
	def __init__(self, cmd, args):
		fvars = { }
		for keyvalue in args.var:
			(varname, expression) = keyvalue.split("=", maxsplit = 1)
			value = ExpressionTools.eval_expression(expression, fvars)
			fvars[varname] = value

		with open(args.outfile or "/dev/stdout", "w") as f:
			print("# Y(%s) = %s" % (args.xvar, args.formula), file = f)
			for (x, y) in sorted(fvars.items()):
				print("#    %s = %f" % (x, y), file = f)
			print(file = f)
			for x in Sweeper(minval = args.xmin, maxval = args.xmax, stepcnt = args.steps, logarithmic = args.logarithmic):
				fvars[args.xvar] = x
				y = ExpressionTools.eval_expression(args.formula, fvars)
				print("%f %f" % (x, y), file = f)
