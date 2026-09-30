# TI-84 circuit programs: design

Date: 2026-09-29. Status: approved for implementation.

## Goal

A set of TI-84 Plus CE programs for an electronic circuits exam covering Modules 1 to 3: the s-domain, op amps and filters. The student picks a circuit or formula from a menu, types the numbers, and gets the answer first. Then [ENTER] pages through the work: for every step, the formula, the formula with the numbers put in, and the result. The professor has approved calculator programs for the exam; the point is to understand the method without getting stuck on arithmetic.

## Constraints

- The target is the TI-84 Plus CE with OS 5.2 or newer (`toString(` needs 5.2). It uses TI-BASIC only: no assembly, no jailbreak, no Python edition. That way the programs run on any CE and are allowed in exam mode.
- The exam is Friday 2026-10-02. Everything must be on the calculator and checked on the device by Thursday 2026-10-01.
- The student types every value. The programs hold formulas only, never answers to course problems.
- The student is a beginner. Screens use words, not just symbols, and every tool starts by saying which part is where in the circuit.

## What the student sees

```
EE main menu           Topic menu (EEFILT)       Tool
┌──────────────────┐   ┌──────────────────┐
│EE                │   │FILTERS           │
│1:BASICS          │   │1:RC LOW-PASS     │   1. picture screen  (ENTER)
│2:COMPLEX+Z       │ → │2:RC HIGH-PASS    │ → 2. inputs          (type, ENTER each)
│3:S-DOMAIN        │   │...               │   3. answer screen   (ENTER=work, CLEAR=quit)
│4:OP AMPS         │   │6:MORE            │   4. work pages      (ENTER=more, CLEAR=quit)
│5:FILTERS         │   │7:BACK            │   5. back to the topic menu
│6:UTILITIES       │   └──────────────────┘
│7:QUIT            │
└──────────────────┘
```

The screen is 10 rows by 26 columns. Rows 1 to 9 hold content and row 10 is the key footer.

1. **Picture screen.** Row 1 is the tool title. Rows 2 to 9 describe the circuit in words: where the source is, which part is in series, and what goes to ground. Row 10 reads `ENTER:GO`. [ENTER] continues (`Pause`).
2. **Inputs.** The screen clears. Each input is one `Input "R1 Ω=",R` prompt, with the unit in the prompt. Numbers use the calculator's own notation: 10 nF is `10ᴇ⁻9` (the [2nd][,] key), and a complex value is `3+4𝑖` ([2nd][.]). An expression such as `1/(2*π*1000)` is also accepted.
3. **Answer screen.** Row 1 is the title. Then comes one line per answer, `NAME=VALUE UNIT`, for example `VOUT=6.667 V`. The footer is `ENTER:WORK  CLEAR:QUIT`.
4. **Work pages.** Every step prints three lines:
   ```
   VOUT=VS*R2/(R1+R2)          ← the formula, in words
   =10*2k/(1k+2k)              ← the same formula with the numbers put in
   =6.667 V                    ← the result
   ```
   When the page is full, the footer reads `ENTER:MORE  CLEAR:QUIT`. After the last step, it reads `DONE  ENTER:MENU`.
5. [CLEAR] on any answer or work screen goes straight back to the topic menu.

**Number format.** Numbers show 4 significant figures with an SI prefix, and trailing zeros are dropped: `1.592k`, `10n`, `-90.83`, `2.2μ`, `1k`. The prefixes are p n μ m k M G. A number outside 1p to 999.9G falls back to the calculator's own format (`1ᴇ13`). Decibels and degrees show 2 decimals (`-3.01 dB`, `-45 °`). A complex value is shown as rectangular `A+jB` (`1k-j159.2`), plus a polar step (`|Z|`, `∠Z`) where it helps.

## Scope

The tools are listed below. [docs/tools.md](../../tools.md) has every input, step and formula, with the course source for each.

| Program | Menu | Tools |
|---|---|---|
| EEBASIC | BASICS | Ohm find V / I / R, series R, parallel 2R, parallel 3R, voltage divider, current divider |
| EECPLX | COMPLEX+Z | rect→polar, polar→rect, Z of capacitor, Z of inductor, series Z, parallel Z, series RLC Z at f, phasor divider |
| EES | S-DOMAIN | τ of RC, τ of RL, first-order step v(t), time to reach v, series RLC (α, ω0, poles, damping), parallel RLC, quadratic / second-order ω0 Q ζ, H(jω) from coefficient lists, sine in→out through H, partial fractions (distinct poles) |
| EEOPAMP | OP AMPS | inverting, non-inverting, summer (3 in), difference amp, output current, offset and bias worst case, finite open-loop gain, GBW bandwidth, slew rate |
| EEFILT | FILTERS | RC low-pass, RC high-pass, loaded RC low-pass, active inverting LP, active inverting HP, second-order ω0/Q/cutoffs/BW, Sallen-Key LP analyze, Sallen-Key LP design, Sallen-Key HP analyze, Sallen-Key HP design, RC ladder analyze, RC ladder design, MFB band-pass, state-variable |
| EEUTIL | UTILITIES | ratio→dB, dB→ratio, Hz↔rad/s and period, phase from scope Δt, nearest E12 value |

