"""Numbers, lists, and toString formatting for the TI-BASIC dialect."""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Any


class SimError(Exception):
    """TI error name or rule, then ' at PROGRAM:LINE' when running a program."""


def normalize(value: Any, *, complex_mode: bool) -> Any:
    """Normalize a computed value: complex→float when imag is 0; reject NONREAL."""
    if isinstance(value, list):
        return [normalize(v, complex_mode=complex_mode) for v in value]
    if isinstance(value, complex):
        if value.imag == 0.0:
            return float(value.real)
        if not complex_mode:
            raise SimError("ERR:NONREAL")
        return complex(float(value.real), float(value.imag))
    if isinstance(value, bool):
        return float(value)
    if isinstance(value, int):
        return float(value)
    if isinstance(value, float):
        return float(value)
    if isinstance(value, str):
        return value
    raise SimError("ERR:DATA TYPE")


def is_true(value: Any) -> bool:
    if isinstance(value, list):
        raise SimError("ERR:DATA TYPE")
    if isinstance(value, str):
        raise SimError("ERR:DATA TYPE")
    if isinstance(value, complex):
        return value != 0
    return value != 0


def round_half_up(x: float, n: int) -> float:
    """round(x,n): n decimals, halves away from zero via Decimal ROUND_HALF_UP."""
    d = Decimal(repr(float(x)))
    quant = Decimal(1).scaleb(-int(n))
    return float(d.quantize(quant, rounding=ROUND_HALF_UP))


def _round_sig(d: Decimal, sig: int = 10) -> Decimal:
    if d == 0:
        return Decimal(0)
    adj = d.adjusted()
    quant = Decimal(1).scaleb(adj - sig + 1)
    return d.quantize(quant, rounding=ROUND_HALF_UP)


def _plain_decimal(d: Decimal) -> str:
    text = format(d, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text


def to_string(x: Any) -> str:
    """Normal Float toString: 10 sig figs, plain or scientific, ⁻ for negatives."""
    if isinstance(x, complex):
        raise SimError("ERR:DATA TYPE")
    if isinstance(x, list) or isinstance(x, str):
        raise SimError("ERR:DATA TYPE")
    d = Decimal(repr(float(x)))
    if d == 0:
        return "0"
    sign = "-" if d < 0 else ""
    d = abs(d)
    d = _round_sig(d, 10)
    if d == 0:
        return "0"
    abs_f = float(d)
    if 1e-3 <= abs_f < 1e10:
        body = _plain_decimal(d)
    else:
        # scientific: mantissa with 1–10 sig digits, trailing zeros dropped
        exp = d.adjusted()
        mant = d.scaleb(-exp)
        mant = _round_sig(mant, 10)
        # renormalize if rounding pushed to 10
        if mant >= 10:
            mant = mant.scaleb(-1)
            exp += 1
        mant_s = _plain_decimal(mant)
        exp_s = _format_exponent(exp)
        body = f"{mant_s}ᴇ{exp_s}"
    if sign:
        return "⁻" + body
    return body


def _format_exponent(exp: int) -> str:
    if exp < 0:
        return "⁻" + str(-exp)
    return str(exp)


def display_value(x: Any) -> str:
    if isinstance(x, str):
        return x
    if isinstance(x, list):
        raise SimError("ERR:DATA TYPE")
    return to_string(x)


def zip_lists(a: Any, b: Any, op):
    """Element-wise op for list/number or equal-length lists."""
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            raise SimError("ERR:DIM MISMATCH")
        return [op(x, y) for x, y in zip(a, b)]
    if isinstance(a, list):
        return [op(x, b) for x in a]
    if isinstance(b, list):
        return [op(a, y) for y in b]
    return op(a, b)


def require_number(x: Any) -> float | complex:
    if isinstance(x, (int, float, complex)) and not isinstance(x, bool):
        return x
    raise SimError("ERR:DATA TYPE")


def require_real(x: Any) -> float:
    x = require_number(x)
    if isinstance(x, complex):
        if x.imag != 0:
            raise SimError("ERR:DATA TYPE")
        return float(x.real)
    return float(x)
