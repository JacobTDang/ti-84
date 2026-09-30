import pytest

from ti84.tokens import (
    DIALECT,
    LintError,
    Token,
    TokenError,
    decode,
    encode,
    lint,
    read_8xp,
    write_8xp,
)


@pytest.mark.parametrize(
    "text, hexbytes",
    [
        ("1.5ᴇ3", "313A353B33"),
        ("𝑖", "2C"),
        ("pi", "AC"),
        ("𝑒", "BB31"),
        ("⁻5", "B035"),
        ("A→B", "410442"),
        ("toString(A)", "EF974111"),
        ("Str0", "AA09"),
        ("L₁", "5D00"),
        ("⌊ZF", "EB5A46"),
        ("a+b𝑖", "BB4F"),
        ('"Ω μ ° ∠ ²"', "2ABBAC29BBA6290B29BBDC290D2A"),
    ],
)
def test_encode_uses_the_canonical_spellings(text, hexbytes):
    assert encode(text).hex().upper() == hexbytes


def test_encode_rejects_text_tivars_cannot_tokenize():
    with pytest.raises(TokenError, match="position 0"):
        encode("π")


def test_decode_gives_bits_and_display_text():
    assert decode(bytes.fromhex("DE2A48492A")) == [
        Token(b"\xde", "Disp "),
        Token(b"\x2a", '"'),
        Token(b"\x48", "H"),
        Token(b"\x49", "I"),
        Token(b"\x2a", '"'),
    ]


def test_dialect_covers_the_table_in_docs():
    for bits, text in [
        (b"\xe1", "ClrHome"),
        (b"\xe0", "Output("),
        (b"\xef\x97", "toString("),
        (b"\xbb\x28", "angle("),
        (b"\xb0", "⁻"),
        (b"\x71", "-"),
        (b"\x5b", "θ"),
        (b"\xaa\x09", "Str0"),
        (b"\x5d\x05", "L₆"),
        (b"\xac", "π"),
    ]:
        assert DIALECT[bits] == text
    assert all(bytes([c]) in DIALECT for c in range(0x41, 0x5B))
    assert all(bytes([c]) in DIALECT for c in range(0x30, 0x3A))


def test_lint_accepts_clean_code():
    lint(
        'ClrHome\nInput "R1 Ω=",R\n⁻R*2ᴇ⁻3→A\n"VOUT="+Str9+" V"→Str0\nprgmZP\n'
        "If A<0\nGoto M\n√(⁻4)+𝑖*pi→Z\n{1,2}→⌊ZF\n",
        "T",
    )


@pytest.mark.parametrize(
    "code, message",
    [
        ("1.5E3→A", "ASCII E after a number"),
        ("3+4i→Z", "lowercase letter 'i' outside a string"),
        ("e^(2)→A", "lowercase letter 'e' outside a string"),
        ("-5→A", "'-' starts an expression"),
        ("A*(-5)→A", "'-' starts an expression"),
        ("2^-1→A", "'-' starts an expression"),
        ("Disp A", "token 'Disp ' is not in the dialect"),
        ('"PI SAYS \'HI\'"→Str1', "does not round-trip in a string"),
    ],
)
def test_lint_rejects(code, message):
    with pytest.raises(LintError, match=message):
        lint(code, "T")


def test_lint_names_program_and_line_and_reports_every_problem():
    with pytest.raises(LintError) as err:
        lint("ClrHome\n-5→A\n1E3→B\n", "EEFILT")
    text = str(err.value)
    assert "EEFILT:2: '-' starts an expression" in text
    assert "EEFILT:3: ASCII E after a number" in text


def test_lint_allows_subtraction_between_values():
    lint("A-B→C\n(A)-2→C\nL₁(2)-1→C\nA²-B→C\n", "T")


def test_lint_allows_lowercase_inside_strings():
    lint('"fc=1.592kHz"→Str1\n', "T")


def test_write_and_read_8xp_round_trip(tmp_path):
    path = tmp_path / "VDIV.8xp"
    write_8xp("VDIV", 'ClrHome\nOutput(1,1,"HI")\n', path)
    name, data = read_8xp(path)
    assert name == "VDIV"
    assert data == encode('ClrHome\nOutput(1,1,"HI")\n')


@pytest.mark.parametrize("name", ["", "vdiv", "TOOLONGNAME", "1ABC", "A-B"])
def test_write_8xp_rejects_bad_program_names(tmp_path, name):
    with pytest.raises(TokenError, match="program name"):
        write_8xp(name, "ClrHome", tmp_path / "X.8xp")
