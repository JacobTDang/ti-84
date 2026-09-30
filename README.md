# ti-84

TI-84 Plus CE programs for electronic circuits. Pick a circuit or formula, type the numbers, and the calculator shows the answer, then every step of the work: the formula, the formula with your numbers in it, and the result.

Topics: basics, complex numbers and impedance, the s-domain (Module 1), op amps (Module 2) and filters (Module 3). [docs/tools.md](docs/tools.md) lists every tool.

## What it looks like

RC low-pass, R = 1k, C = 1μ, F = 159.2 Hz. These screens come from the simulator the tests use:

```
┌──────────────────────────┐ ┌──────────────────────────┐ ┌──────────────────────────┐
│RC LOW-PASS FILTER        │ │RC LOW-PASS FILTER        │ │wc=1/(R*C)                │
│VIN > R > VOUT            │ │fc=159.2 Hz               │ │=1/(1k*1μ)                │
│C FROM VOUT TO GROUND     │ │|H|=707.1m V/V            │ │=1k rad/s                 │
│H = 1/(1+jw/wc)           │ │DB=-3.01 dB               │ │fc=wc/(2*PI)              │
│                          │ │∠H=-45 °                  │ │=1k/(2*PI)                │
│                          │ │                          │ │=159.2 Hz                 │
│                          │ │                          │ │w=2*PI*F                  │
│                          │ │                          │ │=2*PI*159.2               │
│                          │ │                          │ │=1k rad/s                 │
│ENTER:GO                  │ │ENTER:WORK  CLEAR:QUIT    │ │ENTER:MORE  CLEAR:QUIT    │
└──────────────────────────┘ └──────────────────────────┘ └──────────────────────────┘
  which part is where          the answer first             then every step
```

## Put it on the calculator

Needs a TI-84 Plus CE with OS 5.2 or newer ([2nd][+] → 1:About).

1. Install [TI Connect CE](https://education.ti.com/en/products/computer-software/ti-connect-ce-sw) and connect the calculator with its USB cable.
2. Download the `.8xp` files from the latest release (or build them, below).
3. Drag every `.8xp` file onto the calculator in TI Connect CE.
4. On the calculator: [prgm] → `EE` → [ENTER] [ENTER].

Numbers use the calculator's own notation: 10 nF is `10`[2nd][,]`⁻9`, and a complex value such as `3+4𝑖` uses [2nd][.] for 𝑖.

The programs switch the calculator to `a+b𝑖` mode so square roots of negatives work; [mode] → REAL switches back.

## Build and test

Needs [uv](https://docs.astral.sh/uv/).

```
uv run pytest          # all tests
uv run ti84-build      # writes dist/*.8xp and dist/src/*.txt
```

How it works: [docs/superpowers/specs/2026-09-29-ti84-circuits-design.md](docs/superpowers/specs/2026-09-29-ti84-circuits-design.md). The TI-BASIC subset the generator and the test interpreter share: [docs/dialect.md](docs/dialect.md).