**Out of scope:** Module 4 (oscillators), drawing on the graph screen, symbolic algebra, repeated-pole partial fractions, and saving results between runs.

## Architecture

The math and screens are written once, as Python *recipes*. A generator turns them into TI-BASIC, and tivars turns that into `.8xp` files. The same bytes that go to the calculator are decoded and run by a Python interpreter of the TI-BASIC subset (the *sim*), so the tests exercise exactly what the calculator will run.

```
src/ti84/recipes/*.py ──► gen.py ──► program text ──► tokens.encode (tivars) ──► bytes ──► dist/*.8xp ──► TI Connect CE ──► calculator
src/ti84/helpers/*.basic ─────────────┘                                            │
                                                                                   └──► tokens.decode ──► sim ──► tests
```

Each unit has one job:

| Unit | Job | Depends on |
|---|---|---|
| `src/ti84/model.py` | Dataclasses `Topic`, `Tool`, `Input`, `Calc`, `Note`, `Verdict`, `Guard`, `Raw`, plus `validate(topic)` for the length, name and variable rules. | nothing |
| `src/ti84/recipes/` | One module per topic (`basics.py`, `cplx.py`, `sdomain.py`, `opamps.py`, `filters.py`, `util.py`), each exporting a `TOPIC`. `ALL_TOPICS` lists them in menu order. | model |
| `src/ti84/helpers/*.basic` | Hand-written TI-BASIC for the shared helper programs ZF, ZR, ZC, ZS, ZP and ZE (see below). | dialect |
| `src/ti84/gen.py` | `gen_topic(topic) -> str`, `gen_main(topics) -> str`. Emits canonical source text in the dialect. | model |
| `src/ti84/tokens.py` | `encode(text) -> bytes`, `decode(bytes) -> list[Token]`, `lint(text)`, and `write_8xp(name, text, path)`. The only module that imports tivars. | tivars |
| `src/ti84/build.py` | The `ti84-build` CLI. It generates every program, lints and encodes each, and writes `dist/<NAME>.8xp` plus `dist/src/<NAME>.txt`. It exits non-zero on any error. | gen, tokens, helpers |
| `src/ti84/sim/` | The TI-BASIC interpreter for the dialect: expression evaluator, statements, a 10×26 screen, scripted keys and inputs, and subprogram calls. | tokens (decode only) |
| `src/ti84/harness.py` | `run_tool(tool_id, inputs, keys=...) -> Run`. It builds every program in memory, starts the tool's topic program, navigates to the tool, feeds the inputs, pages through, and returns the screens and final variables. | build, sim |

The TI-BASIC subset is the contract between `gen` and `sim`. It is fixed in [docs/dialect.md](../../dialect.md). The generator may emit only what that file lists, and the sim implements exactly that and rejects everything else.

## Programs on the calculator

| Program | What it is |
|---|---|
| `EE` | The main menu, which calls the topic programs. |
| `EEBASIC` `EECPLX` `EES` `EEOPAMP` `EEFILT` `EEUTIL` | One per topic, holding every tool of that topic as a labelled section. Each can also be run on its own. |
| `ZF` `ZR` `ZC` `ZS` `ZP` `ZE` | The shared helpers. They are named Z so they sort last in the PRGM menu. |

**Modes.** Each topic program starts with `Radian`, `Float`, `Normal` and `a+b𝑖`, so square roots of negatives give complex values instead of `ERR:NONREAL`. The calculator stays in these modes afterwards. The README says so.

**Reserved names.** Helpers use `θ`, `Str0`, `Str8`, `Str9` and the named lists `⌊ZF`, `⌊ZC` and `⌊ZS`. Tools may use `A` to `Z`, `Str1` to `Str7` and `L₁` to `L₆`. `validate` rejects a tool that touches a reserved name.

## Helper programs

Every helper takes its input in `Ans` (or `Str0`), never changes `A` to `Z`, `Str1` to `Str7` or `L₁` to `L₆`, and leaves `Str0` alone unless it says otherwise.

