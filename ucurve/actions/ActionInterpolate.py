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

from ucurve.ValueFile import ValueFile
from ucurve.MinMax import MinMax
from ucurve.Interpolation import LinearInterpolator, CSplineInterpolator
from ucurve.Sweeper import Sweeper

class ActionInterpolate(object):
	def __init__(self, cmd, args):
		values = ValueFile(args.xyfile)
		minmax = MinMax().feed(values)
		interpolator_class = {
			"linear":		LinearInterpolator,
			"cspline":		CSplineInterpolator,
		}.get(args.algorithm)
		if interpolator_class is None:
			raise Exception(NotImplemented)

		interpolator = interpolator_class(values.points)
		if args.xmin is None:
			minval = minmax.xmin.x
		else:
			minval = args.xmin
		if args.xmax is None:
			maxval = minmax.xmax.x
		else:
			maxval = args.xmax
		for x in Sweeper(minval = minval, maxval = maxval, stepcnt = args.steps, logarithmic = args.logarithmic):
			print("%f %f" % (x, interpolator[x]))
