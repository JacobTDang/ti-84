import cmath
import math

import pytest

from ti84.sim import Calculator, SimError


def ev(text, complex_mode=True, **state):
    calc = Calculator(complex_mode=complex_mode)
    for name, value in state.items():
        calc.vars[name] = value
    return calc.eval(text)


@pytest.mark.parametrize(
    "text, value",
    [
        ("1+2*3", 7.0),
        ("(1+2)*3", 9.0),
        ("2^3^2", 64.0),
        ("⁻2²", -4.0),
        ("⁻2^2", -4.0),
        ("2⁻¹", 0.5),
        ("2^⁻2", 0.25),
        ("2^⁻1*4", 2.0),
        ("10^(⁻3)", 0.001),
        ("3²", 9.0),
        ("10-4-3", 3.0),
        ("12/3/2", 2.0),
        ("1.5ᴇ3", 1500.0),
        ("2ᴇ⁻9", 2e-9),
        ("ᴇ3", 1000.0),
        (".5", 0.5),
        ("⁻.5*2", -1.0),
        ("2*pi", 2 * math.pi),
        ("𝑒", math.e),
        ("𝑒^(1)", math.e),
        ("ln(𝑒)", 1.0),
        ("log(1000)", 3.0),
        ("√(16)", 4.0),
        ("abs(⁻3)", 3.0),
        ("int(⁻1.5)", -2.0),
        ("int(2.7)", 2.0),
        ("round(2.345,2)", 2.35),
        ("round(⁻2.345,2)", -2.35),
        ("round(2.5,0)", 3.0),
        ("min(3,⁻1)", -1.0),
        ("max(3,⁻1)", 3.0),
        ("sin(pi/2)", 1.0),
        ("cos(0)", 1.0),
        ("tan⁻¹(1)", math.pi / 4),
        ("1<2", 1.0),
        ("2≤1", 0.0),
        ("3≠3", 0.0),
        ("1=1 and 0", 0.0),
        ("1=0 or 2", 1.0),
        ("not(0)", 1.0),
        ("not(5)", 0.0),
        ("1+2=3", 1.0),
    ],
)
def test_real_expressions(text, value):
    assert ev(text) == pytest.approx(value, rel=1e-12, abs=1e-15)


@pytest.mark.parametrize(
    "text, value",
    [
        ("3+4𝑖", 3 + 4j),
        ("𝑖*𝑖", -1.0),
        ("abs(3+4𝑖)", 5.0),
        ("√(⁻4)", 2j),
        ("ln(⁻1)", cmath.pi * 1j),
        ("angle(𝑖)", math.pi / 2),
        ("angle(⁻1)", math.pi),
        ("angle(0)", 0.0),
        ("real(3+4𝑖)", 3.0),
        ("imag(3+4𝑖)", 4.0),
        ("conj(3+4𝑖)", 3 - 4j),
        ("1/(1+𝑖)", 0.5 - 0.5j),
        ("⁻𝑖/(2*pi*1000*1ᴇ⁻6)", -1j / (2 * math.pi * 1000 * 1e-6)),
        ("(1+2𝑖)*(3-𝑖)", 5 + 5j),
        ("2.5𝑖", 2.5j),
    ],
)
def test_complex_expressions(text, value):
    got = ev(text)
    assert got == pytest.approx(value, rel=1e-12, abs=1e-15)


def test_complex_with_zero_imaginary_part_becomes_real():
    got = ev("(1+𝑖)*(1-𝑖)")
    assert got == 2.0
    assert isinstance(got, float)


def test_variables_and_ans():
    calc = Calculator(complex_mode=True)
    calc.vars["R"] = 1000.0
    calc.vars["θ"] = 2.0
    assert calc.eval("R*θ") == 2000.0
    calc.ans = 7.0
    assert calc.eval("Ans+1") == 8.0


