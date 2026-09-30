from pathlib import Path

import pytest

import ti84
from ti84.sim import Calculator, Clear, Key, Out, Wait
from ti84.tokens import lint

HELPERS = ("ZF", "ZR", "ZC", "ZS", "ZP", "ZE")
HELPER_DIR = Path(ti84.__file__).parent / "helpers"


def helper_text(name):
    path = HELPER_DIR / f"{name}.basic"
    if not path.exists():
        pytest.fail(f"no helper file {path.name}")
    return path.read_text(encoding="utf-8")


def calculator():
    calc = Calculator(complex_mode=True)
    for name in HELPERS:
        calc.load_text(name, helper_text(name))
    return calc


def call(helper, value):
    calc = calculator()
    calc.vars["X"] = value
    calc.load_text("T", f"X\nprgm{helper}\n")
    calc.run("T")
    return calc.strings["Str9"]


@pytest.mark.parametrize("name", HELPERS)
def test_helper_lints_clean(name):
    lint(helper_text(name), name)


@pytest.mark.parametrize(
    "value, text",
    [
        (0.0, "0"),
        (1591.549431, "1.592k"),
        (6.6666667, "6.667"),
        (-90.8265, "-90.83"),
        (1e-6, "1μ"),
        (2.2e-9, "2.2n"),
        (999.96, "1k"),
        (999960.0, "1M"),
        (0.001, "1m"),
        (12.5, "12.5"),
        (4.7e9, "4.7G"),
        (3.3e-12, "3.3p"),
        (1.0, "1"),
        (100.0, "100"),
        (0.12346, "123.5m"),
        (-0.0025, "-2.5m"),
        (159.1549, "159.2"),
        (8660.254, "8.66k"),
        (1e13, "1ᴇ13"),
        (2.5e-13, "2.5ᴇ⁻13"),
    ],
)
def test_zf_formats_four_significant_figures_with_si_prefix(value, text):
    assert call("ZF", value) == text


@pytest.mark.parametrize(
    "value, text",
    [
        (-51.4893, "-51.49"),
        (3.0, "3"),
        (-0.004, "0"),
        (0.5, "0.5"),
        (-45.0, "-45"),
        (-3.0103, "-3.01"),
        (123.456, "123.46"),
    ],
)
def test_zr_rounds_to_two_decimals(value, text):
    assert call("ZR", value) == text


@pytest.mark.parametrize(
    "value, text",
    [
        (1000 - 159.15j, "1k-j159.2"),
        (3 + 4j, "3+j4"),
        (5.0, "5"),
        (-2j, "-j2"),
        (0.0, "0"),
        (-5000 + 8660.254j, "-5k+j8.66k"),
    ],
)
def test_zc_formats_rectangular_complex(value, text):
    assert call("ZC", value) == text


@pytest.mark.parametrize(
    "value, text",
    [
        (5.0, "5"),
        (-5.0, "(-5)"),
        (1591.549431, "1.592k"),
        (3 + 4j, "(3+j4)"),
        (-2j, "(-j2)"),
        (0.0, "0"),
    ],
)
def test_zs_formats_a_value_for_the_numbers_line(value, text):
    assert call("ZS", value) == text


SENTINEL_VARS = {letter: 7.0 for letter in "ABCDEFGHIJKLMNOPQRSTUVWYZ"}


@pytest.mark.parametrize("name", ["ZF", "ZR", "ZC", "ZS"])
def test_formatters_leave_student_variables_and_str0_alone(name):
    calc = calculator()
    calc.vars.update(SENTINEL_VARS)
    calc.vars["X"] = -1234.5 + 6.5j if name in ("ZC", "ZS") else -1234.5
    for k in range(1, 8):
        calc.strings[f"Str{k}"] = f"S{k}"
    calc.strings["Str0"] = "LINE"
    calc.lists["L₁"] = [1.0, 2.0]
    calc.load_text("T", f"X\nprgm{name}\n")
    calc.run("T")
    assert {k: calc.vars[k] for k in SENTINEL_VARS} == SENTINEL_VARS
    assert [calc.strings[f"Str{k}"] for k in range(1, 8)] == [f"S{k}" for k in range(1, 8)]
    assert calc.strings["Str0"] == "LINE"
    assert calc.lists["L₁"] == [1.0, 2.0]


def paged(theta, line, events=()):
    calc = calculator()
    calc.vars["θ"] = theta
    calc.strings["Str0"] = line
    calc.load_text("T", "prgmZP\n")
    run = calc.run("T", list(events))
    return calc, run


def test_zp_prints_a_line_and_moves_down():
    calc, run = paged(1, "HELLO")
    assert run.log == [Out(1, 1, "HELLO")]
    assert calc.vars["θ"] == 2.0


def test_zp_counts_wrapped_rows():
    calc, run = paged(1, "X" * 30)
    assert calc.vars["θ"] == 3.0


def test_zp_uses_row_nine():
    calc, run = paged(9, "LAST")
    assert run.log == [Out(9, 1, "LAST")]
    assert calc.vars["θ"] == 10.0


def test_zp_pages_when_the_screen_is_full():
    calc, run = paged(10, "NEXT", [Key("ENTER")])
    assert run.log[0] == Out(10, 1, "ENTER:MORE  CLEAR:QUIT")
    assert isinstance(run.log[1], Wait) and run.log[1].key == "ENTER"
    assert run.log[2:] == [Clear(), Out(1, 1, "NEXT")]
    assert calc.vars["θ"] == 2.0


def test_zp_pages_when_a_wrapped_line_would_pass_row_nine():
    calc, run = paged(9, "Y" * 30, [Key("ENTER")])
    assert run.log[-1] == Out(1, 1, "Y" * 30)
    assert calc.vars["θ"] == 3.0


def test_zp_clear_quits():
    calc, run = paged(10, "NEXT", [Key("CLEAR")])
    assert run.log[0] == Out(10, 1, "ENTER:MORE  CLEAR:QUIT")
    assert not any(isinstance(e, Clear) for e in run.log)
    assert Out(1, 1, "NEXT") not in run.log
    assert calc.vars["θ"] == 0.0


def test_zp_does_nothing_after_quit():
    calc, run = paged(0, "IGNORED")
    assert run.log == []
    assert calc.vars["θ"] == 0.0


def ended(theta, footer, events=()):
    calc = calculator()
    calc.vars["θ"] = theta
    calc.strings["Str0"] = footer
    calc.load_text("T", "prgmZE\n")
    run = calc.run("T", list(events))
    return calc, run


def test_ze_enter_clears_and_starts_a_new_page():
    calc, run = ended(4, "ENTER:WORK  CLEAR:QUIT", [Key("ENTER")])
    assert run.log[0] == Out(10, 1, "ENTER:WORK  CLEAR:QUIT")
    assert isinstance(run.log[1], Wait)
    assert run.log[2:] == [Clear()]
    assert calc.vars["θ"] == 1.0


def test_ze_clear_quits():
    calc, run = ended(4, "ENTER:WORK  CLEAR:QUIT", [Key("CLEAR")])
    assert not any(isinstance(e, Clear) for e in run.log)
    assert calc.vars["θ"] == 0.0


def test_ze_does_nothing_after_quit():
    calc, run = ended(0, "DONE  ENTER:MENU")
    assert run.log == []
    assert calc.vars["θ"] == 0.0


@pytest.mark.parametrize("helper, value, text", [("ZF", 3 + 4j, "3+j4"), ("ZR", -2j, "-j2")])
def test_real_formatters_hand_complex_values_to_zc(helper, value, text):
    assert call(helper, value) == text
