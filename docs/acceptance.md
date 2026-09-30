# On-calculator checklist

Run this on the real TI-84 Plus CE after loading `dist/*.8xp`. Each line has what to do and what you should see. If anything differs, note the line number and what the screen showed; the sim and tests get fixed to match the calculator.

## Setup

1. [2nd][+] (MEM) → 1:About: the OS version is **5.2 or newer**.
2. [prgm]: you see EE, EEBASIC, EECPLX, EES, EEOPAMP, EEFILT, EEUTIL, ZC, ZE, ZF, ZP, ZR, ZS.

## Menus

3. Run EE: menu titled `EE` with 7 items ending in `QUIT`.
4. 5:FILTERS: first page shows 6 tools and `MORE`; `MORE` shows the rest and `BACK`; `BACK` returns to the EE menu.
5. From the EE menu, `QUIT` returns to the home screen.

## One tool per topic

| # | Menu path | Type | Answer screen shows |
|---|---|---|---|
| 6 | BASICS → VOLT DIVIDER | VS=10, R1=1000, R2=2000 | `VOUT=6.667 V`, `I=3.333m A` |
| 7 | COMPLEX+Z → Z OF CAPACITOR | F=1000, C=1ᴇ⁻6 | `w=6.283k rad/s`, `XC=159.2 Ω`, `ZC=-j159.2 Ω` |
| 8 | S-DOMAIN → SERIES RLC | R=100, L=0.01, C=1ᴇ⁻6 | `a=5k 1/s`, `w0=10k rad/s`, `TYPE: UNDERDAMPED: RINGS`, `p1=-5k+j8.66k 1/s` |
| 9 | OP AMPS → FINITE GAIN | R1=1000, R2=100000, AOL=1000 | `INV REAL=-90.83 V/V` |
| 10 | FILTERS → RC LOW-PASS | R=1000, C=1ᴇ⁻6, F=159.1549 | `fc=159.2 Hz`, `|H|=707.1m V/V`, `DB=-3.01 dB`, `∠H=-45 °` |
| 11 | UTILITIES → DB TO RATIO | DB=-3 | `V RATIO=707.9m V/V` |
| 11a | S-DOMAIN → H(s) OP AMP | AMP=1; ZIN: TYPE=1, R=1000, L=0.05, C=0; ZF: TYPE=2, R=10000, L=0, C=1ᴇ⁻8 | `N(s)=(-2G)`, `D(s)=1*s²+30k*s+200M`, `DC GAIN=-10` |
| 11b | S-DOMAIN → PARTIAL FRAC | N={1,3}, POLES={⁻1,⁻1,⁻2} | `K1=-1 OVER (s-p)`, `K2=2 OVER (s-p)²`, `K3=1` |
| 11c | UTILITIES → SOLVE EQNS | ROWS={1,.5,1,⁻5,2,1,0,0,0,2,1,0} | `x1=-1.25`, `x2=2.5`, `x3=-5` |

For each of 6–11c also check:

12. The picture screen shows before the inputs; [ENTER] moves on.
13. [ENTER] on the answer screen shows the work: formula line, line with numbers, result line.
14. `ENTER:MORE  CLEAR:QUIT` appears when a page fills; the next page continues where it left off.
15. The last page says `DONE  ENTER:MENU`; [ENTER] returns to the topic menu.
16. [CLEAR] on the answer screen and on a work page both return to the topic menu.

## Glyphs and formats

17. `Ω`, `μ` (e.g. C=2.2ᴇ⁻6 shows `2.2μ`), `°`, `∠`, `²` look right, not as other symbols.
18. A negative result shows `-` in front (e.g. `-90.83`), not a raised `⁻`.
19. Negative numbers in the numbers line are in parentheses: `(-5)`.

## Errors

20. BASICS → PARALLEL 2R with R1=0, R2=0: the calculator shows `ERR:DIVIDE BY 0` (choose 1:Quit).
21. FILTERS → SK LP DESIGN with Q=0.707, n=1: the message `n TOO SMALL:` / `NEED n ≥ 4Q²`, then [ENTER] returns to the menu.

## Afterwards

22. Home screen: `√(⁻4)` gives `2𝑖` (the programs left the calculator in a+b𝑖 mode). To go back: [mode] → REAL.
