"""Text to TI-84 Plus CE token bytes and back, the dialect table, and the build-time lint.

This is the only module that imports tivars. See docs/dialect.md for the dialect.
"""

import re
from dataclasses import dataclass
from pathlib import Path

from tivars import TIProgram
from tivars.models import TI_84PCE
from tivars.tokenizer import decode as _decode
from tivars.tokenizer import encode as _encode


class TokenError(ValueError):
    """Text that can't become calculator tokens, or a bad program name."""


class LintError(ValueError):
    """Generated or hand-written code that breaks a dialect rule."""


@dataclass(frozen=True)
class Token:
    bits: bytes
    text: str


NEWLINE = b"\x3f"
COLON = b"\x3e"
QUOTE = b"\x2a"
STORE = b"\x04"
MINUS = b"\x71"
LETTER_E = b"\x45"

MIN_OS = TI_84PCE.OS("5.2.0")

# Canonical spellings of every code token the dialect allows (docs/dialect.md).
_SPELLINGS = (
    "ClrHome", "Output(", "Input ", "Pause ", "Menu(", "Lbl ", "Goto ", "If ", "Then", "Else", "End",
    "For(", "Repeat ", "Return", "Stop", "prgm", "→", "Radian", "Float", "Normal", "a+b𝑖",
    "getKey", "Ans", "θ", "Str1", "Str2", "Str3", "Str4", "Str5", "Str6", "Str7", "Str8", "Str9", "Str0",
    "L₁", "L₂", "L₃", "L₄", "L₅", "L₆", "⌊", '"', "{", "}", ",", "(", ")",
    "+", "-", "*", "/", "^", "²", "⁻¹", "⁻", "=", "≠", "<", ">", "≤", "≥", " and ", " or ", "not(",
    ".", "ᴇ", "𝑖", "pi", "𝑒",
    "abs(", "√(", "ln(", "log(", "𝑒^(", "int(", "round(", "min(", "max(", "sum(", "dim(", "seq(",
    "real(", "imag(", "angle(", "conj(", "sin(", "cos(", "tan⁻¹(", "length(", "sub(", "toString(",
    *"ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
)


def _dialect() -> dict[bytes, str]:
    table = {}
    for spelling in _SPELLINGS:
        data, _ = _encode(spelling)
        tokens, _ = _decode(data)
        if len(tokens) != 1:
            raise TokenError(f"dialect spelling {spelling!r} is {len(tokens)} tokens, not 1")
        table[tokens[0].bits] = str(tokens[0])
    return table


DIALECT: dict[bytes, str] = _dialect()

STRING_CHARS = frozenset(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 +-*/^=<>()[]{},.:;!?%&#@_$|"
    "²°ΩμΔ∠αβθστ≤≥⁻ᴇ𝑖"
)

# A '-' right after one of these starts an expression; on the calculator it would mean Ans-...
_OPERATORS = {
    b"\x70", b"\x71", b"\x82", b"\x83", b"\xf0", b"\xb0",
    b"\x6a", b"\x6f", b"\x6b", b"\x6c", b"\x6d", b"\x6e", b"\x40", b"\x3c",
    b"\x10", b"\x2b", b"\x08", STORE, NEWLINE, COLON,
}

_PROGRAM_NAME = re.compile(r"[A-Z][A-Z0-9]{0,7}")


def encode(text: str) -> bytes:
    data, _ = _encode_with_os(text)
    return data


def _encode_with_os(text: str):
    try:
        return _encode(text)
    except ValueError as err:
        raise TokenError(str(err)) from err


def decode(data: bytes) -> list[Token]:
    tokens, _ = _decode(data)
    return [Token(t.bits, str(t)) for t in tokens]


def _starts_expression(prev: Token | None) -> bool:
    if prev is None or prev.bits in _OPERATORS:
        return True
    return prev.text.endswith("(") or prev.text.endswith(" ")


def lint(text: str, program: str) -> None:
    """Raise LintError listing every dialect rule the code breaks, as '<program>:<line>: <message>'."""
    try:
        data, os_version = _encode_with_os(text)
    except TokenError as err:
        raise LintError(f"{program}: {err}") from err
    problems = []
    if not os_version <= MIN_OS:
        problems.append(f"{program}: needs {os_version.model} {os_version.version}, above TI-84+CE 5.2.0")

    line = 1
    in_string = False
    prev: Token | None = None
    for token in decode(data):
        if in_string:
            if token.bits == QUOTE:
                in_string = False
                prev = token
                continue
            if token.bits not in (STORE, NEWLINE):
                if len(token.text) != 1 or token.text not in STRING_CHARS:
                    problems.append(f"{program}:{line}: {token.text!r} does not round-trip in a string")
                continue
            in_string = False
        if token.bits == NEWLINE:
            line += 1
        elif token.bits == QUOTE:
            in_string = True
        elif len(token.bits) == 2 and token.bits[0] == 0xBB and 0xB0 <= token.bits[1] <= 0xCA:
            problems.append(
                f"{program}:{line}: lowercase letter {token.text!r} outside a string (use 𝑖, 𝑒 or ᴇ)"
            )
        elif token.bits == LETTER_E and prev is not None and prev.text in "0123456789.":
            problems.append(f"{program}:{line}: ASCII E after a number (use ᴇ)")
        elif token.bits == MINUS and _starts_expression(prev):
            problems.append(f"{program}:{line}: '-' starts an expression (use ⁻)")
        elif token.bits not in DIALECT:
            problems.append(f"{program}:{line}: token {token.text!r} is not in the dialect")
        prev = token
    if problems:
        raise LintError("\n".join(problems))


def _check_name(name: str) -> None:
    if not _PROGRAM_NAME.fullmatch(name):
        raise TokenError(f"program name {name!r} must be 1-8 uppercase letters or digits, starting with a letter")


def write_8xp(name: str, text: str, path: Path) -> None:
    _check_name(name)
    program = TIProgram(name=name)
    program.data = encode(text)
    program.save(str(path))


def read_8xp(path: Path) -> tuple[str, bytes]:
    program = TIProgram.open(str(path))
    return program.name, bytes(program.data)
