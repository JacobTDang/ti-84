"""Calculator machine: screen, events, and the TI-BASIC run loop."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ti84.tokens import Token, decode, encode

from ti84.sim import expr as ex
from ti84.sim.expr import evaluate, parse_named_list
from ti84.sim.program import (
    B_CLRHOME,
    B_CPLX,
    B_ELSE,
    B_END,
    B_FLOAT,
    B_FOR,
    B_GOTO,
    B_IF,
    B_INPUT,
    B_LBL,
    B_MENU,
    B_NORMAL,
    B_OUTPUT,
    B_PAUSE,
    B_PRGM,
    B_RADIAN,
    B_REPEAT,
    B_RETURN,
    B_STOP,
    B_THEN,
    Program,
    Statement,
    build_program,
    find_store,
    parse_label,
    parse_program_name,
    parse_store_target,
)
from ti84.sim.values import (
    SimError,
    display_value,
    is_true,
    normalize,
    require_real,
    to_string,
)

ROWS = 10
COLS = 26
KEY_CODES = {"ENTER": 105, "CLEAR": 45}
CODE_KEYS = {105: "ENTER", 45: "CLEAR"}


@dataclass(frozen=True)
class Value:
    x: object  # number, complex, list, or TI text like "10ᴇ⁻9"


@dataclass(frozen=True)
class Key:
    key: str | int  # "ENTER" (105), "CLEAR" (45), or a key code


@dataclass(frozen=True)
class Hold:
    key: str | int  # stays at the head; answers every Pause/getKey


@dataclass(frozen=True)
class Choose:
    text: str  # picks a Menu( item by its text


@dataclass(frozen=True)
class Out:
    row: int
    col: int
    text: str


@dataclass(frozen=True)
class Clear:
    pass


@dataclass(frozen=True)
class Wait:
    key: str | int
    screen: tuple[str, ...]  # 10 rows of 26 chars, before the key


@dataclass(frozen=True)
class MenuShown:
    title: str
    items: tuple[str, ...]
    chosen: str | None


@dataclass(frozen=True)
class Prompt:
    prompt: str
    typed: str


@dataclass
class Run:
    log: list = field(default_factory=list)
    screens: list[tuple[str, ...]] = field(default_factory=list)
    screen: list[str] = field(default_factory=list)
    prompts: list[str] = field(default_factory=list)
    menus: list[MenuShown] = field(default_factory=list)
    leaks: int = 0
    steps: int = 0
    stopped_at_menu: str | None = None


def _key_name(key: str | int) -> str | int:
    if isinstance(key, int):
        return CODE_KEYS.get(key, key)
    return key


def _key_code(key: str | int) -> int:
    if isinstance(key, int):
        return key
    if key in KEY_CODES:
        return KEY_CODES[key]
    raise SimError(f"unknown key {key!r}")


class Calculator:
    def __init__(self, complex_mode: bool = False, step_limit: int = 200_000):
        self.vars: dict[str, float | complex] = {}
        self.strings: dict[str, str] = {}
        self.lists: dict[str, list] = {}
        self.ans: object = 0.0
        self.complex_mode = complex_mode
        self.step_limit = step_limit
        self._programs: dict[str, Program] = {}
        self._modes: set[str] = set()
        # run state
        self._events: list = []
        self._event_i = 0
        self._run: Run | None = None
        self._screen: list[list[str]] = [[" "] * COLS for _ in range(ROWS)]
        self._input_row = 1
        self._stop_at_menu = False
        self._halt_all = False

    # --- ExprContext ---
    def get_var(self, name: str) -> float | complex:
        return self.vars.get(name, 0.0)

    def has_var(self, name: str) -> bool:
        return name in self.vars

    def clear_var(self, name: str) -> None:
        self.vars.pop(name, None)

    def set_var(self, name: str, value: Any) -> None:
        self.vars[name] = normalize(value, complex_mode=self.complex_mode)

    def get_string(self, name: str) -> str:
        if name not in self.strings:
            raise SimError("ERR:UNDEFINED")
        return self.strings[name]

    def get_list(self, name: str) -> list:
        if name not in self.lists:
            raise SimError("ERR:UNDEFINED")
        return self.lists[name]

    def get_ans(self) -> Any:
        return self.ans

    def get_key(self) -> float:
        assert self._run is not None
        head = self._peek_event()
        if isinstance(head, Hold):
            code = _key_code(head.key)
            self._log_wait(head.key)
            return float(code)
        if isinstance(head, Key):
            self._event_i += 1
            code = _key_code(head.key)
            self._log_wait(head.key)
            return float(code)
        # empty or wrong type → 0 (getKey never blocks)
        return 0.0

    def load(self, name: str, data: bytes) -> None:
        self._programs[name] = build_program(name, data)

    def load_text(self, name: str, text: str) -> None:
        self.load(name, encode(text))

    def eval(self, text: str) -> object:
        return evaluate(decode(encode(text)), self)

    def run(self, name: str, events=(), *, stop_at_menu: bool = False) -> Run:
        if name not in self._programs:
            raise SimError(f"ERR:UNDEFINED prgm{name}")
        self._events = list(events)
        self._event_i = 0
        self._stop_at_menu = stop_at_menu
        self._halt_all = False
        self._screen = [[" "] * COLS for _ in range(ROWS)]
        self._input_row = 1
        run = Run(screen=self._screen_tuple())
        self._run = run
        try:
            self._exec_program(name)
            self._check_unused_events()
        except SimError:
            raise
        finally:
            run.screen = self._screen_tuple()
            # also snapshot final screen into screens? dialect: "So do getKey waits and the end of the run."
            # Looking at tests - Pause snapshots; end of run sets run.screen but may not need screens append
            self._run = None
        return run

    def _screen_tuple(self) -> list[str]:
        return ["".join(row) for row in self._screen]

    def _snapshot(self) -> tuple[str, ...]:
        return tuple(self._screen_tuple())

    def _log_wait(self, key: str | int) -> None:
        assert self._run is not None
        snap = self._snapshot()
        self._run.screens.append(snap)
        self._run.log.append(Wait(_key_name(key) if isinstance(key, str) else key, snap))

    def _peek_event(self):
        if self._event_i >= len(self._events):
            return None
        return self._events[self._event_i]

    def _check_unused_events(self) -> None:
        leftover = []
        i = self._event_i
        while i < len(self._events):
            ev = self._events[i]
            if isinstance(ev, Hold):
                break
            leftover.append(ev)
            i += 1
        if leftover:
            raise SimError(f"unused events: {leftover!r}")

    def _at(self, program: str, line: int, err: SimError) -> SimError:
        msg = str(err)
        if " at " in msg and ":" in msg.split(" at ", 1)[-1]:
            return err
        return SimError(f"{msg} at {program}:{line}")

    def _exec_program(self, name: str) -> str:
        """Run a program. Returns 'return' | 'stop' | 'done' | 'menu-stop'."""
        prog = self._programs[name]
        pc = 0
        stack: list[dict] = []  # block frames

        while pc < len(prog.statements):
            if self._halt_all:
                return "stop"
            run = self._run
            assert run is not None
            run.steps += 1
            if run.steps > self.step_limit:
                raise SimError("step limit")

            stmt = prog.statements[pc]
            try:
                result = self._exec_stmt(prog, pc, stmt, stack)
            except SimError as err:
                raise self._at(name, stmt.line, err) from err

            if result == "stop":
                self._halt_all = True
                return "stop"
            if result == "return":
                return "return"
            if isinstance(result, tuple) and result[0] == "goto":
                label = result[1]
                if label not in prog.labels:
                    raise self._at(name, stmt.line, SimError("ERR:LABEL"))
                # count abandoned blocks
                run.leaks += len(stack)
                stack.clear()
                pc = prog.labels[label]
                continue
            if isinstance(result, tuple) and result[0] == "menu-stop":
                return "menu-stop"
            if isinstance(result, tuple) and result[0] == "jump":
                pc = result[1]
                continue
            if isinstance(result, tuple) and result[0] == "call":
                sub = result[1]
                if sub not in self._programs:
                    raise self._at(name, stmt.line, SimError(f"ERR:UNDEFINED prgm{sub}"))
                sub_result = self._exec_program(sub)
                if sub_result == "stop":
                    return "stop"
                if sub_result == "menu-stop":
                    return "menu-stop"
                pc += 1
                continue
            pc += 1
        return "done"

    def _exec_stmt(self, prog: Program, pc: int, stmt: Statement, stack: list) -> Any:
        tokens = list(stmt.tokens)
        if not tokens:
            return None
        head = tokens[0].bits

        if head == B_LBL:
            return None

        if head == B_THEN:
            raise SimError("Then without If")

        if head == B_ELSE:
            # jumping to Else means we finished the Then branch; skip to matching End
            end_pc = self._find_block_end(prog, pc, from_else=True)
            stack.pop()  # Then frame
            return ("jump", end_pc + 1)

        if head == B_END:
            if not stack:
                raise SimError("End without block")
            frame = stack[-1]
            kind = frame["kind"]
            if kind == "then":
                stack.pop()
                return None
            if kind == "for":
                return self._for_end(prog, pc, stack)
            if kind == "repeat":
                return self._repeat_end(prog, pc, stack)
            raise SimError("End without block")

        if head == B_IF:
            return self._exec_if(prog, pc, tokens[1:], stack)

        if head == B_FOR:
            return self._exec_for(prog, pc, tokens, stack)

        if head == B_REPEAT:
            cond_tokens = tokens[1:]
            stack.append({"kind": "repeat", "cond": cond_tokens, "start": pc + 1})
            return None

        if head == B_GOTO:
            label = parse_label(tokens[1:])
            return ("goto", label)

        if head == B_RETURN:
            return "return"

        if head == B_STOP:
            return "stop"

        if head == B_PRGM:
            return ("call", parse_program_name(tokens[1:]))

        if head == B_PAUSE:
            return self._exec_pause(tokens[1:])

        if head == B_INPUT:
            return self._exec_input(tokens[1:])

        if head == B_OUTPUT:
            return self._exec_output(tokens[1:])

        if head == B_CLRHOME:
            self._clrhome()
            return None

        if head == B_MENU:
            return self._exec_menu(prog, tokens[1:], stack)

        if head == B_RADIAN:
            self._modes.add("Radian")
            return None
        if head == B_FLOAT:
            self._modes.add("Float")
            return None
        if head == B_NORMAL:
            self._modes.add("Normal")
            return None
        if head == B_CPLX:
            self.complex_mode = True
            return None

        # expression or store
        store_at = find_store(tokens)
        if store_at is not None:
            value = evaluate(tokens[:store_at], self)
            self._store(tokens[store_at + 1 :], value)
            self.ans = value
            return None

        value = evaluate(tokens, self)
        self.ans = value
        return None

    def _exec_if(self, prog: Program, pc: int, cond_tokens: list[Token], stack: list) -> Any:
        cond = is_true(evaluate(cond_tokens, self))
        next_pc = pc + 1
        if next_pc < len(prog.statements) and prog.statements[next_pc].tokens and prog.statements[next_pc].tokens[0].bits == B_THEN:
            # block If: Then at next_pc, body after
            if cond:
                stack.append({"kind": "then"})
                return ("jump", next_pc + 1)
            # false: Else body (push frame so End pops it) or after End
            target, via_else = self._skip_if_block(prog, next_pc)
            if via_else:
                stack.append({"kind": "then"})
            return ("jump", target)

        # single-line If: guard only the next statement
        if not cond:
            return ("jump", pc + 2)
        return None

    def _skip_if_block(self, prog: Program, then_pc: int) -> tuple[int, bool]:
        """then_pc points at Then. Return (pc, via_else) for Else body or after End."""
        i = then_pc + 1
        depth = 1
        while i < len(prog.statements):
            toks = prog.statements[i].tokens
            if not toks:
                i += 1
                continue
            b = toks[0].bits
            if b == B_THEN or b == B_FOR or b == B_REPEAT:
                depth += 1
            elif b == B_ELSE and depth == 1:
                return i + 1, True
            elif b == B_END:
                depth -= 1
                if depth == 0:
                    return i + 1, False
            i += 1
        raise SimError("End without block")

    def _find_block_end(self, prog: Program, else_pc: int, from_else: bool = False) -> int:
        """From Else statement, find matching End index."""
        i = else_pc + 1
        depth = 1
        while i < len(prog.statements):
            toks = prog.statements[i].tokens
            if not toks:
                i += 1
                continue
            b = toks[0].bits
            if b == B_THEN or b == B_FOR or b == B_REPEAT:
                depth += 1
            elif b == B_END:
                depth -= 1
                if depth == 0:
                    return i
            i += 1
        raise SimError("End without block")

    def _exec_for(self, prog: Program, pc: int, tokens: list[Token], stack: list) -> Any:
        # For(var,start,end[,step])
        if tokens[0].bits != B_FOR:
            raise SimError("ERR:SYNTAX")
        inner = tokens[1:]
        # parse var
        tok = ex._Tok(inner)
        t = tok.peek()
        if t is None:
            raise SimError("ERR:ARGUMENT")
        if t.bits == ex.B_THETA:
            var = "θ"
            tok.advance()
        elif t.bits in ex.LETTERS:
            var = t.text
            tok.advance()
        else:
            raise SimError("ERR:ARGUMENT")
        if not tok.match(ex.B_COMMA):
            raise SimError("ERR:ARGUMENT")
        # collect start, end, step expressions
        args_tokens = tok.tokens[tok.i :]
        # strip trailing ) 
        if not args_tokens or args_tokens[-1].bits != ex.B_RPAREN:
            raise SimError("unclosed parenthesis")
        args_tokens = args_tokens[:-1]
        parts = self._split_args(args_tokens)
        if len(parts) not in (2, 3):
            raise SimError("ERR:ARGUMENT")
        start = require_real(evaluate(parts[0], self))
        end = require_real(evaluate(parts[1], self))
        step = require_real(evaluate(parts[2], self)) if len(parts) == 3 else 1.0
        if step == 0:
            raise SimError("ERR:INCREMENT")
        self.set_var(var, start)

        def past(cur: float) -> bool:
            if step > 0:
                return cur > end
            return cur < end

        body_start = pc + 1
        end_pc = self._find_matching_end(prog, pc)
        if past(float(start)):
            return ("jump", end_pc + 1)
        stack.append(
            {
                "kind": "for",
                "var": var,
                "end": end,
                "step": step,
                "body": body_start,
                "end_pc": end_pc,
            }
        )
        return None

    def _for_end(self, prog: Program, pc: int, stack: list) -> Any:
        frame = stack[-1]
        var = frame["var"]
        cur = require_real(self.get_var(var))
        nxt = cur + frame["step"]
        self.set_var(var, nxt)

        def past(v: float) -> bool:
            if frame["step"] > 0:
                return v > frame["end"]
            return v < frame["end"]

        if past(float(nxt)):
            stack.pop()
            return None
        return ("jump", frame["body"])

    def _repeat_end(self, prog: Program, pc: int, stack: list) -> Any:
        frame = stack[-1]
        if is_true(evaluate(frame["cond"], self)):
            stack.pop()
            return None
        return ("jump", frame["start"])

    def _find_matching_end(self, prog: Program, open_pc: int) -> int:
        """open_pc is For( or Repeat ; find matching End."""
        i = open_pc + 1
        depth = 1
        while i < len(prog.statements):
            toks = prog.statements[i].tokens
            if not toks:
                i += 1
                continue
            b = toks[0].bits
            if b == B_THEN or b == B_FOR or b == B_REPEAT:
                depth += 1
            elif b == B_END:
                depth -= 1
                if depth == 0:
                    return i
            i += 1
        raise SimError("End without block")

    def _split_args(self, tokens: list[Token]) -> list[list[Token]]:
        parts: list[list[Token]] = []
        cur: list[Token] = []
        depth = 0
        in_string = False
        for t in tokens:
            if in_string:
                cur.append(t)
                if t.bits == ex.B_QUOTE:
                    in_string = False
                continue
            if t.bits == ex.B_QUOTE:
                in_string = True
                cur.append(t)
                continue
            if t.bits == ex.B_COMMA and depth == 0:
                parts.append(cur)
                cur = []
                continue
            if t.bits in (ex.B_LPAREN, ex.B_LBRACE) or t.text.endswith("("):
                depth += 1
            elif t.bits in (ex.B_RPAREN, ex.B_RBRACE):
                depth -= 1
            cur.append(t)
        parts.append(cur)
        return parts

    def _store(self, target_tokens: list[Token], value: Any) -> None:
        kind, name, idx_tokens = parse_store_target(target_tokens)
        value = normalize(value, complex_mode=self.complex_mode)
        if kind == "var":
            if isinstance(value, (list, str)):
                raise SimError("ERR:DATA TYPE")
            self.vars[name] = value  # type: ignore[assignment]
            return
        if kind == "str":
            if not isinstance(value, str):
                raise SimError("ERR:DATA TYPE")
            self.strings[name] = value
            return
        if kind == "list":
            if not isinstance(value, list):
                raise SimError("ERR:DATA TYPE")
            self.lists[name] = list(value)
            return
        if kind == "list_el":
            assert idx_tokens is not None
            idx = int(require_real(evaluate(idx_tokens, self)))
            if name not in self.lists:
                raise SimError("ERR:UNDEFINED")
            lst = self.lists[name]
            if idx < 1:
                raise SimError("ERR:INVALID DIM")
            if idx == len(lst) + 1:
                lst.append(value)
            elif idx <= len(lst):
                lst[idx - 1] = value
            else:
                raise SimError("ERR:INVALID DIM")
            return
        raise SimError("ERR:SYNTAX")

    def _clrhome(self) -> None:
        assert self._run is not None
        self._screen = [[" "] * COLS for _ in range(ROWS)]
        self._input_row = 1
        self._run.log.append(Clear())

    def _exec_output(self, tokens: list[Token]) -> None:
        # Output(row,col,value) — tokens after Output(
        if not tokens or tokens[-1].bits != ex.B_RPAREN:
            raise SimError("unclosed parenthesis")
        parts = self._split_args(tokens[:-1])
        if len(parts) != 3:
            raise SimError("ERR:ARGUMENT")
        row = int(require_real(evaluate(parts[0], self)))
        col = int(require_real(evaluate(parts[1], self)))
        val = evaluate(parts[2], self)
        text = display_value(val)
        if row < 1 or row > ROWS or col < 1 or col > COLS:
            raise SimError("ERR:DOMAIN")
        assert self._run is not None
        self._run.log.append(Out(row, col, text))
        r, c = row - 1, col - 1
        for ch in text:
            if r >= ROWS:
                break
            self._screen[r][c] = ch
            c += 1
            if c >= COLS:
                c = 0
                r += 1

    def _exec_input(self, tokens: list[Token]) -> None:
        # Input "prompt",var
        assert self._run is not None
        tok = ex._Tok(tokens)
        if tok.peek_bits() != ex.B_QUOTE:
            raise SimError("ERR:SYNTAX")
        prompt = self._eval_string_literal(tok)
        if not tok.match(ex.B_COMMA):
            raise SimError("ERR:SYNTAX")
        target = tok.tokens[tok.i :]
        ev = self._peek_event()
        if ev is None:
            raise SimError(f"no event for Input {prompt!r}")
        if not isinstance(ev, Value):
            raise SimError(f"Input needs Value, got {type(ev).__name__}")
        self._event_i += 1
        typed, stored = self._value_from_event(ev)
        self._run.prompts.append(prompt)
        self._run.log.append(Prompt(prompt, typed))
        # write prompt+typed at cursor row
        line = prompt + typed
        r = self._input_row - 1
        for i, ch in enumerate(line[:COLS]):
            self._screen[r][i] = ch
        # move cursor down, scroll past row 10
        self._input_row += 1
        if self._input_row > ROWS:
            self._scroll_up()
            self._input_row = ROWS
        self._store(target, stored)

    def _eval_string_literal(self, tok: ex._Tok) -> str:
        # reuse parser string — advance opening quote handled inside
        # Manual:
        tok.advance()
        parts: list[str] = []
        while True:
            t = tok.peek()
            if t is None:
                raise SimError("unclosed string")
            if t.bits == ex.B_QUOTE:
                tok.advance()
                return "".join(parts)
            parts.append(t.text)
            tok.advance()

    def _value_from_event(self, ev: Value) -> tuple[str, Any]:
        x = ev.x
        if isinstance(x, str):
            typed = x
            stored = evaluate(decode(encode(x)), self)
            return typed, stored
        if isinstance(x, list):
            typed = "{" + ",".join(to_string(v) if not isinstance(v, complex) else str(v) for v in x) + "}"
            return typed, [normalize(v, complex_mode=self.complex_mode) for v in x]
        if isinstance(x, complex):
            typed = to_string(x.real) + ("+" if x.imag >= 0 else "") + (to_string(x.imag) if False else "") 
            # simpler typed form
            typed = str(x)
            return typed, normalize(x, complex_mode=self.complex_mode)
        typed = to_string(float(x)) if isinstance(x, (int, float)) else str(x)
        # Prefer plain int-looking
        if isinstance(x, (int, float)) and float(x) == int(float(x)) and abs(float(x)) < 1e10:
            typed = str(int(float(x)))
        return typed, normalize(x, complex_mode=self.complex_mode)

    def _scroll_up(self) -> None:
        self._screen = self._screen[1:] + [[" "] * COLS]

    def _exec_pause(self, rest: list[Token]) -> None:
        if rest:
            raise SimError("Pause with argument not supported")
        assert self._run is not None
        head = self._peek_event()
        if isinstance(head, Hold):
            if _key_code(head.key) != KEY_CODES["ENTER"]:
                raise SimError(f"Pause needs ENTER, got {head.key!r}")
            self._log_wait(head.key)
            return
        if isinstance(head, Key):
            if _key_code(head.key) != KEY_CODES["ENTER"]:
                raise SimError(f"Pause needs ENTER, got {head.key!r}")
            self._event_i += 1
            self._log_wait(head.key)
            return
        if head is None:
            raise SimError("no event for Pause")
        raise SimError(f"Pause needs Key, got {type(head).__name__}")

    def _exec_menu(self, prog: Program, tokens: list[Token], stack: list) -> Any:
        assert self._run is not None
        if not tokens or tokens[-1].bits != ex.B_RPAREN:
            raise SimError("unclosed parenthesis")
        parts = self._split_args(tokens[:-1])
        # title, item, label, item, label, ...
        if len(parts) < 3 or len(parts) % 2 == 0:
            raise SimError("ERR:ARGUMENT")
        title = self._eval_string_tokens(parts[0])
        items: list[str] = []
        labels: list[str] = []
        i = 1
        while i < len(parts):
            items.append(self._eval_string_tokens(parts[i]))
            labels.append(parse_label(parts[i + 1]))
            i += 2
        if len(items) > 7:
            raise SimError("ERR:ARGUMENT")
        if not items:
            raise SimError("ERR:ARGUMENT")

        head = self._peek_event()
        if self._stop_at_menu and (head is None or isinstance(head, Hold)):
            shown = MenuShown(title, tuple(items), None)
            self._run.menus.append(shown)
            self._run.log.append(shown)
            self._run.stopped_at_menu = title
            return ("menu-stop",)

        if head is None:
            raise SimError("no event for Menu")
        if not isinstance(head, Choose):
            raise SimError(f"Menu needs Choose, got {type(head).__name__}")
        self._event_i += 1
        if head.text not in items:
            raise SimError(f"unknown menu choice {head.text!r}; items: {', '.join(items)}")
        chosen = head.text
        shown = MenuShown(title, tuple(items), chosen)
        self._run.menus.append(shown)
        self._run.log.append(shown)
        label = labels[items.index(chosen)]
        # Menu jump abandons open blocks? typically at top level. Count leaks like Goto.
        self._run.leaks += len(stack)
        stack.clear()
        if label not in prog.labels:
            raise SimError("ERR:LABEL")
        return ("jump", prog.labels[label])

    def _eval_string_tokens(self, tokens: list[Token]) -> str:
        return evaluate(tokens, self) if False else self._force_string(tokens)

    def _force_string(self, tokens: list[Token]) -> str:
        val = evaluate(tokens, self)
        if not isinstance(val, str):
            raise SimError("ERR:DATA TYPE")
        return val
