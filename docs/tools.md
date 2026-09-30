# Tool catalog

Every tool the calculator offers, as recipe content. Formulas follow the course lecture notes (their notation, e.g. Sallen-Key `R1=mR`, `C1=nC`, `C1` to the output). The recipes in `src/ti84/recipes/` implement this file; the tests in `tests/tools/` hold the numbers.

## Notation

```
### <id> · <MENU LABEL> · <title>
picture:            ≤ 8 lines, each ≤ 26 characters (rows 2-9 of the picture screen)
inputs:             <var> "<prompt>" [kind]            kind: real (default) · complex · list
steps:              <var> <NAME> = <formula as shown> | <expr> | <unit> | <fmt>
answers:            names shown on the answer screen, in order
```

- `var` is the variable the step stores into (`A`–`Z`; lists `L₁`–`L₆`). Names and formulas are display text; `expr` is dialect code.
- `fmt`: `si` (default, helper ZF), `fix2` (ZR, for dB and degrees), `cplx` (ZC). A complex step uses `cplx`.
- `Verdict <Str> <NAME>: <cond> → "<text>" / … / else "<text>"` picks a line of text.
- `Guard <cond> → "<message>"` stops the tool with that message before anything is shown.
- `Poly <var> <NAME> = <list>(<at>) loop <K>` evaluates a coefficient list (highest power first) at a point by Horner's rule; the work shows only the result line.
- `Note "<text>"` adds a line of text to the work.
- Display text writes `w` for ω, `PI` for π, `SQRT(` for √, `j` for the imaginary unit; code writes `pi`, `√(`, `𝑖`.
- Display text never contains `->`: tivars reads it as the store arrow `→`, which ends a string. Pictures use `>` instead.

---

## BASICS · `EEBASIC`

### ohmv · OHM: FIND V · OHMS LAW: FIND V
picture:
```
V ACROSS R, I THROUGH R
V = I*R
```
inputs: `I "I A="` · `R "R Ω="`
steps:
```
V  V = I*R          | I*R | V
P  P = V*I          | V*I | W
```
answers: V, P

### ohmi · OHM: FIND I · OHMS LAW: FIND I
picture: same as ohmv.
inputs: `V "V V="` · `R "R Ω="`
steps:
```
I  I = V/R          | V/R | A
P  P = V*I          | V*I | W
```
answers: I, P

### ohmr · OHM: FIND R · OHMS LAW: FIND R
picture: same as ohmv.
inputs: `V "V V="` · `I "I A="`
steps:
```
R  R = V/I          | V/I | Ω
P  P = V*I          | V*I | W
```
answers: R, P

### rser · SERIES R · RESISTORS IN SERIES
picture:
```
R1, R2, R3 END TO END
SAME CURRENT IN EACH
TYPE 0 FOR A MISSING R
```
inputs: `A "R1 Ω="` · `B "R2 Ω="` · `C "R3 Ω="`
steps:
```
S  RS = R1+R2+R3    | A+B+C | Ω
```
answers: RS

### rpar2 · PARALLEL 2R · TWO R IN PARALLEL
picture:
```
R1 AND R2 SIDE BY SIDE
SAME VOLTAGE ACROSS EACH
PRODUCT OVER SUM
```
inputs: `A "R1 Ω="` · `B "R2 Ω="`
steps:
```
P  RP = R1*R2/(R1+R2)  | A*B/(A+B) | Ω
```
answers: RP

### rpar3 · PARALLEL 3R · THREE R IN PARALLEL
picture:
```
R1, R2, R3 SIDE BY SIDE
SAME VOLTAGE ACROSS EACH
```
inputs: `A "R1 Ω="` · `B "R2 Ω="` · `C "R3 Ω="`
steps:
```
P  RP = 1/(1/R1+1/R2+1/R3)  | 1/(1/A+1/B+1/C) | Ω
```
answers: RP

### vdiv · VOLT DIVIDER · VOLTAGE DIVIDER
picture:
```
VS + TO TOP OF R1
R1 MEETS R2 AT VOUT
R2 BOTTOM TO GROUND
VOUT IS ACROSS R2
```
inputs: `V "VS V="` · `R "R1 Ω="` · `S "R2 Ω="`
steps:
```
O  VOUT = VS*R2/(R1+R2)  | V*S/(R+S) | V
I  I = VS/(R1+R2)        | V/(R+S)   | A
```
answers: VOUT, I

### idiv · CURRENT DIV · CURRENT DIVIDER
picture:
```
IS SPLITS INTO R1 AND R2
R1 AND R2 IN PARALLEL
I1 IN R1, I2 IN R2
```
inputs: `I "IS A="` · `R "R1 Ω="` · `S "R2 Ω="`
steps:
```
A  I1 = IS*R2/(R1+R2)  | I*S/(R+S) | A
B  I2 = IS*R1/(R1+R2)  | I*R/(R+S) | A
```
answers: I1, I2

---

## COMPLEX+Z · `EECPLX`

Complex inputs are typed with [2nd][.] for 𝑖: `3+4𝑖`.

### r2p · RECT TO POLAR · RECTANGULAR TO POLAR
picture:
```
Z = A + jB
TYPE Z LIKE 3+4i
(i IS 2ND . )
```
inputs: `Z "Z=" complex`
steps:
```
A  A = REAL(Z)             | real(Z)            | 
B  B = IMAG(Z)             | imag(Z)            | 
M  |Z| = SQRT(A²+B²)       | √(A²+B²)           | 
D  ∠Z = ANGLE(Z)*180/PI    | angle(Z)*180/pi    | ° | fix2
```
answers: |Z|, ∠Z

### p2r · POLAR TO RECT · POLAR TO RECTANGULAR
picture:
```
Z = M ∠ ANGLE
ANGLE IN DEGREES
```
inputs: `M "|Z|="` · `D "ANGLE °="`
steps:
```
A  A = M*COS(ANGLE)   | M*cos(D*pi/180) | 
B  B = M*SIN(ANGLE)   | M*sin(D*pi/180) | 
Z  Z = A+jB           | A+B*𝑖           |  | cplx
```
answers: Z

### zc · Z OF CAPACITOR · CAPACITOR IMPEDANCE
picture:
```
ZC = 1/(jwC) = -j/(wC)
BIG AT LOW F, SMALL AT HI
```
inputs: `F "F Hz="` · `C "C F="`
steps:
```
W  w = 2*PI*F     | 2*pi*F    | rad/s
X  XC = 1/(w*C)   | 1/(W*C)   | Ω
Z  ZC = -j*XC     | ⁻𝑖*X      | Ω | cplx
```
answers: w, XC, ZC

### zl · Z OF INDUCTOR · INDUCTOR IMPEDANCE
picture:
```
ZL = jwL
SMALL AT LOW F, BIG AT HI
```
inputs: `F "F Hz="` · `L "L H="`
steps:
```
W  w = 2*PI*F     | 2*pi*F  | rad/s
X  XL = w*L       | W*L     | Ω
Z  ZL = j*XL      | 𝑖*X     | Ω | cplx
```
answers: w, XL, ZL

