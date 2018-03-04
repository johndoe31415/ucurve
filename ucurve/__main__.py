#!/usr/bin/python3
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

import sys
from ucurve.FriendlyArgumentParser import baseint
from ucurve.MultiCommand import MultiCommand
from ucurve.actions.ActionXYGen import ActionXYGen
from ucurve.actions.ActionCodeGen import ActionCodeGen
from ucurve.actions.ActionInterpolate import ActionInterpolate

mc = MultiCommand()

def genparser(parser):
	parser.add_argument("-v", "--var", metavar = "var=value", action = "append", type = str, default = [ ], help = "Substitute the given variable in the formula. Can be specified multiple times.")
	parser.add_argument("--xmin", metavar = "value", type = float, required = True, help = "Minimum X value to use. Mandatory argument.")
	parser.add_argument("--xmax", metavar = "value", type = float, required = True, help = "Maximum X value to use. Mandatory argument.")
	parser.add_argument("--xvar", metavar = "symbol", type = str, default = "x", help = "Variable to use for sweeping X. Defaults to %(default)s.")
	parser.add_argument("-s", "--steps", metavar = "cnt", type = int, default = 100, help = "Number of steps to interpolate.")
	parser.add_argument("-l", "--logarithmic", action = "store_true", help = "Sweep through X in a logarithmically. Default is to do a linear sweep.")
	parser.add_argument("-o", "--outfile", metavar = "filename", help = "Write output to the given filename.")
	parser.add_argument("formula", type = str, help = "Formula used to compute y from a given x value.")
mc.register("xygen", "Generate an X/Y file from a formula and parameters", genparser, action = ActionXYGen)

def genparser(parser):
	parser.add_argument("--in-varnames", metavar = "xname,yname", type = str, default = "x,y", help = "Rename X and Y variables (separated by comma) that come from xyfile. Defaults to '%(default)s'.")
	parser.add_argument("--out-varnames", metavar = "xname,yname", type = str, default = "x,y", help = "Rename X and Y variables (separated by comma) that comprise the final mapping after applying mangling formulas. Defaults to '%(default)s'.")
	parser.add_argument("--yaoi", metavar = "min,max", type = str, help = "Define the Y area of interest for analysis. Does not affect the computation at all, just gives out some numbers about that area.")
	parser.add_argument("--json-analysis", action = "store_true", help = "When printing YAOI analysis data, do not use human-readable text, but rather output JSON data. This allows machine-post-processing (such as iterative changing of parameters by a script calling ucurve).")
	parser.add_argument("--xval", metavar = "formula", type = str, default = "x", help = "Default mangling formula to apply to x. Defaults to '%(default)s'.")
	parser.add_argument("--yval", metavar = "formula", type = str, default = "y", help = "Default mangling formula to apply to y. Defaults to '%(default)s'.")
	parser.add_argument("--xmin", metavar = "value", type = baseint, help = "Minimum X value that will ever considered valid.")
	parser.add_argument("--xmax", metavar = "value", type = baseint, help = "Maximum X value that will ever considered valid.")
	parser.add_argument("-e", "--max-error-y", metavar = "ydev", type = float, default = 10, help = "Maximum error to stay below, specified as abs(y_true - y_interp). Defaults to %(default)d.")
	parser.add_argument("-v", "--verbose", action = "store_true", help = "Be more verbose during code generation.")
	parser.add_argument("--struct-lookup", choices = [ "default", "avr-progmem" ], default = "default", help = "Specify how lookup of in-program structure data is performed. Can be any of %(choices)s and defaults to %(default)s.")
	parser.add_argument("--gnuplot", action = "store_true", help = "Also output a gnuplot file that plots input/output mapping, error graphs and deviation from original.")
	parser.add_argument("--gnuplot-flipaxis", action = "store_true", help = "When creating gnuplot output, flip X and Y axis.")
	parser.add_argument("--gnuplot-flipdiff", action = "store_true", help = "When creating gnuplot output, compute dX/dY instead of dY/dX on axis X1Y2.")
	parser.add_argument("--funcname", metavar = "name", type = str, default = "lookup", help = "Lookup function name. Defaults to '%(default)s'.")
	parser.add_argument("--outdir", metavar = "path", type = str, default = ".", help = "Directory to write all outfiles to. By default, these files are created in the working directory.")
	parser.add_argument("--outfile", metavar = "prefix", type = str, default = "lookup", help = "Prefix to use for the output .c/.h filename. Defaults to '%(default)s'.")
	parser.add_argument("xyfile", type = str, help = "X/Y file that specifies input data.")
mc.register("codegen", "Generate code to interpolate Y from a given X", genparser, action = ActionCodeGen)

def genparser(parser):
	parser.add_argument("-a", "--algorithm", choices = [ "cspline", "linear" ], default = "cspline", help = "Algorithm for interpolation. Can be one of %(choices)s, defaults to %(default)s.")
	parser.add_argument("--gnuplot", action = "store_true", help = "Also output a gnuplot file that plots input/output mapping, error graphs and deviation from original.")
	parser.add_argument("--xmin", metavar = "value", type = float, help = "Minimum X value to use. If not specified, minimum in given dataset is used.")
	parser.add_argument("--xmax", metavar = "value", type = float, help = "Maximum X value to use. If not specified, maximum in given dataset is used.")
	parser.add_argument("-s", "--steps", metavar = "cnt", type = int, default = 100, help = "Number of steps to interpolate.")
	parser.add_argument("-l", "--logarithmic", action = "store_true", help = "Sweep through X in a logarithmically. Default is to do a linear sweep.")
	parser.add_argument("xyfile", type = str, help = "X/Y file that specifies input data.")
mc.register("interpolate", "Interpolate a given X/Y table of values using a given algorithm and output more interpolated values", genparser, action = ActionInterpolate)

mc.run(sys.argv[1:])
