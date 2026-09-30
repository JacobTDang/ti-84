"""Expression parser and evaluator for the TI-BASIC dialect."""

from __future__ import annotations

import cmath
import math
from typing import Any, Callable, Protocol

from ti84.tokens import DIALECT, Token

from ti84.sim.values import (
    SimError,
    is_true,
    normalize,
    require_number,
    require_real,
    round_half_up,
    to_string,
    zip_lists,
)

B_QUOTE = b"\x2a"
B_LPAREN = b"\x10"
B_RPAREN = b"\x11"
B_LBRACE = b"\x08"
B_RBRACE = b"\x09"
B_COMMA = b"\x2b"
B_PLUS = b"\x70"
B_MINUS = b"\x71"
B_MUL = b"\x82"
B_DIV = b"\x83"
B_POW = b"\xf0"
B_SQ = b"\x0d"
B_INV = b"\x0c"
B_NEG = b"\xb0"
B_EQ = b"\x6a"
B_NE = b"\x6f"
B_LT = b"\x6b"
B_GT = b"\x6c"
B_LE = b"\x6d"
B_GE = b"\x6e"
B_AND = b"\x40"
B_OR = b"\x3c"
B_NOT = b"\xb8"
B_DOT = b"\x3a"
B_EE = b"\x3b"
B_I = b"\x2c"
B_PI = b"\xac"
B_ECONST = b"\xbb\x31"
B_ANS = b"\x72"
B_GETKEY = b"\xad"
B_THETA = b"\x5b"
B_NAMED = b"\xeb"
B_STORE = b"\x04"
B_SEQ = b"\x23"

DIGITS = {bytes([c]) for c in range(0x30, 0x3A)}
LETTERS = {bytes([c]) for c in range(0x41, 0x5B)}

LIST_TOKENS = {
    b"\x5d\x00": "L₁",
    b"\x5d\x01": "L₂",
    b"\x5d\x02": "L₃",
    b"\x5d\x03": "L₄",
    b"\x5d\x04": "L₅",
    b"\x5d\x05": "L₆",
}
STR_TOKENS = {
    b"\xaa\x00": "Str1",
    b"\xaa\x01": "Str2",
    b"\xaa\x02": "Str3",
    b"\xaa\x03": "Str4",
    b"\xaa\x04": "Str5",
    b"\xaa\x05": "Str6",
    b"\xaa\x06": "Str7",
    b"\xaa\x07": "Str8",
    b"\xaa\x08": "Str9",
    b"\xaa\x09": "Str0",
}

FN_BITS = {
    b"\xb2": "abs",
    b"\xbc": "sqrt",
    b"\xbe": "ln",
    b"\xc0": "log",
    b"\xbf": "exp",
    b"\xb1": "int",
    b"\x12": "round",
    b"\x1a": "min",
    b"\x19": "max",
    b"\xb6": "sum",
    b"\xb5": "dim",
    b"\xbb\x26": "real",
    b"\xbb\x27": "imag",
    b"\xbb\x28": "angle",
    b"\xbb\x25": "conj",
    b"\xc2": "sin",
    b"\xc4": "cos",
    b"\xc7": "atan",
    b"\xbb\x2b": "length",
    b"\xbb\x0c": "sub",
    b"\xef\x97": "toString",
}


class ExprContext(Protocol):
    def get_var(self, name: str) -> float | complex: ...
    def set_var(self, name: str, value: Any) -> None: ...
    def get_string(self, name: str) -> str: ...
    def get_list(self, name: str) -> list: ...
    def get_ans(self) -> Any: ...
    def get_key(self) -> float: ...

    @property
    def complex_mode(self) -> bool: ...


class _Tok:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.i = 0

    def peek(self) -> Token | None:
        if self.i >= len(self.tokens):
            return None
        return self.tokens[self.i]

    def peek_bits(self) -> bytes | None:
        t = self.peek()
        return None if t is None else t.bits

    def advance(self) -> Token:
        t = self.tokens[self.i]
        self.i += 1
        return t

    def match(self, bits: bytes) -> bool:
        if self.peek_bits() == bits:
            self.advance()
            return True
        return False

    def at_end(self) -> bool:
        return self.i >= len(self.tokens)