### zser · SERIES Z · IMPEDANCES IN SERIES
picture:
```
Z1, Z2, Z3 END TO END
TYPE 0 FOR A MISSING Z
TYPE Z LIKE 100-50i
```
inputs: `A "Z1=" complex` · `B "Z2=" complex` · `C "Z3=" complex`
steps:
```
Z  Z = Z1+Z2+Z3        | A+B+C            | Ω | cplx
M  |Z| = ABS(Z)        | abs(Z)           | Ω
D  ∠Z = ANGLE(Z)       | angle(Z)*180/pi  | ° | fix2
```
answers: Z, |Z|, ∠Z

### zpar · PARALLEL Z · IMPEDANCES IN PARALLEL
picture:
```
Z1 AND Z2 SIDE BY SIDE
PRODUCT OVER SUM
TYPE Z LIKE 100-50i
```
inputs: `A "Z1=" complex` · `B "Z2=" complex`
steps:
```
Z  Z = Z1*Z2/(Z1+Z2)   | A*B/(A+B)        | Ω | cplx
M  |Z| = ABS(Z)        | abs(Z)           | Ω
D  ∠Z = ANGLE(Z)       | angle(Z)*180/pi  | ° | fix2
```
answers: Z, |Z|, ∠Z

### zrlc · SERIES RLC Z · SERIES RLC IMPEDANCE
picture:
```
R, L, C END TO END
DRIVEN AT FREQUENCY F
```
inputs: `R "R Ω="` · `L "L H="` · `C "C F="` · `F "F Hz="`
steps:
```
W  w = 2*PI*F          | 2*pi*F           | rad/s
A  ZL = j*w*L          | 𝑖*W*L            | Ω | cplx
B  ZC = -j/(w*C)       | ⁻𝑖/(W*C)         | Ω | cplx
Z  Z = R+ZL+ZC         | R+A+B            | Ω | cplx
M  |Z| = ABS(Z)        | abs(Z)           | Ω
D  ∠Z = ANGLE(Z)       | angle(Z)*180/pi  | ° | fix2
```
answers: Z, |Z|, ∠Z

### pdiv · PHASOR DIVIDER · PHASOR VOLTAGE DIVIDER
picture:
```
VS + TO TOP OF Z1
Z1 MEETS Z2 AT VOUT
Z2 BOTTOM TO GROUND
TYPE Z LIKE 100-50i
```
inputs: `V "VS=" complex` · `A "Z1=" complex` · `B "Z2=" complex`
steps:
```
O  VOUT = VS*Z2/(Z1+Z2)  | V*B/(A+B)        | V | cplx
M  |VOUT| = ABS(VOUT)    | abs(O)           | V
D  ∠VOUT = ANGLE(VOUT)   | angle(O)*180/pi  | ° | fix2
```
answers: VOUT, |VOUT|, ∠VOUT

---

## S-DOMAIN · `EES` (Module 1)

### hdiv · H(s) Z DIVIDER · H(s) OF A Z DIVIDER
picture:
```
VIN > Z1 > VOUT > Z2 > GND
EACH Z IS R, L, C:
 TYPE 1 = IN SERIES
 TYPE 2 = IN PARALLEL
0 = PART NOT THERE
SAVES L1=TOP, L2=BOTTOM
```
inputs: `T "Z1 TYPE="` · `R "Z1 R Ω="` · `L "Z1 L H="` · `C "Z1 C F="` · `U "Z2 TYPE="` · `S "Z2 R Ω="` · `M "Z2 L H="` · `D "Z2 C F="`
Guards: `(T≠1 and T≠2) or (U≠1 and U≠2)` → "TYPE MUST BE 1 OR 2"; `R=0 and L=0 and C=0` → "Z1 HAS NO PARTS"; `S=0 and M=0 and D=0` → "Z2 HAS NO PARTS".
Compute (Raw), as coefficient lists (highest power first):
- a series arm is `Z = (L*s² + R*s + 1/C)/s`, numerator `{L,R,1/C}` over `{1,0}` (1/C is 0 when C is 0);
- a parallel arm is `Z = s/(C*s² + s/R + 1/L)`, numerator `{1,0}` over `{C,1/R,1/L}` (1/R, 1/L are 0 when the part is 0);
- strip leading zeros, then cancel common trailing zeros (factors of s) between numerator and denominator;
- `H = Z2/(Z1+Z2)`: top `n2*d1`, bottom `n1*d2 + n2*d1` (polynomial multiply and add);
- strip again, then divide top and bottom by the bottom's leading coefficient. Store the top in `L₁` and the bottom in `L₂`.
Polynomial text (used below): terms from the highest power down, zero coefficients skipped, each `<ZS(c)>*s^k` written `<ZS(c)>*s²`, `<ZS(c)>*s`, or `<ZS(c)>` for k = 2, 1, 0 (`<ZS(c)>*s^<k>` above 2), joined with `+`.
Answers (Raw), after the title:
```
N(s)=<text of L₁>
D(s)=<text of L₂>
DC GAIN=<ZF(N(0)/D(0))>          or  DC GAIN: POLE AT s=0   when D(0)=0
then by the order of D:
 1: POLE=<ZC(-L₂(2))>
 2: w0=<ZF(√(d0))> rad/s, Q=<ZF(√(d0)/d1)>, p1=<ZC>, p2=<ZC>   (four lines; p = (-d1±√(d1²-4d0))/2)
 3 or more: ORDER <n>: USE PLYSMLT2
```
Work (Raw):
```
Z1=(<text of n1>)/(<text of d1>)
Z2=(<text of n2>)/(<text of d2>)
H=Z2/(Z1+Z2)
=(<text of top>)/(<text of bottom>)            before dividing
DIVIDE TOP AND BOTTOM BY <ZF(lead)>
then the answer lines, then SAVED: L1=TOP, L2=BOTTOM
```

### hopamp · H(s) OP AMP · H(s) OF AN OP AMP STAGE
picture:
```
ZF FROM (-) TO VOUT
AMP 1 INV: VIN>ZIN>(-)
AMP 2 NON-INV: VIN>(+),
 ZIN FROM (-) TO GND
EACH Z: 1=SERIES 2=PAR
0 = PART NOT THERE
```
inputs: `A "AMP 1/2="` · `T "ZIN TYPE="` · `R "ZIN R Ω="` · `L "ZIN L H="` · `C "ZIN C F="` · `U "ZF TYPE="` · `S "ZF R Ω="` · `M "ZF L H="` · `D "ZF C F="`
Guards: `A≠1 and A≠2` → "AMP MUST BE 1 OR 2"; the type and no-parts guards of hdiv (ZIN, ZF).
Compute (Raw): arms as in hdiv. Inverting `H = -ZF/ZIN`: top `-nf*din`, bottom `df*nin`. Non-inverting `H = 1+ZF/ZIN`: top `nin*df + nf*din`, bottom `nin*df`. Then strip, normalize and store as in hdiv.
Answers and work: as hdiv, with `ZIN=`/`ZF=` for the arm lines and `H=-ZF/ZIN` or `H=1+ZF/ZIN`.