def test_strings():
    calc = Calculator()
    calc.strings["Str9"] = "1.592k"
    assert calc.eval('"VOUT="+Str9+" V"') == "VOUT=1.592k V"
    assert calc.eval('length("Ω μ")') == 3.0
    assert calc.eval('sub("ABCDE",2,3)') == "BCD"
    assert calc.eval('"AB"="AB"') == 1.0
    assert calc.eval('"AB"≠"AB"') == 0.0


def test_lists():
    calc = Calculator(complex_mode=True)
    calc.lists["L₁"] = [1.0, 800.0, 1e6]
    assert calc.eval("dim(L₁)") == 3.0
    assert calc.eval("L₁(2)") == 800.0
    assert calc.eval("sum(L₁)") == 1000801.0
    assert calc.eval("{1,2,3}*2") == [2.0, 4.0, 6.0]
    assert calc.eval("{1,2}+{10,20}") == [11.0, 22.0]
    assert calc.eval("max({1,5,3})") == 5.0
    assert calc.eval("min({1,5,3})") == 1.0
    assert calc.eval("max(45={45,105})") == 1.0
    assert calc.eval("seq(K²,K,1,4)") == [1.0, 4.0, 9.0, 16.0]
    assert calc.eval("abs({⁻1,2})") == [1.0, 2.0]


def test_seq_restores_its_variable():
    calc = Calculator()
    calc.vars["K"] = 42.0
    calc.eval("seq(K,K,1,3)")
    assert calc.vars["K"] == 42.0


def test_named_lists():
    calc = Calculator()
    calc.lists["⌊ZF"] = [3.0, 4.0]
    assert calc.eval("⌊ZF(2)") == 4.0


@pytest.mark.parametrize(
    "text, error",
    [
        ("1/0", "ERR:DIVIDE BY 0"),
        ("0⁻¹", "ERR:DIVIDE BY 0"),
        ("ln(0)", "ERR:DOMAIN"),
        ("log(0)", "ERR:DOMAIN"),
        ("0^0", "ERR:DOMAIN"),
        ("{1,2}+{1,2,3}", "ERR:DIM MISMATCH"),
        ("L₁(4)", "ERR:INVALID DIM"),
        ('"A"+1', "ERR:DATA TYPE"),
        ("toString(1+𝑖)", "ERR:DATA TYPE"),
        ("2A", "implicit multiplication"),
        ("A(B)", "implicit multiplication"),
        ("(1)(2)", "implicit multiplication"),
        ("A𝑖", "implicit multiplication"),
        ("-5", "'-' starts an expression"),
        ("2*(-5)", "'-' starts an expression"),
        ("(1+2", "unclosed"),
        ('"ABC', "unclosed"),
        ("Disp 1", "unsupported token"),
    ],
)
def test_errors(text, error):
    calc = Calculator(complex_mode=True)
    calc.lists["L₁"] = [1.0, 2.0, 3.0]
    with pytest.raises(SimError, match=error):
        calc.eval(text)


def test_real_mode_rejects_complex_results():
    with pytest.raises(SimError, match="ERR:NONREAL"):
        ev("√(⁻4)", complex_mode=False)
    with pytest.raises(SimError, match="ERR:NONREAL"):
        ev("3+4𝑖", complex_mode=False)


@pytest.mark.parametrize(
    "value, text",
    [
        (0.0, "0"),
        (1.592, "1.592"),
        (1500.0, "1500"),
        (0.25, "0.25"),
        (0.001, "0.001"),
        (-5.0, "⁻5"),
        (2.0 / 3.0, "0.6666666667"),
        (123456789.0, "123456789"),
        (9999999999.4, "9999999999"),
        (1e10, "1ᴇ10"),
        (1e13, "1ᴇ13"),
        (2.5e-13, "2.5ᴇ⁻13"),
        (0.000999, "9.99ᴇ⁻4"),
        (-1.23456789012e15, "⁻1.23456789ᴇ15"),
        (1591.549430919, "1591.549431"),
    ],
)
def test_to_string_matches_normal_float_mode(value, text):
    calc = Calculator()
    calc.vars["X"] = value
    assert calc.eval("toString(X)") == text
