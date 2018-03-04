#!/bin/bash
#
#

# Generate X/Y file that follows the formula from the datasheet
# Datasheet: Vishay 2381 640 3/4/6... NTC Thermistors, Accuracy Line
./ucurve.py xygen \
	--outfile ntc.txt \
	--steps 1000 \
	--xvar TC \
	--xmin -40 \
	--xmax 150 \
	--var "Rref=100e3" \
	--var "A=-9.094" \
	--var "B=2251.74" \
	--var "C=229098" \
	--var "D=-27448200" \
	"Rref * exp(A + (B/(TC+273.15)) + (C / (TC+273.15)**2) + (D/(TC+273.15)**3))"

# Then generate code from the X/Y file, assuming an 8 bit ADC and 47kOhm series
# resistor
./ucurve.py codegen \
	--outfile adu2temp_degc \
	--funcname adu2temp_degc \
	--gnuplot \
	--verbose \
	--max-error 1 \
	--in-varnames "T,R" \
	--out-varnames "ADU,°C" \
	--yaoi 15,80 \
	--xmin 0 \
	--xmax 255 \
	--xval '0xff * R / (R + 47e3)' \
	--yval 'T' \
	ntc.txt