### taurc · TAU OF RC · RC TIME CONSTANT
picture:
```
R AND C IN ONE LOOP
TAU = R*C
AFTER 5 TAU: SETTLED
```
inputs: `R "R Ω="` · `C "C F="`
steps:
```
T  TAU = R*C        | R*C       | s
U  5TAU = 5*TAU     | 5*T       | s
W  wc = 1/TAU       | 1/T       | rad/s
F  fc = wc/(2*PI)   | W/(2*pi)  | Hz
```
answers: TAU, 5TAU, wc, fc

### taurl · TAU OF RL · RL TIME CONSTANT
picture:
```
R AND L IN ONE LOOP
TAU = L/R
AFTER 5 TAU: SETTLED
```
inputs: `L "L H="` · `R "R Ω="`
steps:
```
T  TAU = L/R        | L/R       | s
U  5TAU = 5*TAU     | 5*T       | s
W  wc = 1/TAU       | 1/T       | rad/s
F  fc = wc/(2*PI)   | W/(2*pi)  | Hz
```
answers: TAU, 5TAU, wc, fc

### step1 · 1ST ORDER STEP · FIRST-ORDER STEP RESPONSE
picture:
```
V(0): JUST AFTER SWITCH
 C KEEPS V, L KEEPS I
V(INF): LONG AFTER
 C OPEN, L SHORT
```
inputs: `A "V(0)="` · `B "V(INF)="` · `T "TAU s="` · `X "t s="`
steps:
```
V  v(t) = VINF+(V0-VINF)*e^(-t/TAU)  | B+(A-B)*𝑒^(⁻X/T) | 
```
answers: v(t)

### treach · TIME TO REACH · TIME TO REACH A VALUE
picture:
```
FIRST-ORDER CIRCUIT
GOING FROM V(0) TO V(INF)
WHEN DOES IT HIT TARGET?
```
inputs: `A "V(0)="` · `B "V(INF)="` · `T "TAU s="` · `V "TARGET="`
Guard `(A-B)/(V-B)≤1` → "TARGET NOT BETWEEN" / "V(0) AND V(INF)"
steps:
```
X  t = TAU*LN((V0-VINF)/(V-VINF))  | T*ln((A-B)/(V-B)) | s
```
answers: t

### srlc · SERIES RLC · SERIES RLC POLES
picture:
```
SOURCE,R,L,C IN ONE LOOP
OUTPUT ACROSS C
H=w0²/(s²+2as+w0²)
```
inputs: `R "R Ω="` · `L "L H="` · `C "C F="`
steps:
```
A  a = R/(2L)              | R/(2*L)       | 1/s
W  w0 = 1/SQRT(LC)         | 1/√(L*C)      | rad/s
Z  ZETA = a/w0             | A/W           | 
Q  Q = w0/(2a)             | W/(2*A)       | 
P  p1 = -a+SQRT(a²-w0²)    | ⁻A+√(A²-W²)   | 1/s | cplx
N  p2 = -a-SQRT(a²-w0²)    | ⁻A-√(A²-W²)   | 1/s | cplx
Verdict Str1 TYPE: A>W → "OVERDAMPED: 2 REAL POLES" / A=W → "CRITICAL: REPEATED POLE" / else "UNDERDAMPED: RINGS"
```
answers: a, w0, TYPE, p1, p2

### prlc · PARALLEL RLC · PARALLEL RLC POLES
picture:
```
R, L, C ALL IN PARALLEL
SAME VOLTAGE ACROSS ALL
```
inputs: `R "R Ω="` · `L "L H="` · `C "C F="`
steps: as srlc, with `A  a = 1/(2RC) | 1/(2*R*C) | 1/s`.
answers: a, w0, TYPE, p1, p2

### quad · AS²+BS+C · SECOND-ORDER POLES
picture:
```
DENOMINATOR AS²+BS+C
TYPE A, B, C
```
inputs: `A "A="` · `B "B="` · `C "C="`
steps:
```
W  w0 = SQRT(C/A)          | √(C/A)            | rad/s
Q  Q = SQRT(A*C)/B         | √(A*C)/B          | 
Z  ZETA = 1/(2Q)           | 1/(2*Q)           | 
D  DISC = B²-4AC           | B²-4*A*C          | 
P  p1 = (-B+SQRT(DISC))/2A | (⁻B+√(D))/(2*A)   | 1/s | cplx
N  p2 = (-B-SQRT(DISC))/2A | (⁻B-√(D))/(2*A)   | 1/s | cplx
Verdict Str1 POLES: Q<.5 → "Q<0.5: 2 REAL POLES" / Q=.5 → "Q=0.5: REPEATED POLE" / else "Q>0.5: COMPLEX PAIR"
Verdict Str2 PEAK: Q>1/√(2) → "Q>0.707: PEAKS" / else "NO PEAK"
```
answers: w0, Q, POLES, p1, p2, PEAK

### hjw · H(jw) AT F · EVALUATE H(s) AT s=jw
picture:
```
H(s)=N(s)/D(s)
TYPE COEFFICIENT LISTS,
HIGHEST POWER FIRST:
s²+800s+1ᴇ6 IS {1,800,1ᴇ6}
F=0 GIVES DC GAIN H(0)
```
inputs: `L₁ "N {..}=" list` · `L₂ "D {..}=" list` · `F "F Hz="`
steps:
```
W  w = 2*PI*F          | 2*pi*F           | rad/s
S  s = j*w             | 𝑖*W              | 1/s | cplx
Poly N N(s) = L₁(S) loop K
Poly D D(s) = L₂(S) loop K
H  H = N/D             | N/D              |  | cplx
M  |H| = ABS(H)        | abs(H)           | V/V
G  DB = 20*LOG|H|      | 20*log(M)        | dB | fix2
P  ∠H = ANGLE(H)       | angle(H)*180/pi  | ° | fix2
```
answers: |H|, DB, ∠H

### sine · SINE IN TO OUT · SINUSOIDAL STEADY STATE
picture:
```
IN: A*COS(wt+PHASE)
OUT: A|H|COS(wt+PHASE+∠H)
H AS COEFFICIENT LISTS,
HIGHEST POWER FIRST
```
inputs: `L₁ "N {..}=" list` · `L₂ "D {..}=" list` · `A "IN AMPLITUDE="` · `P "IN PHASE °="` · `F "F Hz="`
steps: as hjw up to `M |H|` and `G ∠H`, then
```
M  |H| = ABS(H)            | abs(H)           | V/V
G  ∠H = ANGLE(H)           | angle(H)*180/pi  | ° | fix2
Y  OUT AMP = A*|H|         | A*M              | 
Q  OUT PHASE = PHASE+∠H    | P+G              | ° | fix2
```
answers: OUT AMP, OUT PHASE

