# The TI-BASIC dialect

This is the contract between the generator (`gen.py`), the hand-written helpers (`helpers/*.basic`) and the interpreter (`sim/`). Generated and helper code uses only what is listed here. The sim implements exactly this and raises `SimError` on anything else. Where this file and the real calculator disagree, the calculator wins: fix this file, the sim and the tests together.

## Source text

- A program is lines separated by `\n`. `:` also separates statements on one line; the sim accepts it, and the generator emits one statement per line.
- Source text is what `tokens.encode` accepts: tivars `encode(text)` in its default smart mode, for the TI-84+CE. The table below gives the canonical spelling of every token. Spell each token exactly this way. `π` is the one symbol whose spelling (`pi`) differs from how it displays.
- `sim` runs **decoded bytes**, never source text. The pipeline is `encode(text)`, then `.8xp` bytes, then `decode`, then the sim, so a token tivars would read differently (ASCII `E`, lowercase `i`) shows up as a different token and fails.

## Tokens

| Spelling | Bytes | Kind | Meaning |
|---|---|---|---|
| `ClrHome` | E1 | stmt | Blank the 10×26 home screen and move the Input cursor to row 1. |
| `Output(` | E0 | stmt | `Output(row,col,value)`. See Screen. |
| `Input ` | DC | stmt | `Input "prompt",var`. `var` is a real var, `L₁`–`L₆` or `θ`. |
| `Pause ` | D8 | stmt | With no argument, wait for [ENTER]. Always spell it with the trailing space: a bare `Pause` tokenizes as five lowercase letters. The same holds for `Input `, `If `, `Lbl `, `Goto ` and `Repeat `. |
| `Menu(` | E6 | stmt | `Menu("title","item",label,...)`, 1–7 items. It jumps to the chosen item's label. |
| `Lbl ` | D6 | stmt | Label of 1–2 characters from `A`–`Z`, `0`–`9`, `θ`. |
| `Goto ` | D7 | stmt | Jump to a label in the same program (the first `Lbl` from the top). |
| `If ` | CE | stmt | `If cond` guards the next statement. `If cond` + `Then` … [`Else` …] `End` is a block. |
| `Then` `Else` `End` | CF D0 D4 | stmt | Block parts. `End` also closes `For(` and `Repeat `. |
| `For(` | D3 | stmt | `For(var,start,end[,step])` … `End`. The variable is checked before each pass, and step defaults to 1. |
| `Repeat ` | D2 | stmt | `Repeat cond` … `End`. The body runs once, then again until cond is true. |
| `Return` | D5 | stmt | Leave the current program. From a subprogram, go back to the caller; from the top program, stop. |
| `Stop` | D9 | stmt | End everything. |
| `prgm` | 5F | stmt | `prgmNAME` runs another program (a subprogram call). All variables are global. |
| `→` | 04 | stmt | `expr→target`. Targets: real var, `θ`, `Str0`–`Str9`, `L₁`–`L₆`, `⌊NAME`, `L₁(n)`, `⌊NAME(n)`. |
| `Radian` `Float` `Normal` | 64 69 66 | stmt | Mode settings. The sim records them. |
| `a+b𝑖` | BB4F | stmt | Complex mode. Without it, a complex result raises `ERR:NONREAL`. |
| `getKey` | AD | value | Code of the key pressed since the last call, or 0. |
| `Ans` | 72 | value | The last expression-statement value. |
| `A`–`Z` | 41–5A | var | Real variables. They may hold complex values in `a+b𝑖` mode. |
| `θ` | 5B | var | Real variable. Reserved for the pager. |
| `Str1`…`Str9`, `Str0` | AA00…AA08, AA09 | var | String variables. |
| `L₁`–`L₆` | 5D00–5D05 | var | List variables. |
| `⌊` | EB | var | Named-list prefix: `⌊ZF`, a letter then up to 4 letters or digits. Decodes as `ʟ`. |
| `"` | 2A | str | Starts or ends a string. The string also ends at `→` or at the end of the line. |
| `{` `}` `,` `(` `)` | 08 09 2B 10 11 | punct | Lists, calls and grouping. |
| `+` `-` `*` `/` `^` | 70 71 82 83 F0 | op | Binary operators. `+` also joins strings. |
| `²` `⁻¹` | 0D 0C | op | Postfix square and reciprocal. |
| `⁻` | B0 | op | Prefix negation. |
| `=` `≠` `<` `>` `≤` `≥` | 6A 6F 6B 6C 6D 6E | cmp | 1 or 0. `=` and `≠` also compare strings. They work element by element on lists. |
| ` and ` ` or ` `not(` | 40 3C B8 | logic | Truth is nonzero. The result is 1 or 0. |
| `0`–`9` `.` `ᴇ` | 30–39 3A 3B | num | Number literal: `1.5ᴇ3`, `2ᴇ⁻9`. |
| `𝑖` `pi` `𝑒` | 2C AC BB31 | const | The imaginary unit, π, and Euler's number. |
| `abs(` `√(` `ln(` `log(` `𝑒^(` | B2 BC BE C0 BF | fn | Complex-aware: `abs(3+4𝑖)`=5, `√(⁻4)`=2𝑖, `ln(⁻1)`=π𝑖. |
| `int(` | B1 | fn | Floor: `int(⁻1.5)`=⁻2. |
| `round(` | 12 | fn | `round(x,n)`: n decimals, halves away from zero. |
| `min(` `max(` `sum(` `dim(` | 1A 19 B6 B5 | fn | `min(a,b)` or `min(list)`, the same for `max(`. `sum(list)`. `dim(list)`. |
| `seq(` | 23 | fn | `seq(expr,var,start,end[,step])` gives a list. The variable is restored afterwards. |
| `real(` `imag(` `angle(` `conj(` | BB26 BB27 BB28 BB25 | fn | Complex parts. `angle(` is in radians (the programs run in `Radian`). |
| `sin(` `cos(` `tan⁻¹(` | C2 C4 C7 | fn | Radians. |
| `length(` `sub(` `toString(` | BB2B BB0C EF97 | fn | `length(str)`, `sub(str,start,len)` (1-based), `toString(real)` (see Numbers). |

