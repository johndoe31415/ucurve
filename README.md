# ucurve
µCurve (microcurve) is a tool to generate X/Y curve interpolation tables for
microcontrollers. It is able to decimate the data to reduce the amount of flash
data that is used. Examples for usage is to create functions that translate
from sampled ADU values of a PTC or NTC temperature sensor back into a degree
measurement or a sine table (or some other mathematical function).

# Example
Let's say you have a specific NTC. The datasheet says that the formula to get
resistance from a given temperature in Kelvin is

Rref * exp(A + (B / T) + (C / T^2) + (D / T^3))

Rref is the base temperature at 25°C. A, B, C and D are the type-dependent
variables that you can read from the datasheet. T is the temperature, given in
Kelvin. To make it easier for us, we can restructure the formula to use degrees
Celsius:

Rref * exp(A + (B / (TC+273.15)) + (C / (TC + 273.15)^2) + (D / (TC+273.15)^3))

Now, given some concrete parameters from the datasheet, we can have ucurve calculate an X/Y table:

```
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
```

This is nothing special so far, any spreadsheet software could have given you
that. You end up with a file ntc.txt that contains 1000 data points (as
specified on the command line), swept linearly with TC from -40 to 150:

```
# Y(TC) = Rref * exp(A + (B/(TC+273.15)) + (C / (TC+273.15)**2) + (D/(TC+273.15)**3))
#    A = -16.034900
#    B = 5459.339000
#    C = -191141.000000
#    D = -3328322.000000
#    Rref = 100000.000000

-40.000000 3666321.339250
-39.809810 3620002.366633
[...]
24.664665 101547.246107
24.854855 100666.785039
25.045045 99794.861006
25.235235 98931.383051
[...]
149.619620 1447.850591
149.809810 1440.938148
150.000000 1434.064180
```

This file can be directly fed to gnuplot, if you want to inspect its contents:

```
gnuplot> plot 'ntc.txt' using 1:2 with lines
```

Now let's assume we have this NTC in a target environment where it's sampled by
an ADC. The circuit is simply a series resistor: Vcc -> R -> NTC -> GND. The ADC
samples inbetween R and NTC, i.e. the voltage drop over the NTC. Let's imagine that our series resistor is 47 kOhms. Then the sampled value equals:

```
0xff * Rntc / (Rntc + 47e3)
```

The sampled value, however, is clampled between 0 and 0xff (when the ADC goes into saturation). So let's generate a table for this:

```
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
```

This is a little bit more complicated, but can still be explained easily:
First, we want to generate files that have a `adu2temp_degc` prefix. The
internal function should also be called adu2temp_degc inside out code.
Additionally, we ask ucurve to generate a gnuplot graph file that we can use to
determine visually where the greatest interpolation errors are. We also ask it
to be verbose about generation of the code. The maximum error that we want to
accept is a deviation of +- 1°C (i.e., given in output units). Now we name our
variables: Inside the input file, we have a T / R table (temperature in degrees
Celsius vs resistance of NTC) -- we just generated that table in the last step.

The function we want to generate, however, gets an ADU value from the ADC as
input (i.e., its X value) and is supposed to return °C that correspond to that
value. The Y-area-of-interest (i.e., output Y values) that is going to be of
most use to us is the range from 15°C to 80°C. ucurve is going to show us
detailed information about that area.

We also specify other constraints: Namely, X will only ever range from 0..255
(this is our ADC hardware limit). Then we give two functions to transform X and Y
from the input data to our final function. Concretely, X (the input value of
the generated function) is the sampled ADU value (the calculation seen as
above) and Y (i.e., the return value the generated function) is simply the
temperature in degrees C. This is the result:

```
Read 1000 values from XY file.
1000 transformed values.
1000 undecimated values.
245 rounded values.
1000 input points reduced to 16 points with -1.00 max error.
Analyzing area-of-interest range of °C: 15.0 - 80.0 (span size 65.0)
    341 values in that range, ADU from 49.5 - 196.8, °C from 15.2 - 79.8
    d°C/dADU:
        Absolute d°C/dADU minimum at ADU = 143.4, -0.4 °C/ADU (at 36.4 °C)
        Absolute d°C/dADU maximum at ADU = 49.7, -0.7 °C/ADU (at 79.7 °C)
        Average: -0.46 °C/ADU = -2.20 ADU/°C
```

It shows us that it read 1000 values from the ntc.txt file and, after applying
the X/Y translation formulas, ended up with 245 data points altogether. Then it
decimated them, taking care that the maximal error does not exceed +-1°C.

In the final dataset, the Y-area-of-interest from 15 - 80°C is shown, which
equates to a span of 65°C. In that area of interest, ADU values fall between
49.5 and 196.8. The NTC in this setup is going to be most precise at 36.4°C
because every ADU corresponds to a changes of -0.4°C. At higher temperatures,
i.e, at 79.7°C, it will be least responsive, changing -0.7°C with every ADU.

Let's run the same generation with a less suitable series resistor, such as a
10 kOhm:

```
223 rounded values.
1000 input points reduced to 15 points with -1.00 max error.
Analyzing area-of-interest range of °C: 15.0 - 80.0 (span size 65.0)
    341 values in that range, ADU from 135.4 - 239.9, °C from 15.2 - 79.8
    d°C/dADU:
        Absolute d°C/dADU minimum at ADU = 145.3, -0.5 °C/ADU (at 75.4 °C)
        Absolute d°C/dADU maximum at ADU = 239.8, -1.5 °C/ADU (at 15.3 °C)
        Average: -0.70 °C/ADU = -1.43 ADU/°C
```

We see that the worst-case sensitivity in the Y-area-of-interest is worse than
half of what we get with our 47 kOhm resistor, i.e., about -1.5 °C per ADU.

Going back to our original 47 kOhm resistor, we can now also take a look at the
generated code:

```
[...]
/* Maximum error: (y_true - y_interpolated) = -1.00 °C */
static const struct lookup_entry_t lookup_table[] = {
	{ .x = 28, .y = 149 },
	{ .x = 41, .y = 124 },		/* +1.0 °C */
	{ .x = 52, .y = 109 },		/* +1.0 °C */
[...]
	{ .x = 238, .y = -25 },		/* -0.9 °C */
	{ .x = 243, .y = -33 },		/* -1.0 °C */
	{ .x = 247, .y = -40 },		/* -1.0 °C */
};
```

And also at the gnuplot graph:

# License
GNU GPL-v3.