def parse_named_list(tok: _Tok) -> str:
    """After ⌊/ʟ, read a letter then up to 4 letters or digits."""
    parts = ["⌊"]
    first = tok.peek()
    if first is None or first.bits not in LETTERS:
        raise SimError("ERR:SYNTAX")
    parts.append(tok.advance().text)
    while True:
        t = tok.peek()
        if t is None:
            break
        if t.bits not in LETTERS and t.bits not in DIGITS:
            break
        if len(parts) - 1 >= 5:
            break
        parts.append(tok.advance().text)
    return "".join(parts)


def evaluate(tokens: list[Token], ctx: ExprContext) -> Any:
    parser = _Parser(tokens, ctx)
    value = parser.parse_or()
    if not parser.tok.at_end():
        nxt = parser.tok.peek()
        assert nxt is not None
        if _starts_primary(nxt.bits):
            raise SimError("implicit multiplication")
        raise SimError(f"unexpected token {nxt.text}")
    return normalize(value, complex_mode=ctx.complex_mode)


class _Parser:
    def __init__(self, tokens: list[Token], ctx: ExprContext):
        self.tok = _Tok(tokens)
        self.ctx = ctx

    def parse_or(self) -> Any:
        left = self.parse_and()
        while self.tok.match(B_OR):
            right = self.parse_and()
            left = 1.0 if (is_true(left) or is_true(right)) else 0.0
        return left

    def parse_and(self) -> Any:
        left = self.parse_cmp()
        while self.tok.match(B_AND):
            right = self.parse_cmp()
            left = 1.0 if (is_true(left) and is_true(right)) else 0.0
        return left

    def parse_cmp(self) -> Any:
        left = self.parse_add()
        op = self.tok.peek_bits()
        if op in (B_EQ, B_NE, B_LT, B_GT, B_LE, B_GE):
            self.tok.advance()
            right = self.parse_add()
            return self._cmp(op, left, right)
        return left

    def _cmp(self, op: bytes, a: Any, b: Any) -> Any:
        if isinstance(a, str) or isinstance(b, str):
            if not isinstance(a, str) or not isinstance(b, str):
                raise SimError("ERR:DATA TYPE")
            if op == B_EQ:
                return 1.0 if a == b else 0.0
            if op == B_NE:
                return 1.0 if a != b else 0.0
            raise SimError("ERR:DATA TYPE")

        def one(x: Any, y: Any) -> float:
            if op == B_EQ:
                return 1.0 if x == y else 0.0
            if op == B_NE:
                return 1.0 if x != y else 0.0
            xr, yr = require_real(x), require_real(y)
            if op == B_LT:
                return 1.0 if xr < yr else 0.0
            if op == B_GT:
                return 1.0 if xr > yr else 0.0
            if op == B_LE:
                return 1.0 if xr <= yr else 0.0
            if op == B_GE:
                return 1.0 if xr >= yr else 0.0
            raise SimError("ERR:SYNTAX")

        return zip_lists(a, b, one)

    def parse_add(self) -> Any:
        left = self.parse_mul()
        while True:
            bits = self.tok.peek_bits()
            if bits == B_PLUS:
                self.tok.advance()
                right = self.parse_mul()
                left = self._add(left, right)
            elif bits == B_MINUS:
                self.tok.advance()
                right = self.parse_mul()
                left = zip_lists(left, right, lambda x, y: require_number(x) - require_number(y))
            else:
                break
        return left

    def _add(self, a: Any, b: Any) -> Any:
        if isinstance(a, str) or isinstance(b, str):
            if not isinstance(a, str) or not isinstance(b, str):
                raise SimError("ERR:DATA TYPE")
            return a + b
        return zip_lists(a, b, lambda x, y: require_number(x) + require_number(y))

    def parse_mul(self) -> Any:
        left = self.parse_unary()
        while True:
            bits = self.tok.peek_bits()
            if bits == B_MUL:
                self.tok.advance()
                right = self.parse_unary()
                left = zip_lists(left, right, lambda x, y: require_number(x) * require_number(y))
            elif bits == B_DIV:
                self.tok.advance()
                right = self.parse_unary()
                left = zip_lists(left, right, self._div)
            else:
                nxt = self.tok.peek()
                if nxt is not None and _starts_primary(nxt.bits):
                    raise SimError("implicit multiplication")
                break
        return left

    def _div(self, x: Any, y: Any) -> Any:
        x, y = require_number(x), require_number(y)
        if y == 0 or y == 0j:
            raise SimError("ERR:DIVIDE BY 0")
        return x / y

    def parse_unary(self) -> Any:
        if self.tok.match(B_NEG):
            return self._neg(self.parse_unary())
        if self.tok.peek_bits() == B_MINUS:
            raise SimError("'-' starts an expression")
        return self.parse_power()

    def _neg(self, val: Any) -> Any:
        if isinstance(val, list):
            return [self._neg(v) for v in val]
        return -require_number(val)

    def parse_power(self) -> Any:
        left = self.parse_postfix()
        while self.tok.match(B_POW):
            right = self._parse_exponent()
            left = zip_lists(left, right, self._pow)
        return left

    def _parse_exponent(self) -> Any:
        """The operand after ^, which may be negated: 2^⁻2 is 0.25."""
        if self.tok.match(B_NEG):
            return self._neg(self._parse_exponent())
        return self.parse_postfix()

    def _pow(self, x: Any, y: Any) -> Any:
        x, y = require_number(x), require_number(y)
        y_real_neg = isinstance(y, (int, float)) and y < 0
        y_cplx_neg = isinstance(y, complex) and y.imag == 0 and y.real < 0
        if x == 0 and (y == 0 or y_real_neg or y_cplx_neg):
            raise SimError("ERR:DOMAIN")
        try:
            return x**y
        except ZeroDivisionError as err:
            raise SimError("ERR:DIVIDE BY 0") from err
        except ValueError as err:
            raise SimError("ERR:DOMAIN") from err

    def parse_postfix(self) -> Any:
        val = self.parse_primary()
        while True:
            bits = self.tok.peek_bits()
            if bits == B_SQ:
                self.tok.advance()
                val = self._sq(val)
            elif bits == B_INV:
                self.tok.advance()
                val = self._inv(val)
            else:
                break
        return val

    def _sq(self, val: Any) -> Any:
        if isinstance(val, list):
            return [self._sq(v) for v in val]
        return require_number(val) ** 2

    def _inv(self, val: Any) -> Any:
        if isinstance(val, list):
            return [self._inv(v) for v in val]
        x = require_number(val)
        if x == 0 or x == 0j:
            raise SimError("ERR:DIVIDE BY 0")
        return 1 / x

    def parse_primary(self) -> Any:
        t = self.tok.peek()
        if t is None:
            raise SimError("unexpected end of expression")
        bits = t.bits

        if bits == B_MINUS:
            raise SimError("'-' starts an expression")

        if bits in DIGITS or bits == B_DOT or bits == B_EE:
            return self._parse_number()

        if bits == B_I:
            self.tok.advance()
            return 1j

        if bits == B_PI:
            self.tok.advance()
            return float(math.pi)

        if bits == B_ECONST:
            self.tok.advance()
            return float(math.e)

        if bits == B_QUOTE:
            return self._parse_string()

        if bits == B_LBRACE:
            return self._parse_list_lit()

        if bits == B_LPAREN:
            self.tok.advance()
            val = self.parse_or()
            if not self.tok.match(B_RPAREN):
                raise SimError("unclosed parenthesis")
            return val

        if bits == B_ANS:
            self.tok.advance()
            return self.ctx.get_ans()

        if bits == B_GETKEY:
            self.tok.advance()
            return self.ctx.get_key()

        if bits == B_NOT:
            self.tok.advance()
            arg = self.parse_or()
            if not self.tok.match(B_RPAREN):
                raise SimError("unclosed parenthesis")
            return 0.0 if is_true(arg) else 1.0

        if bits == B_SEQ:
            return self._parse_seq()

        if bits in FN_BITS:
            return self._call_fn(FN_BITS[bits])

        if bits in STR_TOKENS:
            self.tok.advance()
            return self.ctx.get_string(STR_TOKENS[bits])

        if bits in LIST_TOKENS:
            self.tok.advance()
            return self._finish_list_ref(LIST_TOKENS[bits])

        if bits == B_NAMED:
            self.tok.advance()
            name = parse_named_list(self.tok)
            return self._finish_list_ref(name)

        if bits == B_THETA or bits in LETTERS:
            name = "θ" if bits == B_THETA else t.text
            self.tok.advance()
            return self.ctx.get_var(name)

        raise SimError(f"unsupported token {t.text}")

    def _parse_number(self) -> Any:
        chars: list[str] = []
        saw_digit = False
        saw_dot = False
        if self.tok.peek_bits() == B_EE:
            chars.append("1")
        while True:
            bits = self.tok.peek_bits()
            if bits in DIGITS:
                chars.append(self.tok.advance().text)
                saw_digit = True
            elif bits == B_DOT and not saw_dot:
                chars.append(".")
                self.tok.advance()
                saw_dot = True
            else:
                break
        if self.tok.match(B_EE):
            chars.append("e")
            if self.tok.match(B_NEG):
                chars.append("-")
            elif self.tok.peek_bits() == B_MINUS:
                raise SimError("'-' starts an expression")
            exp_digits = False
            while self.tok.peek_bits() in DIGITS:
                chars.append(self.tok.advance().text)
                exp_digits = True
            if not exp_digits:
                raise SimError("ERR:SYNTAX")
            saw_digit = True
        if not saw_digit:
            raise SimError("ERR:SYNTAX")
        value: Any = float("".join(chars))
        if self.tok.match(B_I):
            value = complex(0.0, float(value))
        return value

    def _parse_string(self) -> str:
        self.tok.advance()  # opening "
        parts: list[str] = []
        while True:
            t = self.tok.peek()
            if t is None:
                raise SimError("unclosed string")
            if t.bits == B_QUOTE:
                self.tok.advance()
                return "".join(parts)
            if t.bits == B_STORE:
                return "".join(parts)
            parts.append(t.text)
            self.tok.advance()

    def _parse_list_lit(self) -> list:
        self.tok.advance()  # {
        if self.tok.match(B_RBRACE):
            return []
        items = [self.parse_or()]
        while self.tok.match(B_COMMA):
            items.append(self.parse_or())
        if not self.tok.match(B_RBRACE):
            raise SimError("unclosed list")
        return items

    def _finish_list_ref(self, name: str) -> Any:
        if self.tok.match(B_LPAREN):
            idx_val = self.parse_or()
            if not self.tok.match(B_RPAREN):
                raise SimError("unclosed parenthesis")
            idx = int(require_real(idx_val))
            lst = self.ctx.get_list(name)
            if idx < 1 or idx > len(lst):
                raise SimError("ERR:INVALID DIM")
            return lst[idx - 1]
        return list(self.ctx.get_list(name))

    def _parse_seq(self) -> list:
        self.tok.advance()  # seq(
        expr_tokens = self._collect_until_comma()
        var = self._parse_var_name()
        if not self.tok.match(B_COMMA):
            raise SimError("ERR:ARGUMENT")
        start = require_real(self.parse_or())
        if not self.tok.match(B_COMMA):
            raise SimError("ERR:ARGUMENT")
        end = require_real(self.parse_or())
        step = 1.0
        if self.tok.match(B_COMMA):
            step = require_real(self.parse_or())
        if not self.tok.match(B_RPAREN):
            raise SimError("unclosed parenthesis")
        if step == 0:
            raise SimError("ERR:INCREMENT")
        had = self.ctx.has_var(var)
        previous = self.ctx.get_var(var)

        result: list[Any] = []
        x = start

        def past(cur: float) -> bool:
            if step > 0:
                return cur > end
            return cur < end

        try:
            while not past(x):
                self.ctx.set_var(var, float(x))
                result.append(evaluate(expr_tokens, self.ctx))
                x += step
        finally:
            if had:
                self.ctx.set_var(var, previous)
            else:
                self.ctx.clear_var(var)
        return result

    def _collect_until_comma(self) -> list[Token]:
        depth = 0
        out: list[Token] = []
        while True:
            t = self.tok.peek()
            if t is None:
                raise SimError("unclosed parenthesis")
            if t.bits == B_COMMA and depth == 0:
                self.tok.advance()
                if not out:
                    raise SimError("ERR:ARGUMENT")
                return out
            if t.bits in (B_LPAREN, B_LBRACE) or t.bits in FN_BITS or t.bits == B_NOT or t.bits == B_SEQ:
                # fn tokens include '(', so they open depth
                if t.bits in (B_LPAREN, B_LBRACE) or t.text.endswith("("):
                    depth += 1
                out.append(self.tok.advance())
                continue
            if t.bits in (B_RPAREN, B_RBRACE):
                if depth == 0:
                    raise SimError("ERR:ARGUMENT")
                depth -= 1
                out.append(self.tok.advance())
                continue
            if t.bits == B_QUOTE:
                out.append(self.tok.advance())
                while True:
                    s = self.tok.peek()
                    if s is None:
                        raise SimError("unclosed string")
                    out.append(self.tok.advance())
                    if s.bits == B_QUOTE:
                        break
                continue
            out.append(self.tok.advance())

    def _parse_var_name(self) -> str:
        t = self.tok.peek()
        if t is None:
            raise SimError("ERR:ARGUMENT")
        if t.bits == B_THETA:
            self.tok.advance()
            return "θ"
        if t.bits in LETTERS:
            self.tok.advance()
            return t.text
        raise SimError("ERR:ARGUMENT")

    def _call_fn(self, name: str) -> Any:
        self.tok.advance()
        args = self._parse_args()
        return self._dispatch(name, args)

    def _parse_args(self) -> list[Any]:
        if self.tok.match(B_RPAREN):
            return []
        args = [self.parse_or()]
        while self.tok.match(B_COMMA):
            args.append(self.parse_or())
        if not self.tok.match(B_RPAREN):
            raise SimError("unclosed parenthesis")
        return args

    def _dispatch(self, name: str, args: list[Any]) -> Any:
        if name == "abs":
            self._arity(args, 1)
            return self._map1(args[0], lambda x: abs(require_number(x)))
        if name == "sqrt":
            self._arity(args, 1)
            return self._map1(args[0], self._sqrt)
        if name == "ln":
            self._arity(args, 1)
            return self._map1(args[0], self._ln)
        if name == "log":
            self._arity(args, 1)
            return self._map1(args[0], self._log10)
        if name == "exp":
            self._arity(args, 1)
            return self._map1(args[0], self._exp)
        if name == "int":
            self._arity(args, 1)
            return self._map1(args[0], lambda x: float(math.floor(require_real(x))))
        if name == "round":
            self._arity(args, 2)
            return round_half_up(require_real(args[0]), int(require_real(args[1])))
        if name == "min":
            return self._min_max(args, min)
        if name == "max":
            return self._min_max(args, max)
        if name == "sum":
            self._arity(args, 1)
            if not isinstance(args[0], list):
                raise SimError("ERR:DATA TYPE")
            total: Any = 0.0
            for v in args[0]:
                total = require_number(total) + require_number(v)
            return total
        if name == "dim":
            self._arity(args, 1)
            if not isinstance(args[0], list):
                raise SimError("ERR:DATA TYPE")
            return float(len(args[0]))
        if name == "real":
            self._arity(args, 1)
            return self._map1(args[0], self._real)
        if name == "imag":
            self._arity(args, 1)
            return self._map1(args[0], self._imag)
        if name == "angle":
            self._arity(args, 1)
            return self._map1(args[0], self._angle)
        if name == "conj":
            self._arity(args, 1)
            return self._map1(args[0], self._conj)
        if name == "sin":
            self._arity(args, 1)
            return self._map1(args[0], lambda x: math.sin(require_real(x)))
        if name == "cos":
            self._arity(args, 1)
            return self._map1(args[0], lambda x: math.cos(require_real(x)))
        if name == "atan":
            self._arity(args, 1)
            return self._map1(args[0], lambda x: math.atan(require_real(x)))
        if name == "length":
            self._arity(args, 1)
            if not isinstance(args[0], str):
                raise SimError("ERR:DATA TYPE")
            return float(len(args[0]))
        if name == "sub":
            self._arity(args, 3)
            s = args[0]
            if not isinstance(s, str):
                raise SimError("ERR:DATA TYPE")
            start = int(require_real(args[1]))
            length = int(require_real(args[2]))
            return s[start - 1 : start - 1 + length]
        if name == "toString":
            self._arity(args, 1)
            return to_string(args[0])
        raise SimError(f"unsupported token {name}")

    def _arity(self, args: list, n: int) -> None:
        if len(args) != n:
            raise SimError("ERR:ARGUMENT")

    def _map1(self, val: Any, fn: Callable[[Any], Any]) -> Any:
        if isinstance(val, list):
            return [fn(v) for v in val]
        return fn(val)

    def _sqrt(self, x: Any) -> Any:
        x = require_number(x)
        if isinstance(x, complex) or x < 0:
            return cmath.sqrt(x)
        return math.sqrt(float(x))

    def _ln(self, x: Any) -> Any:
        x = require_number(x)
        if x == 0 or x == 0j:
            raise SimError("ERR:DOMAIN")
        if isinstance(x, complex) or (isinstance(x, (int, float)) and x < 0):
            return cmath.log(x)
        return math.log(float(x))

    def _log10(self, x: Any) -> Any:
        x = require_number(x)
        if x == 0 or x == 0j:
            raise SimError("ERR:DOMAIN")
        if isinstance(x, complex) or (isinstance(x, (int, float)) and x < 0):
            return cmath.log10(x)
        return math.log10(float(x))

    def _exp(self, x: Any) -> Any:
        x = require_number(x)
        if isinstance(x, complex):
            return cmath.exp(x)
        return math.exp(float(x))

    def _real(self, x: Any) -> float:
        x = require_number(x)
        if isinstance(x, complex):
            return float(x.real)
        return float(x)

    def _imag(self, x: Any) -> float:
        x = require_number(x)
        if isinstance(x, complex):
            return float(x.imag)
        return 0.0

    def _angle(self, x: Any) -> float:
        x = require_number(x)
        if isinstance(x, complex):
            return float(cmath.phase(x))
        if x < 0:
            return float(math.pi)
        return 0.0

    def _conj(self, x: Any) -> Any:
        x = require_number(x)
        if isinstance(x, complex):
            return x.conjugate()
        return x

    def _min_max(self, args: list[Any], fn) -> Any:
        if len(args) == 1:
            if not isinstance(args[0], list) or not args[0]:
                raise SimError("ERR:DATA TYPE")
            return fn(args[0])
        if len(args) == 2:
            if isinstance(args[0], list) or isinstance(args[1], list):
                raise SimError("ERR:DATA TYPE")
            return fn(args[0], args[1])
        raise SimError("ERR:ARGUMENT")


def _starts_primary(bits: bytes) -> bool:
    if bits in DIGITS or bits in (
        B_DOT,
        B_EE,
        B_I,
        B_PI,
        B_ECONST,
        B_QUOTE,
        B_LBRACE,
        B_LPAREN,
        B_ANS,
        B_GETKEY,
        B_NOT,
        B_THETA,
        B_NAMED,
        B_NEG,
        B_SEQ,
    ):
        return True
    if bits in LETTERS or bits in LIST_TOKENS or bits in STR_TOKENS or bits in FN_BITS:
        return True
    return False
