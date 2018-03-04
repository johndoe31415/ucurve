#!/bin/bash
#
#

# Generate X/Y file that follows the formula from the datasheet
# Datasheet: Vishay NTC thermistors, 2381 640 3/4/6... datasheet, Accuracy Line
# 100kOhm NTC (brown, black, yellow, gold): R_25 = 100kOhm, B_25/85 = 4190K +- 1.5% 5% accuracy, serial 2381 640 63104
# Parameter type 11

./ucurve.py xygen \
	--outfile ntc.txt \
	--steps 1000 \
	--xvar TC \
	--xmin -40 \
	--xmax 150 \
	--var "Rref=100e3" \
	--var "A=-16.0349" \
	--var "B=5459.339" \
	--var "C=-191141" \
	--var "D=-3328322" \
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
	--xval 'clamp(0xff * R / (R + 47e3), 0, 255)' \
	--yval 'T' \
	ntc.txt

