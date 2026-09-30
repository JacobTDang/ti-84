"""Statement splitting, labels, and block structure for TI-BASIC programs."""

from __future__ import annotations

from dataclasses import dataclass

from ti84.tokens import Token, decode

from ti84.sim.expr import (
    B_QUOTE,
    B_STORE,
    DIGITS,
    LETTERS,
    LIST_TOKENS,
    STR_TOKENS,
    B_NAMED,
    B_THETA,
    B_LPAREN,
    B_RPAREN,
    B_COMMA,
    parse_named_list,
    _Tok,
)
from ti84.sim.values import SimError

NEWLINE = b"\x3f"
COLON = b"\x3e"

B_IF = b"\xce"
B_THEN = b"\xcf"
B_ELSE = b"\xd0"
B_END = b"\xd4"
B_FOR = b"\xd3"
B_REPEAT = b"\xd2"
B_LBL = b"\xd6"
B_GOTO = b"\xd7"
B_RETURN = b"\xd5"
B_STOP = b"\xd9"
B_PRGM = b"\x5f"
B_PAUSE = b"\xd8"
B_INPUT = b"\xdc"
B_OUTPUT = b"\xe0"
B_CLRHOME = b"\xe1"
B_MENU = b"\xe6"
B_RADIAN = b"\x64"
B_FLOAT = b"\x69"
B_NORMAL = b"\x66"
B_CPLX = b"\xbb\x4f"


@dataclass(frozen=True)
class Statement:
    tokens: tuple[Token, ...]
    line: int  # 1-based source line


@dataclass
class Program:
    name: str
    statements: list[Statement]
    labels: dict[str, int]  # label -> statement index


def split_statements(data: bytes) -> list[Statement]:
    tokens = decode(data)
    statements: list[Statement] = []
    current: list[Token] = []
    line = 1
    stmt_line = 1
    in_string = False
    for token in tokens:
        if in_string:
            current.append(token)
            if token.bits == B_QUOTE:
                in_string = False
            elif token.bits in (NEWLINE, B_STORE):
                # → or newline ends the string on the calculator; keep as statement break rules
                if token.bits == NEWLINE:
                    in_string = False
                    if current[:-1] or True:
                        # newline ends statement; the NEWLINE itself is not kept
                        body = current[:-1]
                        if body:
                            statements.append(Statement(tuple(body), stmt_line))
                        current = []
                        line += 1
                        stmt_line = line
                continue
            continue
        if token.bits == B_QUOTE:
            current.append(token)
            in_string = True
            continue
        if token.bits == NEWLINE:
            if current:
                statements.append(Statement(tuple(current), stmt_line))
                current = []
            line += 1
            stmt_line = line
            continue
        if token.bits == COLON:
            if current:
                statements.append(Statement(tuple(current), stmt_line))
                current = []
            # same line number
            continue
        if not current:
            stmt_line = line
        current.append(token)
    if current:
        statements.append(Statement(tuple(current), stmt_line))
    return statements


def build_program(name: str, data: bytes) -> Program:
    statements = split_statements(data)
    labels: dict[str, int] = {}
    for i, stmt in enumerate(statements):
        if not stmt.tokens:
            continue
        if stmt.tokens[0].bits == B_LBL:
            try:
                label = parse_label(list(stmt.tokens[1:]))
            except SimError as err:
                raise SimError(f"{err} at {name}:{stmt.line}") from err
            if label not in labels:
                labels[label] = i
    return Program(name=name, statements=statements, labels=labels)


def parse_label(tokens: list[Token]) -> str:
    if not tokens:
        raise SimError("ERR:LABEL")
    chars: list[str] = []
    for t in tokens:
        if t.bits in LETTERS or t.bits in DIGITS or t.bits == B_THETA:
            chars.append("θ" if t.bits == B_THETA else t.text)
            if len(chars) > 2:
                raise SimError("ERR:LABEL")
        else:
            raise SimError("ERR:LABEL")
    if not chars:
        raise SimError("ERR:LABEL")
    return "".join(chars)


def parse_program_name(tokens: list[Token]) -> str:
    if not tokens:
        raise SimError("ERR:UNDEFINED prgm")
    chars: list[str] = []
    for t in tokens:
        if t.bits in LETTERS or t.bits in DIGITS:
            chars.append(t.text)
        else:
            raise SimError(f"ERR:UNDEFINED prgm{''.join(chars)}")
    name = "".join(chars)
    if not name:
        raise SimError("ERR:UNDEFINED prgm")
    return name


def find_store(tokens: list[Token]) -> int | None:
    """Index of → outside strings, or None."""
    in_string = False
    for i, t in enumerate(tokens):
        if in_string:
            if t.bits == B_QUOTE:
                in_string = False
            continue
        if t.bits == B_QUOTE:
            in_string = True
            continue
        if t.bits == B_STORE:
            return i
    return None


def parse_store_target(tokens: list[Token]) -> tuple[str, str, list[Token] | None]:
    """Return (kind, name, index_tokens_or_None). kind is var|str|list|list_el."""
    if not tokens:
        raise SimError("ERR:SYNTAX")
    tok = _Tok(tokens)
    t = tok.peek()
    assert t is not None
    if t.bits in STR_TOKENS:
        name = STR_TOKENS[t.bits]
        tok.advance()
        if not tok.at_end():
            raise SimError("ERR:SYNTAX")
        return "str", name, None
    if t.bits in LIST_TOKENS:
        name = LIST_TOKENS[t.bits]
        tok.advance()
        if tok.match(B_LPAREN):
            idx_tokens = _rest_index(tok)
            return "list_el", name, idx_tokens
        if not tok.at_end():
            raise SimError("ERR:SYNTAX")
        return "list", name, None
    if t.bits == B_NAMED:
        tok.advance()
        name = parse_named_list(tok)
        if tok.match(B_LPAREN):
            idx_tokens = _rest_index(tok)
            return "list_el", name, idx_tokens
        if not tok.at_end():
            raise SimError("ERR:SYNTAX")
        return "list", name, None
    if t.bits == B_THETA or t.bits in LETTERS:
        name = "θ" if t.bits == B_THETA else t.text
        tok.advance()
        if not tok.at_end():
            raise SimError("ERR:SYNTAX")
        return "var", name, None
    raise SimError("ERR:SYNTAX")


def _rest_index(tok: _Tok) -> list[Token]:
    depth = 1
    out: list[Token] = []
    while not tok.at_end():
        t = tok.advance()
        if t.bits == B_LPAREN or t.text.endswith("("):
            depth += 1
            out.append(t)
            continue
        if t.bits == B_RPAREN:
            depth -= 1
            if depth == 0:
                if not tok.at_end():
                    raise SimError("ERR:SYNTAX")
                return out
            out.append(t)
            continue
        out.append(t)
    raise SimError("unclosed parenthesis")


def is_block_opener(stmt: Statement) -> bool:
    if not stmt.tokens:
        return False
    return stmt.tokens[0].bits in (B_THEN, B_FOR, B_REPEAT)


def statement_kind(stmt: Statement) -> str:
    if not stmt.tokens:
        return "empty"
    return stmt.tokens[0].bits.hex()