### bode · BODE LINES · STRAIGHT-LINE BODE PLOT
picture:
```
H=K0(1+s/z)../(1+s/p)..
 AND 1/s^N (N POLES AT 0)
CORNERS z, p IN rad/s
NO ZEROS OR POLES: {0}
```
inputs: `K "K0="` · `N "POLES AT 0="` · `L₁ "ZEROS {..}=" list` · `L₂ "POLES {..}=" list`
Guards: `K=0` → "K0 CANNOT BE 0"; `min(L₁)<0 or min(L₂)<0` → "CORNERS MUST BE > 0".
Compute (Raw): the low-frequency asymptote is `L + s0*log(w)` with `L = 20*log|K0|` and `s0 = -20N`. Take the corners (entries of 0 are ignored) in increasing order, merging equal ones; each zero adds +20 dB/dec and each pole -20 dB/dec at its corner. The level at the first corner is `L + s0*log(c1)`, then `A(c) = A(prev) + slope*log(c/prev)`.
Answers (Raw), after the title:
```
LOW F SLOPE=<ZR(s0)> dB/DEC
20*LOG|K0|=<ZR(L)> dB
w=<ZF(c)>: <ZR(A(c))> dB, THEN <ZR(slope after c)>        one per corner
```
Work (Raw):
```
LOW F: 20*LOG|K0|+SLOPE*LOG(w)
20*LOG|K0|=<ZR(L)> dB, SLOPE <ZR(s0)>
then per corner:
w=<ZF(c)>: SLOPE CHANGE <ZR(change)>
=<ZR(A(prev))>+(<ZR(slope before)>)*LOG(<ZF(c)>)            first corner
=<ZR(A(prev))>+(<ZR(slope before)>)*LOG(<ZF(c)>/<ZF(prev)>)  later corners
=<ZR(A(c))> dB, SLOPE NOW <ZR(slope after)>
```

### ends · START AND END · STEP START AND END VALUES
picture:
```
STEP OF SIZE V INTO H(s)
H AS LISTS, HIGHEST POWER
FIRST (L1 TOP, L2 BOTTOM)
ONLY FOR A STABLE H(s)
```
inputs: `L₁ "N {..}=" list` · `L₂ "D {..}=" list` · `V "STEP V="`
Guards: `dim(L₁)>dim(L₂)` → "IMPROPER H(s)"; `L₂(dim(L₂))=0` → "POLE AT s=0:" / "NO FINAL VALUE".
steps:
```
E  y(INF) = V*N(0)/D(0)                  | V*L₁(dim(L₁))/L₂(dim(L₂))         |  | si | sub=False
S  y(0+) = V*LEAD N/LEAD D IF SAME ORDER | V*(dim(L₁)=dim(L₂))*L₁(1)/L₂(1)  |  | si | sub=False
Note "FROM s*Y(s) AT s=0 AND s=INF"
```
answers: y(0+), y(INF)