| Helper | In | Out | Behavior |
|---|---|---|---|
| `ZF` | `Ans` real | `Str9` | Formats with 4 significant figures and an SI prefix (p n μ m · k M G), dropping trailing zeros; a negative value gets a leading `-`. `0`→`0`. `1591.549`→`1.592k`. `6.6666667`→`6.667`. `-90.8265`→`-90.83`. `1ᴇ⁻6`→`1μ`. `2.2ᴇ⁻9`→`2.2n`. `999.96`→`1k`. `999960`→`1M`. `0.001`→`1m`. `12.5`→`12.5`. `4.7ᴇ9`→`4.7G`. Outside [1ᴇ⁻12, 999.95ᴇ9] it returns `toString(Ans)`. |
| `ZR` | `Ans` real | `Str9` | Rounds to 2 decimals, dropping trailing zeros, with `-` for negatives; a result that rounds to 0 has no sign. `-51.4893`→`-51.49`. `3`→`3`. `-0.004`→`0`. |
| `ZC` | `Ans` real or complex | `Str9` | Gives `ZF(real)` then `+j`/`-j` and `ZF(|imag|)`. `1000-159.15𝑖`→`1k-j159.2`. `3+4𝑖`→`3+j4`. `5`→`5`. `-2𝑖`→`-j2`. `0`→`0`. |
| `ZS` | `Ans` real or complex | `Str9` | The value for a substituted line. A real value is `ZF`, wrapped in parentheses when negative (`(-5)`). A complex value (imag ≠ 0) is `(`+`ZC`+`)`. |
| `ZP` | `Str0`, `θ` | screen, `θ` | Prints one line. If `θ=0` (the student quit), it does nothing. The line takes `max(1,⌈length(Str0)/26⌉)` rows. If it would pass row 9, it shows the footer `ENTER:MORE  CLEAR:QUIT` on row 10 and waits: [CLEAR] sets `θ=0` and returns, and [ENTER] clears the screen and sets `θ=1`. Then it runs `Output(θ,1,Str0)` and advances `θ` by the rows used. |
| `ZE` | `Str0` (footer), `θ` | `θ` | Ends a section. If `θ=0`, it does nothing. It shows `Str0` on row 10 and waits for [ENTER] (clear the screen, `θ=1`) or [CLEAR] (`θ=0`). |

## Generated code shape

For a topic program, `gen_topic` emits the following. The exact tokens are in the dialect.

```
Radian / Float / Normal / a+b𝑖
Lbl M                             topic menu, 6 tools per page, then MORE or BACK
Menu("FILTERS","RC LOW-PASS",A,...,"MORE",M1)
Lbl Q / ClrHome / Return          BACK
Lbl A                             one section per tool:
  ClrHome / Output(...) picture / Output(10,1,"ENTER:GO") / Pause
  ClrHome / Input "R Ω=",R / ...
  compute: each Calc as expr→var, each Verdict as If/Then/Else into its Str, each Guard as `If cond` + `Goto <guard label>`
  answers: ClrHome, 1→θ, title and each answer line through ZP, then "ENTER:WORK  CLEAR:QUIT"→Str0, prgmZE, If not(θ) / Goto M
  work:    for each step, the formula, substituted and result lines through ZP (ZS fills the numbers in)
  "DONE  ENTER:MENU"→Str0 / prgmZE / Goto M
Lbl <guard label>                 ClrHome, message lines, Pause, Goto M
```

The generator never jumps out of a `Then`, `For(` or `Repeat` block with `Goto`, because that leaks memory on the calculator. Quitting works by `ZP` and `ZE` turning into no-ops once `θ=0`, and each section ends with a `Goto M` at the top level.

## Error handling

Mistakes are caught loudly at build time. `ti84-build` exits non-zero, naming the program and line, when any of the following happens:

- a text line is wider than 26 characters, a menu item is longer than 14 characters, or a program name is not 1 to 8 uppercase letters or digits;
- a tool uses a reserved variable, two steps store to the same variable, or an answer names a missing step;
- a display string doesn't survive an encode→decode round trip, or the code contains a token outside the dialect;
- the lint finds a lowercase-letter token outside a string, an ASCII `E` after a digit (should be `ᴇ`), `i` used as the imaginary unit (should be `𝑖`), or a subtraction `-` at the start of an expression (should be the negation `⁻`);
- the minimum OS reported by tivars is above TI-84+CE 5.2.

On the calculator, bad input produces the calculator's own error screen (`ERR:DIVIDE BY 0`, `ERR:DOMAIN`). That is loud, and it's the right behavior. Known invalid design inputs use a `Guard`, which shows a message that says what to change (`NEED C1/C2 ≥ 4Q²`). Nothing is clamped or guessed silently.

## Testing

We write each test before its code. pytest runs everything with `uv run pytest`.

| Layer | What is checked |
|---|---|
| sim | Expression semantics (precedence, negation, complex, lists, `toString(` format), statements, screen wrap and truncation, Menu, Input and getKey scripting, subprogram calls, errors, and the step limit. |
| tokens and build | Canonical spellings map to the right bytes, lint catches every bad pattern, `.8xp` files round-trip, and the build fails loudly on each rule above. |
| gen | Topic and tool skeletons, menu pages, label allocation, substituted-line building, and `validate`. |
| helpers | The examples in the helper table, run on the sim. |
| tools | For every tool, at least one course example or hand-worked vector: full-precision variables after the run, the answer-screen text, and the three-line work for every step. |
| device | [docs/acceptance.md](../../acceptance.md): a short checklist run on the real calculator on Thursday. It covers modes, glyphs (Ω μ ° ∠ ²), Menu paging, `toString(`, one tool per topic, and CLEAR from every screen. |

## Delivery

1. Run `uv run ti84-build`, which writes `dist/*.8xp`.
2. Install TI Connect CE (Mac), connect the calculator with USB, and drag every file from `dist/` onto the calculator.
3. On the calculator, press [prgm], choose EE, and press [ENTER].

A GitHub release attaches the `.8xp` files so the calculator can be loaded without building.
