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

import os
import sys
import datetime
import collections
import math
import mako.lookup
import json
from ucurve.Tools import ExpressionTools, CTypeTools
from ucurve.MinMax import MinMax

_PointWithError = collections.namedtuple("PointWithError", [ "x", "y", "error" ])

def _absmax(a, b):
	if abs(a) > abs(b):
		return a
	else:
		return b

class ActionCodeGen(object):
	def __init__(self, cmd, args):
		self._args = args

		# Read values from file first
		values = self._read_values()

		if self._args.verbose:
			print("Read %d values from XY file." % (len(values)), file = sys.stderr)

		# Then transform them according to X/Y rules
		values = self._transform_values(values)

		if self._args.verbose:
			print("%d transformed values." % (len(values)), file = sys.stderr)

		# Filter the ones that do not fit min/max criteria
		self._undecimated_values = [ (x, y) for (x, y) in sorted(self._filter_minmax(values).items()) ]

		if self._args.verbose:
			print("%d undecimated values." % (len(self._undecimated_values)), file = sys.stderr)

		# Round values and take closest ones
		self._rounded_values = self._round_values(self._undecimated_values)

		if self._args.verbose:
			print("%d rounded values." % (len(self._rounded_values)), file = sys.stderr)

		# Determine values to be used as cornerpoints
		(self._cornerpoints, self._max_error) = self._thin_values(self._rounded_values)
		if self._args.verbose:
			print("%d input points reduced to %d points with %.2f max error." % (len(values), len(self._cornerpoints), self._max_error), file = sys.stderr)

		# Emit code
		self._emit_code()

		# Analyze result
		self._analyze_result()

	def _emit_code(self):
		(out_xname, out_yname) = self._args.out_varnames.split(",")
		xvalues = [ point[0] for point in self._cornerpoints ]
		yvalues = [ point[1] for point in self._cornerpoints ]
		env = {
			"in_type":				CTypeTools.get_type(xvalues),
			"extd_in_type":			CTypeTools.get_type(xvalues + [ min(xvalues) - 10, max(xvalues) + 10 ]),
			"out_type":				CTypeTools.get_type(yvalues),
			"idx_type":				CTypeTools.get_type([ 0, len(self._cornerpoints) ]),
			"win_mul_yspan_type":	CTypeTools.get_type([ (p1.x - p0.x - 1) * (p1.y - p0.y) for (p0, p1) in zip(self._cornerpoints, self._cornerpoints[1:]) ]),
			"yspan_type":			CTypeTools.get_type([ p1.y - p0.y for (p0, p1) in zip(self._cornerpoints, self._cornerpoints[1:]) ]),
			"lup_name":				self._args.funcname,
			"points":				self._cornerpoints,
			"filename":				self._args.outfile,
			"min":					self._cornerpoints[0],
			"max":					self._cornerpoints[-1],
			"max_error":			self._max_error,
			"struct_lookup":		self._args.struct_lookup,
			"sqrt":					math.sqrt,
			"orig_data":			self._undecimated_values,
			"out_xname":			out_xname,
			"out_yname":			out_yname,
			"today":				datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
			"flip_axis":			self._args.gnuplot_flipaxis,
			"flip_diff":			self._args.gnuplot_flipdiff,
		}

		tlup = mako.lookup.TemplateLookup([ "." ], strict_undefined = True, input_encoding = "utf-8")

		try:
			os.makedirs(self._args.outdir)
		except FileExistsError:
			pass

		generate_extensions = [ "c", "h" ]
		if self._args.gnuplot:
			generate_extensions.append("gpl")

		for extension in generate_extensions:
			template = tlup.get_template("lookup_template." + extension)
			with open(self._args.outdir + "/" + self._args.outfile + "." + extension, "w") as f:
				f.write(template.render(**env))

	def _read_values(self):
		values = { }
		with open(self._args.xyfile) as f:
			for line in f:
				line = line.strip()
				if line.startswith("#") or (line == ""):
					continue
				(x, y) = line.split()
				x = float(x)
				y = float(y)
				values[x] = y
		return values

	def _transform_values(self, values):
		(xname, yname) = self._args.in_varnames.split(",")
		result = { }
		for (x_in, y_in) in sorted(values.items()):
			env = {
				xname: x_in,
				yname: y_in,
			}
			x_out = ExpressionTools.eval_expression(self._args.xval, env)
			y_out = ExpressionTools.eval_expression(self._args.yval, env)
			result[x_out] = y_out
		return result

	@staticmethod
	def _interpolate(xvalue, low, high):
		xspan = high[0] - low[0]
		yspan = high[1] - low[1]
		xwin = xvalue - low[0]
		return low[1] + (xwin / xspan) * yspan

	def _interpolation_error(self, values):
		assert(len(values) >= 3)
		first = values[0]
		last = values[-1]
		max_error = 0
		for (x, y) in values[1 : -1]:
			y_interp = self._interpolate(x, first, last)
			error = y_interp - y
			max_error = _absmax(max_error, error)
		return max_error

	def _filter_minmax(self, values):
		result = { }
		for (x, y) in values.items():
			if (self._args.xmin is not None) and (x < self._args.xmin):
				continue
			if (self._args.xmax is not None) and (x > self._args.xmax):
				continue
			result[x] = y
		return result

	def _round_values(self, points):
		result = collections.defaultdict(list)
		for (x, y) in points:
			rndx = round(x)
			rndy = round(y)
			abserr = abs(rndx - x)
			result[rndx].append((abserr, rndy))

		result_list = [ ]
		for (x, ylist) in sorted(result.items()):
			ylist.sort()
			result_list.append((x, ylist[0][1]))
		return result_list

	def _thin_values(self, points):
		next_error = None
		max_error = 0
		index = 0
		result = [ ]
		while index < len(points):
			result.append(_PointWithError(x = points[index][0], y = points[index][1], error = next_error))
			low = result[-1]

			next_error = 0
			next_index = index + 1
			for potential_high_index in range(index + 3, len(points)):
				error = self._interpolation_error(points[index : potential_high_index])
				if abs(error) <= abs(self._args.max_error_y):
					next_index = potential_high_index
					next_error = _absmax(next_error, error)
					max_error = _absmax(max_error, error)
				else:
					break
			index = next_index

		return (result, max_error)

	def _analyze_result(self):
		if self._args.yaoi is None:
			return

		(xname, yname) = self._args.out_varnames.split(",")
		(yaoimin, yaoimax) = [ float(v) for v in self._args.yaoi.split(",") ]

		values_in_yaoi = [ (x, y) for (x, y) in self._undecimated_values if yaoimin <= y <= yaoimax ]
		minmax = MinMax()
		for (x, y) in values_in_yaoi:
			minmax.add(x, y)

		diff_minmax = MinMax()
		for ((x0, y0), (x1, y1)) in zip(values_in_yaoi, values_in_yaoi[1:]):
			dy = y1 - y0
			dx = x1 - x0
			if dx != 0:
				dy_over_dx = dy / dx
				x = (x0 + x1) / 2
				y = (y0 + y1) / 2
				diff_minmax.add(x, dy_over_dx, info = y)

		if not self._args.json_analysis:
			print("Analyzing area-of-interest range of %s: %.1f - %.1f (span size %.1f)" % (yname, yaoimin, yaoimax, yaoimax - yaoimin))
			if minmax.have_data:
				print("    %d values in that range, %s from %.1f - %.1f, %s from %.1f - %.1f" % (len(values_in_yaoi), xname, minmax.xmin.x, minmax.xmax.x, yname, minmax.ymin.y, minmax.ymax.y))
			if diff_minmax.have_data:
				print("    d%s/d%s:" % (yname, xname))
				print("        Absolute d%s/d%s minimum at %s = %.1f, %.1f %s/%s (at %.1f %s)" % (yname, xname, xname, diff_minmax.yabsmin.x, diff_minmax.yabsmin.y, yname, xname, diff_minmax.yabsmin.info, yname))
				print("        Absolute d%s/d%s maximum at %s = %.1f, %.1f %s/%s (at %.1f %s)" % (yname, xname, xname, diff_minmax.yabsmax.x, diff_minmax.yabsmax.y, yname, xname, diff_minmax.yabsmax.info, yname))
				print("        Average: %.2f %s/%s = %.2f %s/%s" % (diff_minmax.yavg, yname, xname, 1 / diff_minmax.yavg, xname, yname))
		else:
			result = {
				"xname":	xname,
				"yname":	yname,
			}
			if minmax.have_data:
				result["xspan"] = [ minmax.xmin.x, minmax.xmax.x ]
			if minmax.have_data:
				result["yspan"] = [ minmax.ymin.y, minmax.ymax.y ]
			if diff_minmax.have_data:
				result["dy_dx"] = {
					"absmin": {
						"x":		diff_minmax.yabsmin.x,
						"dy_dx":	diff_minmax.yabsmin.y,
						"y":		diff_minmax.yabsmin.info,
					},
					"absmax": {
						"x":		diff_minmax.yabsmax.x,
						"dy_dx":	diff_minmax.yabsmax.y,
						"y":		diff_minmax.yabsmax.info,
					},
					"avg_dy_dx": diff_minmax.yavg,
				}
			print(json.dumps(result))