### pfrac · PARTIAL FRAC · PARTIAL FRACTIONS
picture:
```
F(s)=N(s)/((s-p1)(s-p2)..)
DENOMINATOR STARTS AT 1s^n
ONE DOUBLE POLE ALLOWED
STEP INPUT: ADD POLE 0
POLES LIKE {0,-2,-1+3i}
```
inputs: `L₁ "N {..}=" list` · `L₂ "POLES {..}=" list`
Guards: `dim(L₁)>dim(L₂)` → "IMPROPER: DEG N ≥ DEG D" / "DIVIDE FIRST"; repeated poles beyond one double pole → see below.
Compute (Raw): for each pole i, `Ki = N(pi) / ∏(j≠i) (pi-pj)` into `L₃` (N evaluated by Horner's rule).
Answers (Raw): one line per pole, `K<i>=<ZC(Ki)>`.
Work (Raw), per pole i; `ZS`, `ZC`, `ZF` and `ZR` are the helpers:
```
K<i> AT s=<ZS(pi)>
=<ZS(N(pi))>/(<ZS(pi-pj)>*<ZS(pi-pk)>...)      one factor per other pole, in list order
=<ZC(Ki)>
then, for a real pole:
TERM: <ZS(Ki)>*e^(<ZS(pi)>t)
for a complex pole with imag > 0:
PAIR: 2|K|*e^(at)*COS(bt+∠K)
=<ZF(2|Ki|)>*e^(<ZS(real pi)>t)*COS(<ZF(imag pi)>t<+ if ∠Ki ≥ 0><ZR(∠Ki in degrees)>°)
for a complex pole with imag < 0:
(CONJUGATE OF PAIR ABOVE)
```
Example, `N={10}`, poles `{0,-2,-5}`: `K1 AT s=0`, `=10/(2*5)`, `=1`, `TERM: 1*e^(0t)`, `K2 AT s=(-2)`, `=10/((-2)*3)`, `=-1.667`, `TERM: (-1.667)*e^((-2)t)`, …
Example, `N={1}`, poles `{-1+2i,-1-2i}`: `K1 AT s=(-1+j2)`, `=1/((j4))`, `=-j250m`, `PAIR: 2|K|*e^(at)*COS(bt+∠K)`, `=500m*e^((-1)t)*COS(2t-90°)`, `K2 AT s=(-1-j2)`, `=1/((-j4))`, `=j250m`, `(CONJUGATE OF PAIR ABOVE)`.


One double pole is allowed (a pole entered twice, like `{-1,-1,-2}`). Write the double pole as `p` and the product of the other factors as `REST(s) = ∏(s-q)` over every other pole (1 if there are none). Then the coefficient of `1/(s-p)²` is `K2 = N(p)/REST(p)`, and the coefficient of `1/(s-p)` is `K1 = (dN/ds - K2*dREST/ds)/REST`, all at s = p. Every other pole uses the formula above, with both copies of `p` in its product. `L₃` holds `K1` at the first copy of `p` and `K2` at the second.
Answers: the first copy's line ends ` OVER (s-p)` and the second's ` OVER (s-p)²`, e.g. `K1=-1 OVER (s-p)`, `K2=2 OVER (s-p)²`.
Work for the double pole, printed at its first copy (the second copy prints nothing):
```
DOUBLE POLE AT s=<ZS(p)>
K<i2> OVER (s-p)²=N(p)/REST(p)
=<ZS(N(p))>/<ZS(REST(p))>
=<ZC(K2)>
K<i1> OVER (s-p)=(dN/ds-K<i2>*dREST/ds)/REST
=<ZC(K1)>
TERM: <ZS(K2)>*t*e^(<ZS(p)>t)+<ZS(K1)>*e^(<ZS(p)>t)
```
Guard change: a pole entered three or more times, or two different repeated poles → "REPEATED POLES:" / "ONLY ONE DOUBLE POLE".

---

## OP AMPS · `EEOPAMP` (Module 2)

Output limits follow the course rule `VEE+2 ≤ vo ≤ VCC-2` (use the datasheet numbers when a problem gives them: type them as VCC and VEE plus 2).

### inv · INVERTING · INVERTING AMPLIFIER
picture:
```
VIN > R1 > (-) INPUT
R2 FROM (-) TO VOUT
(+) INPUT TO GROUND
GAIN = -R2/R1
```
inputs: `V "VIN V="` · `R "R1 Ω="` · `F "R2 Ω="` · `P "VCC V="` · `N "VEE V="`
steps:
```
G  GAIN = -R2/R1          | ⁻F/R             | V/V
O  VOUT = GAIN*VIN        | G*V              | V
H  VOMAX = VCC-2          | P-2              | V
L  VOMIN = VEE+2          | N+2              | V
X  |VIN|MAX = VLIM/|GAIN| | min(H,abs(L))/abs(G) | V
Verdict Str1 RAILS: O>H or O<L → "CLIPS: PAST RAILS-2V" / else "OK: INSIDE RAILS"
```
answers: GAIN, VOUT, RAILS, |VIN|MAX

### noninv · NON-INVERTING · NON-INVERTING AMPLIFIER
picture:
```
VIN > (+) INPUT
R2 FROM (-) TO VOUT
R1 FROM (-) TO GROUND
GAIN = 1+R2/R1
```
inputs: `V "VIN V="` · `R "R1 Ω="` · `F "R2 Ω="` · `P "VCC V="` · `N "VEE V="`
steps: as inv with `G  GAIN = 1+R2/R1 | 1+F/R | V/V`, then `Note "VCM = VIN: CHECK INPUT RANGE"`.
answers: GAIN, VOUT, RAILS, |VIN|MAX

### limits · OUTPUT LIMITS · OUTPUT SWING LIMITS
picture:
```
VOUT = GAIN*VIN UNTIL IT
 HITS VO MAX OR VO MIN
DATASHEET VALUES, OR
 VCC-2 AND VEE+2
```
inputs: `G "GAIN V/V="` · `V "VIN V="` · `H "VO MAX V="` · `L "VO MIN V="`
steps:
```
O  IDEAL VOUT = GAIN*VIN          | G*V               | V
A  ACTUAL VOUT = CLIP TO LIMITS   | min(H,max(L,O))   | V
X  VIN AT VO MAX = VO MAX/GAIN    | H/G               | V
Y  VIN AT VO MIN = VO MIN/GAIN    | L/G               | V
Verdict Str1 CLIPS: O>H or O<L → "YES: OUTPUT CLIPS" / else "NO: INSIDE LIMITS"
```
answers: `IDEAL VOUT` · `ACTUAL VOUT` · `CLIPS` · `VIN AT VO MAX` · `VIN AT VO MIN`

### sum3 · SUMMER · INVERTING SUMMER
picture:
```
V1>R1, V2>R2, V3>R3
ALL MEET AT (-) INPUT
RF FROM (-) TO VOUT
UNUSED INPUT: V=0, R=1
```
inputs: `A "V1="` · `R "R1 Ω="` · `B "V2="` · `S "R2 Ω="` · `C "V3="` · `T "R3 Ω="` · `F "RF Ω="`
steps:
```
O  VOUT = -RF*(V1/R1+V2/R2+V3/R3) | ⁻F*(A/R+B/S+C/T) | V
```
answers: VOUT

### diff · DIFFERENCE AMP · DIFFERENCE AMPLIFIER
picture:
```
VA > RA > (-) INPUT
RB FROM (-) TO VOUT
VB > RC > (+) INPUT
RD FROM (+) TO GROUND
```
inputs: `A "VA="` · `B "VB="` · `R "RA Ω="` · `F "RB Ω="` · `S "RC Ω="` · `T "RD Ω="`
steps:
```
P  V+ = VB*RD/(RC+RD)            | B*T/(S+T)          | V
O  VOUT = V+*(1+RB/RA)-VA*RB/RA  | P*(1+F/R)-A*F/R    | V
Note "RA=RC, RB=RD: RB/RA*(VB-VA)"
```
answers: VOUT

### iout · OUTPUT CURRENT · OP AMP OUTPUT CURRENT
picture:
```
OUTPUT FEEDS THE LOAD RL
AND THE FEEDBACK RF
V- = 0 FOR INVERTING
V- = VIN FOR NON-INVERTING
```
inputs: `O "VOUT V="` · `L "RL Ω="` · `F "RF Ω="` · `N "V- V="`
steps:
```
A  IL = VOUT/RL          | O/L       | A
B  IF = (VOUT-V-)/RF     | (O-N)/F   | A
I  IO = IL+IF            | A+B       | A
```
answers: IL, IF, IO

### offset · OFFSET + BIAS · OFFSET AND BIAS ERROR
picture:
```
INVERTING OR NON-INV AMP
R1 IN, R2 FEEDBACK
R3 AT (+) CANCELS IB
SIGNS UNKNOWN: ADD SIZES
```
inputs: `V "VOS V="` · `B "IB A="` · `I "IOS A="` · `R "R1 Ω="` · `F "R2 Ω="`
steps:
```
G  NOISE GAIN = 1+R2/R1         | 1+F/R        | V/V
E  VO(VOS) = |VOS|*(1+R2/R1)    | abs(V)*G     | V
A  VO(IB), NO R3 = IB*R2        | B*F          | V
C  R3 = R1*R2/(R1+R2)           | R*F/(R+F)    | Ω
D  VO(IOS), WITH R3 = IOS*R2    | I*F          | V
W  WORST, WITH R3 = VO(VOS)+VO(IOS) | E+D      | V
X  WORST, NO R3 = VO(VOS)+VO(IB)    | E+A      | V
```
answers: `R3` · `WORST, WITH R3` · `WORST, NO R3`

### vosm · VOS FROM VO · OFFSET FROM MEASURED VO
picture:
```
INPUT GROUNDED (VS=0)
VO IS THE MEASURED OUTPUT
R1 IN, R2 FEEDBACK
VO = VOS*(1+R2/R1)
```
inputs: `O "VO V="` · `R "R1 Ω="` · `F "R2 Ω="`
steps:
```
G  NOISE GAIN = 1+R2/R1   | 1+F/R  | V/V
V  VOS = VO/NOISE GAIN    | O/G    | V
```
answers: `VOS`

### ibcap · BIAS INTO CAP · BIAS CURRENT INTO A CAP
picture:
```
(+) HAS ONLY C TO GROUND
BIAS CURRENT CHARGES C
IP<0: CURRENT OUT OF PIN
GAIN 1+R2/R1 (NON-INV)
```
inputs: `P "IP A="` · `N "IN A="` · `C "C F="` · `R "R1 Ω="` · `F "R2 Ω="` · `T "t s="` · `H "VO MAX V="` · `L "VO MIN V="`
Guard `P=0` → "IP=0: NO RAMP".
steps:
```
S  dVP/dt = -IP/C                  | ⁻P/C            | V/s
G  GAIN = 1+R2/R1                  | 1+F/R           | V/V
V  VP(t) = dVP/dt*t                | S*T             | V
O  VO(t) = GAIN*VP(t)              | G*V             | V
M  LIMIT = VO MAX IF RISING ELSE VO MIN | (S≥0)*H+(S<0)*L | V | si | sub=False
X  tSAT = LIMIT/(GAIN*dVP/dt)      | M/(G*S)         | s
B  IB = (IP+IN)/2                  | (P+N)/2         | A
D  IOS = IP-IN                     | P-N             | A
```
answers: `VO(t)` · `tSAT` · `IB` · `IOS`

### finite · FINITE GAIN · FINITE OPEN-LOOP GAIN
picture:
```
REAL OP AMP GAIN AOL
R1 IN, R2 FEEDBACK
```
inputs: `R "R1 Ω="` · `F "R2 Ω="` · `A "AOL V/V="`
steps:
```
G  NOISE GAIN = 1+R2/R1       | 1+F/R          | V/V
I  INV IDEAL = -R2/R1         | ⁻F/R           | V/V
J  INV REAL = IDEAL/(1+NG/AOL) | I/(1+G/A)     | V/V
N  NONINV IDEAL = 1+R2/R1     | G              | V/V
M  NONINV REAL = NG/(1+NG/AOL) | G/(1+G/A)     | V/V
E  ERROR = 100*(1-REAL/IDEAL) | 100*(1-J/I)    | %
```
answers: INV REAL, NONINV REAL, ERROR

### gbw · GBW BANDWIDTH · GAIN-BANDWIDTH
picture:
```
GBW = GAIN * BANDWIDTH
USE NOISE GAIN 1+R2/R1
EVEN FOR INVERTING
LM324: GBW ABOUT 1.2MHz
```
inputs: `G "GBW Hz="` · `R "R1 Ω="` · `F "R2 Ω="` · `X "F Hz="`
steps:
```
N  NOISE GAIN = 1+R2/R1   | 1+F/R  | V/V
C  FC = GBW/(1+R2/R1)     | G/N    | Hz
A  AMAX AT F = GBW/F      | G/X    | V/V
```
answers: FC, AMAX AT F

### slew · SLEW RATE · SLEW RATE LIMIT
picture:
```
VM = OUTPUT PEAK VOLTAGE
SR FROM DATASHEET V/μs
NEED 2PI*F*VM ≤ SR
```
inputs: `S "SR V/μs="` · `V "VM V="` · `F "F Hz="`
steps:
```
R  SR = SR*1ᴇ6              | S*1ᴇ6       | V/s
N  NEEDED = 2*PI*F*VM       | 2*pi*F*V    | V/s
M  FMAX = SR/(2*PI*VM)      | R/(2*pi*V)  | Hz
X  VMMAX = SR/(2*PI*F)      | R/(2*pi*F)  | V
Verdict Str1 SLEW: N≤R → "OK: NO SLEW LIMIT" / else "SLEW LIMITED: DISTORTS"
```
answers: SLEW, FMAX, VMMAX

---

## FILTERS · `EEFILT` (Module 3)

### rclp · RC LOW-PASS · RC LOW-PASS FILTER
picture:
```
VIN > R > VOUT
C FROM VOUT TO GROUND
H = 1/(1+jw/wc)
```
inputs: `R "R Ω="` · `C "C F="` · `F "F Hz="`
steps:
```
W  wc = 1/(R*C)          | 1/(R*C)          | rad/s
T  fc = wc/(2*PI)        | W/(2*pi)         | Hz
X  w = 2*PI*F            | 2*pi*F           | rad/s
G  H = 1/(1+j*w/wc)      | 1/(1+𝑖*X/W)      |  | cplx
M  |H| = ABS(H)          | abs(G)           | V/V
D  DB = 20*LOG|H|        | 20*log(M)        | dB | fix2
P  ∠H = ANGLE(H)         | angle(G)*180/pi  | ° | fix2
```
answers: fc, |H|, DB, ∠H

### rchp · RC HIGH-PASS · RC HIGH-PASS FILTER
picture:
```
VIN > C > VOUT
R FROM VOUT TO GROUND
H = (jw/wc)/(1+jw/wc)
```
inputs and steps: as rclp with `G  H = (j*w/wc)/(1+j*w/wc) | (𝑖*X/W)/(1+𝑖*X/W) |  | cplx`.
answers: fc, |H|, DB, ∠H

### rcload · LOADED RC LP · LOADED RC LOW-PASS
picture:
```
VIN > R > VOUT
C AND RL FROM VOUT TO GND
LOAD LOWERS GAIN,
RAISES CUTOFF
```
inputs: `R "R Ω="` · `C "C F="` · `L "RL Ω="`
steps:
```
K  K = RL/(R+RL)          | L/(R+L)   | V/V
W  wc NO LOAD = 1/(R*C)   | 1/(R*C)   | rad/s
V  wc LOADED = wc/K       | W/K       | rad/s
T  fc LOADED = wc/(2*PI)  | V/(2*pi)  | Hz
```
answers: K, wc LOADED, fc LOADED

### actlp · ACTIVE INV LP · ACTIVE INVERTING LOW-PASS
picture:
```
VIN > R1 > (-) INPUT
R2 AND C IN PARALLEL
 FROM (-) TO VOUT
(+) TO GROUND
```
inputs: `R "R1 Ω="` · `F "R2 Ω="` · `C "C F="` · `X "F Hz="`
steps:
```
G  G0 = -R2/R1           | ⁻F/R             | V/V
W  wc = 1/(R2*C)         | 1/(F*C)          | rad/s
T  fc = wc/(2*PI)        | W/(2*pi)         | Hz
Y  w = 2*PI*F            | 2*pi*X           | rad/s
H  H = G0/(1+j*w/wc)     | G/(1+𝑖*Y/W)      |  | cplx
M  |H| = ABS(H)          | abs(H)           | V/V
D  DB = 20*LOG|H|        | 20*log(M)        | dB | fix2
P  ∠H = ANGLE(H)         | angle(H)*180/pi  | ° | fix2
```
answers: G0, fc, |H|, DB, ∠H

### acthp · ACTIVE INV HP · ACTIVE INVERTING HIGH-PASS
picture:
```
VIN > C > R1 > (-) IN
R2 FROM (-) TO VOUT
(+) TO GROUND
```
inputs: `R "R1 Ω="` · `C "C F="` · `F "R2 Ω="` · `X "F Hz="`
steps: as actlp with `W  wc = 1/(R1*C) | 1/(R*C) | rad/s` and `H  H = G0*(j*w/wc)/(1+j*w/wc) | G*(𝑖*Y/W)/(1+𝑖*Y/W) |  | cplx`.
answers: G0, fc, |H|, DB, ∠H

### so2 · 2ND ORDER · SECOND ORDER w0 Q CUTOFFS
picture:
```
D(s) = AS²+BS+C
G0 = PASSBAND GAIN
GIVES LP/HP CUTOFF AND
BP EDGES + BANDWIDTH
```
inputs: `A "A="` · `B "B="` · `C "C="` · `G "G0="`
steps:
```
W  w0 = SQRT(C/A)            | √(C/A)                              | rad/s
F  f0 = w0/(2*PI)            | W/(2*pi)                            | Hz
Q  Q = SQRT(A*C)/B           | √(A*C)/B                            | 
P  |HLP(jw0)| = Q*G0         | Q*G                                 | V/V
X  wc LP = w0*SQRT(1-1/(2Q²)+SQRT(1+(1-1/(2Q²))²)) | W*√(1-1/(2*Q²)+√(1+(1-1/(2*Q²))²)) | rad/s
U  wc HP = w0²/wc LP         | W²/X                                | rad/s
L  wL BP = w0*SQRT(1+1/(4Q²))-w0/(2Q) | W*√(1+1/(4*Q²))-W/(2*Q)    | rad/s
H  wH BP = w0*SQRT(1+1/(4Q²))+w0/(2Q) | W*√(1+1/(4*Q²))+W/(2*Q)    | rad/s
D  BW = w0/Q                 | W/Q                                 | rad/s
```
answers: w0, Q, wc LP, wc HP, BW

### sklpa · SK LP ANALYZE · SALLEN-KEY LOW-PASS
picture:
```
VIN>R1>VX>R2>(+)
C1 FROM VX TO VOUT
C2 FROM (+) TO GROUND
FOLLOWER: VOUT = V+
```
inputs: `R "R1 Ω="` · `S "R2 Ω="` · `C "C1 F="` · `D "C2 F="`
steps:
```
M  m = R1/R2               | R/S               | 
N  n = C1/C2               | C/D               | 
W  w0 = 1/SQRT(R1R2C1C2)   | 1/√(R*S*C*D)      | rad/s
F  f0 = w0/(2*PI)          | W/(2*pi)          | Hz
Q  Q = SQRT(mn)/(m+1)      | √(M*N)/(M+1)      | 
```
answers: w0, f0, Q

### sklpd · SK LP DESIGN · DESIGN SALLEN-KEY LOW-PASS
picture:
```
R2=R, R1=mR, C2=C, C1=nC
PICK C AND n (n ≥ 4Q²)
F0 IS w0/(2PI); FOR
Q=0.707 FC = F0
```
inputs: `F "F0 Hz="` · `Q "Q="` · `C "C2 F="` · `N "n=C1/C2="`
Guard `N<4*Q²` → "n TOO SMALL:" / "NEED n ≥ 4Q²"
steps:
```
W  w0 = 2*PI*F0            | 2*pi*F              | rad/s
K  k = n/(2Q²)-1           | N/(2*Q²)-1          | 
M  m = k+SQRT(k²-1)        | K+√(K²-1)           | 
S  R2 = 1/(w0*C*SQRT(mn))  | 1/(W*C*√(M*N))      | Ω
R  R1 = m*R2               | M*S                 | Ω
D  C1 = n*C                | N*C                 | F
```
answers: R1, R2, C1, m

### skhpa · SK HP ANALYZE · SALLEN-KEY HIGH-PASS
picture:
```
VIN>C1>VX>C2>(+)
R1 FROM VX TO VOUT
R2 FROM (+) TO GROUND
FOLLOWER: VOUT = V+
```
inputs: `C "C1 F="` · `D "C2 F="` · `R "R1 Ω="` · `S "R2 Ω="`
steps:
```
M  m = R1/R2               | R/S               | 
N  n = C1/C2               | C/D               | 
W  w0 = 1/SQRT(R1R2C1C2)   | 1/√(R*S*C*D)      | rad/s
F  f0 = w0/(2*PI)          | W/(2*pi)          | Hz
Q  Q = SQRT(n/m)/(n+1)     | √(N/M)/(N+1)      | 
```
answers: w0, f0, Q

### skhpd · SK HP DESIGN · DESIGN SALLEN-KEY HP
picture:
```
EQUAL CAPACITORS C1=C2=C
m = R1/R2 = 1/(4Q²)
```
inputs: `F "F0 Hz="` · `Q "Q="` · `C "C F="`
steps:
```
W  w0 = 2*PI*F0            | 2*pi*F          | rad/s
M  m = 1/(4Q²)             | 1/(4*Q²)        | 
S  R2 = 1/(w0*C*SQRT(m))   | 1/(W*C*√(M))    | Ω
R  R1 = m*R2               | M*S             | Ω
```
answers: R1, R2, m

### ladda · RC LADDER · RC LADDER ANALYZE
picture:
```
VIN>R1>V1>R2>VOUT
C1 FROM V1 TO GROUND
C2 FROM VOUT TO GROUND
Q IS ALWAYS BELOW 0.5
```
inputs: `R "R1 Ω="` · `C "C1 F="` · `S "R2 Ω="` · `D "C2 F="`
steps:
```
A  s² COEF = R1C1R2C2          | R*C*S*D        | s²
B  s COEF = R1C1+C2(R1+R2)     | R*C+D*(R+S)    | s
W  w0 = 1/SQRT(s² COEF)        | 1/√(A)         | rad/s
F  f0 = w0/(2*PI)              | W/(2*pi)       | Hz
Q  Q = SQRT(s² COEF)/s COEF    | √(A)/B         | 
```
answers: w0, f0, Q

### laddd · LADDER DESIGN · DESIGN RC LADDER
picture:
```
SAME LADDER AS ANALYZE
PICK R1 AND a = C1/C2
MAX Q = SQRT(a/(a+1))/2
```
inputs: `W "w0 rad/s="` · `Q "Q="` · `R "R1 Ω="` · `A "a=C1/C2="`
Guard `A-4*Q²*(A+1)<0` → "Q TOO HIGH FOR" / "THIS C1/C2"
steps:
```
M  MAX Q = SQRT(a/(a+1))/2              | √(A/(A+1))/2                  | 
X  SQRT(R2/R1) = (SQRT(a)-SQRT(a-4Q²(a+1)))/(2Q) | (√(A)-√(A-4*Q²*(A+1)))/(2*Q) | 
S  R2 = X²*R1                           | X²*R                          | Ω
D  C2 = 1/(w0*SQRT(R1*R2*a))            | 1/(W*√(R*S*A))                | F
C  C1 = a*C2                            | A*D                           | F
```
answers: R2, C1, C2

### mfb · MFB BANDPASS · MULTI-FEEDBACK BANDPASS
picture:
```
VIN > R1 > NODE X
R3 FROM X TO GROUND
C1 FROM X TO (-) INPUT
C2 FROM X TO VOUT
R2 FROM (-) TO VOUT
```
inputs: `R "R1 Ω="` · `S "R2 Ω="` · `T "R3 Ω="` · `C "C1 F="` · `D "C2 F="`
steps:
```
W  w0 = SQRT((1+R1/R3)/(R1R2C1C2))  | √((1+R/T)/(R*S*C*D))  | rad/s
F  f0 = w0/(2*PI)                   | W/(2*pi)              | Hz
B  BW = (C1+C2)/(R2C1C2)            | (C+D)/(S*C*D)         | rad/s
Q  Q = w0/BW                        | W/B                   | 
G  G0 = -Q/(w0*R1*C2)               | ⁻Q/(W*R*D)            | V/V
```
answers: w0, f0, Q, BW, G0

### sv · STATE-VARIABLE · STATE-VARIABLE FILTER
picture:
```
SUMMER > INTEGRATOR >
 INTEGRATOR (R, C EACH)
OUTPUTS: HP, BP, LP
G3 = RF/R1
```
inputs: `A "R1 Ω="` · `F "RF Ω="` · `B "R2 Ω="` · `D "R3 Ω="` · `R "R Ω="` · `C "C F="`
steps:
```
G  G3 = RF/R1                     | F/A                  | 
W  w0 = SQRT(G3)/(R*C)            | √(G)/(R*C)           | rad/s
E  f0 = w0/(2*PI)                 | W/(2*pi)             | Hz
U  G1 = (1+RF/R1)/(1+R2/R3)       | (1+F/A)/(1+B/D)      | 
V  G2 = (1+RF/R1)/(1+R3/R2)       | (1+F/A)/(1+D/B)      | 
Q  Q = SQRT(G3)/G2                | √(G)/V               | 
H  HP GAIN = G1                   | U                    | V/V
P  BP GAIN = -G1/G2               | ⁻U/V                 | V/V
L  LP GAIN = G1/G3                | U/G                  | V/V
```
answers: w0, Q, HP GAIN, BP GAIN, LP GAIN

---

## UTILITIES · `EEUTIL`

### solve · SOLVE EQNS · SOLVE LINEAR EQUATIONS
picture:
```
UP TO 4 EQNS, 4 UNKNOWNS
TYPE ALL ROWS IN ONE LIST
 a11,a12,b1,a21,a22,b2..
2x1+3x2=5 AND x1-x2=0:
 {2,3,5,1,⁻1,0}
COMPLEX VALUES ALLOWED
```
inputs: `L₁ "ROWS {..}=" list`
steps and guards, in order:
```
N  N = (SQRT(4*COUNT+1)-1)/2   | (√(4*dim(L₁)+1)-1)/2 |  | si | sub=False
Guard N≠int(N) or N<2 or N>4 → "NEED N*(N+1) NUMBERS" / "FOR N EQUATIONS, N=2-4"
Raw: Gaussian elimination with partial pivoting (largest abs pivot) into L₂, setting a flag when a pivot is 0
Guard <flag> → "NO UNIQUE SOLUTION"
```
Answers (Raw): `x<i>=<ZC(x_i)>` for each unknown; the solution is also left in `L₂`.
Work (Raw):
```
EQ<i>: <ZS(a_i1)>*x1+<ZS(a_i2)>*x2+...=<ZS(b_i)>     every coefficient, zeros included
SOLVED BY ELIMINATION
```

### todb · RATIO TO DB · RATIO TO DECIBELS
picture:
```
VOLTAGE RATIO: 20 LOG
POWER RATIO: 10 LOG
x10=+20dB, x2=+6dB
```
inputs: `X "RATIO="`
steps:
```
D  DB (V) = 20*LOG|X|    | 20*log(abs(X))  | dB | fix2
P  DB (P) = 10*LOG|X|    | 10*log(abs(X))  | dB | fix2
```
answers: DB (V), DB (P)

### fromdb · DB TO RATIO · DECIBELS TO RATIO
picture:
```
V RATIO = 10^(DB/20)
P RATIO = 10^(DB/10)
-3dB = 0.707 V/V
```
inputs: `D "DB="`
steps:
```
X  V RATIO = 10^(DB/20)   | 10^(D/20)  | V/V
P  P RATIO = 10^(DB/10)   | 10^(D/10)  | W/W
```
answers: V RATIO, P RATIO

### hzrad · HZ TO RAD/S · HERTZ TO RAD/S
picture:
```
w = 2*PI*F
T = 1/F
```
inputs: `F "F Hz="`
steps:
```
W  w = 2*PI*F    | 2*pi*F  | rad/s
T  T = 1/F       | 1/F     | s
```
answers: w, T

### radhz · RAD/S TO HZ · RAD/S TO HERTZ
picture:
```
F = w/(2*PI)
T = 1/F
```
inputs: `W "w rad/s="`
steps:
```
F  F = w/(2*PI)  | W/(2*pi)  | Hz
T  T = 1/F       | 1/F       | s
```
answers: F, T

### scope · PHASE FROM DT · PHASE FROM A SCOPE
picture:
```
DT = TIME FROM INPUT PEAK
 TO OUTPUT PEAK
NEGATIVE IF OUTPUT LAGS
```
inputs: `F "F Hz="` · `T "DT s="`
steps:
```
P  PHASE = 360*F*DT   | 360*F*T  | ° | fix2
```
answers: PHASE

### e12 · NEAREST E12 · NEAREST E12 VALUE
picture:
```
E12: 1 1.2 1.5 1.8 2.2 2.7
 3.3 3.9 4.7 5.6 6.8 8.2
TIMES A POWER OF 10
```
inputs: `X "VALUE="`
Guard `X≤0` → "VALUE MUST BE > 0"
Compute (Raw): decade `D=10^(int(log(X)))`, mantissa `M=X/D`, the list `L₆={1,1.2,1.5,1.8,2.2,2.7,3.3,3.9,4.7,5.6,6.8,8.2,10}`. NEAREST is the entry with the smallest `abs(log(L₆/M))`, times D. BELOW is the largest E12 value ≤ X and ABOVE the smallest ≥ X (both equal X when X is an E12 value).
steps (shown):
```
D  DECADE = 10^INT(LOG(X))   | 10^(int(log(X)))  | 
M  MANTISSA = X/DECADE       | X/D               | 
E  NEAREST = E12*DECADE      | <mantissa>*D      | 
B  BELOW                     | <mantissa>*D      | 
A  ABOVE                     | <mantissa>*D      | 
```
The Raw block only picks the three list entries (into spare variables); NEAREST, BELOW and ABOVE are ordinary Calc steps on them, so the tests can read them by name.
answers: NEAREST, BELOW, ABOVE