Any other token raises `SimError("unsupported token <name> at <program>:<line>")`.

## Expressions

The precedence, from tightest to loosest, is:

1. literals, variables, calls and parentheses; list element `L₁(n)`
2. postfix `²` `⁻¹`
3. `^` (left to right, as on the calculator: `2^3^2` = 64)
4. prefix `⁻` (so `⁻2²` = ⁻4 and `⁻2^2` = ⁻4)
5. `*` `/` (left to right)
6. `+` `-` (left to right)
7. `=` `≠` `<` `>` `≤` `≥`
8. `and`
9. `or`

The sim adds these rules:

- **Explicit multiplication only.** Two operands next to each other (`2A`, `A(B)`, `)(`, `A𝑖`) raise `SimError`. The generator always writes `*`. The one exception is a number literal followed directly by `𝑖` (`4𝑖`, `2.5𝑖`), which is a complex literal, because that's how a complex value is typed.
- **A `-` at the start of an expression** (after the start of a line, `(`, `,`, `→` or an operator) raises `SimError`. On the calculator that means `Ans-…`; the generator writes `⁻`.
- **Every `(` and `"` must be closed.** The calculator lets them be left open at the end of a line; the sim does not. The generator always closes them.
- **Lists.** Arithmetic and comparisons work element by element: a list with a number, or two lists of equal length (unequal lengths raise `SimError("ERR:DIM MISMATCH")`).
- **Numbers.** Values are Python `float`, or `complex` with a nonzero imaginary part. A complex result whose imaginary part is exactly 0 becomes a `float`. Outside `a+b𝑖` mode, a complex result raises `SimError("ERR:NONREAL")`.
- **Calculator errors.** Division by zero raises `SimError("ERR:DIVIDE BY 0")`. `ln(0)`, `log(0)`, `0^0` and `0^` a negative raise `SimError("ERR:DOMAIN")`. Wrong argument types raise `SimError("ERR:DATA TYPE")`.

## Numbers as text: `toString(`

`toString(x)` works on a real `x` in Normal Float mode. A complex argument raises `SimError`; the helpers split it into parts first.

- `0` gives `"0"`.
- Round to 10 significant digits.
- If 1ᴇ⁻3 ≤ |x| < 1ᴇ10, use plain decimal notation with trailing zeros and any trailing `.` dropped: `1.592`, `1500`, `0.25`.
- Otherwise use scientific notation: a mantissa with 1 to 10 significant digits (trailing zeros dropped), then `ᴇ`, then the exponent: `1ᴇ13`, `2.5ᴇ⁻13`.
- A negative value starts with `⁻` (the negation glyph), not `-`: `⁻5`.

The calculator is the judge of this format; the device checklist compares it. The helpers always pass `toString(` a positive value in [1, 1000) or a rounded one, so the tool screens never depend on the rarer cases.

## Screen

The home screen is 10 rows × 26 columns, and each displayed character takes one cell.

- `Output(r,c,v)`: `1≤r≤10` and `1≤c≤26`, otherwise `SimError("ERR:DOMAIN")`. A number `v` is shown as `toString(v)`. Text starts at (r,c), wraps from column 26 to column 1 of the next row, and is cut off after row 10 column 26. It never scrolls. It does not move the Input cursor.
- `ClrHome` blanks every cell.
- `Input "p",v` writes the prompt and typed text at the Input cursor row, then moves the cursor down, scrolling the whole screen up one row when it passes row 10. The sim also records every prompt in order, as `run.prompts`.
- `Menu(` shows the menu. The sim records it as `run.menus` (title and items). The screen is not changed afterwards (the calculator redraws the home screen).
- `Pause` records a snapshot of the screen in `run.screens`. So do `getKey` waits and the end of the run.

## Script events

The sim runs against a scripted list of events and never blocks:

- `Value(x)`: consumed by `Input`. `x` is a number, a complex number, a Python list, or TI text such as `"10ᴇ⁻9"` or `"3+4𝑖"`, which the sim evaluates with the dialect.
- `Key(name)`: consumed by `Pause` (only `ENTER`) and by `getKey`. Names and codes: `ENTER`=105, `CLEAR`=45.
- `Choose(text)`: consumed by `Menu(`. It picks the item whose text is equal, or raises `SimError` listing the items.

A statement that needs an event of one type while the next event is another type raises `SimError`. Running out of events while waiting also raises `SimError`. `getKey` with an empty queue returns 0, and the step limit (default 200 000 statements) raises `SimError("step limit")`, so a missing key can't hang a test.

## Memory

`Calculator` holds programs by name (bytes), variables, strings, lists, `Ans`, and modes, all global to every program. `prgmNAME` for a name it doesn't hold raises `SimError("ERR:UNDEFINED prgmNAME")`. `Goto` to a missing label raises `SimError("ERR:LABEL")`. A `Goto` that leaves an open `Then`, `For(` or `Repeat ` block is allowed (the calculator allows it), but the sim counts it in `run.leaks`. The tests require `run.leaks == 0` for generated code.

## Lint (build time, `tokens.lint`)

Outside strings, the lint rejects:

- lowercase-letter tokens (`BBB0`–`BBCA`): the letters `i` and `e` used where `𝑖`, `𝑒` or `ᴇ` were meant;
- a letter `E` right after a digit or `.`: the author typed `1.5E3`;
- `-` (71) at the start of an expression, as defined above;
- `→` followed by anything but a store target (a letter, `θ`, `Str0`–`Str9`, `L₁`–`L₆` or a named list), which catches forms like `→dim(` that are valid TI-BASIC but outside the dialect;
- any token not in the table above.

Inside strings, the lint rejects `"` and any character whose encode→decode round trip changes the text. The display glyphs known to work in strings are `² ° Ω μ Δ ∠ α β θ σ τ ≤ ≥ ⁻ ᴇ 𝑖 |` and ASCII letters, digits, spaces and `+-*/^=<>()[]{},.:;!?%&#@_$|`. The apostrophe, `~` and `\` do not round-trip, and `→` always ends a string. `π`, `ω` and `√` don't encode inside strings, so the display text writes `PI`, `w` and `SQRT(`.
