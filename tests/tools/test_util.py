import math

import pytest

from ti84.harness import run_tool

approx = pytest.approx


def test_todb():
    r = run_tool("todb", [10])
    assert r.value("DB (V)") == approx(20)
    assert r.value("DB (P)") == approx(10)


def test_todb_uses_the_size_of_a_negative_gain():
    r = run_tool("todb", [-100])
    assert r.value("DB (V)") == approx(40)


def test_fromdb():
    r = run_tool("fromdb", [-3])
    assert r.value("V RATIO") == approx(10 ** (-3 / 20))
    assert r.value("P RATIO") == approx(10 ** (-3 / 10))
    assert "V RATIO=707.9m V/V" in r.answers


def test_hzrad():
    r = run_tool("hzrad", [60])
    assert r.value("w") == approx(120 * math.pi)
    assert r.value("T") == approx(1 / 60)


def test_radhz():
    r = run_tool("radhz", [1000])
    assert r.value("F") == approx(1000 / (2 * math.pi))
    assert r.value("T") == approx(2 * math.pi / 1000)


def test_scope_lag_is_negative():
    r = run_tool("scope", [1000, -125e-6])
    assert r.value("PHASE") == approx(-45)
    assert "PHASE=-45 °" in r.answers


@pytest.mark.parametrize(
    "value, nearest, below, above",
    [
        (4500, 4700, 3900, 4700),
        (1234, 1200, 1200, 1500),
        (0.00007, 6.8e-5, 6.8e-5, 8.2e-5),
        (9500, 10000, 8200, 10000),
        (3300, 3300, 3300, 3300),
    ],
)
def test_e12(value, nearest, below, above):
    r = run_tool("e12", [value])
    assert r.value("NEAREST") == approx(nearest)
    assert r.value("BELOW") == approx(below)
    assert r.value("ABOVE") == approx(above)


def test_e12_guard():
    assert run_tool("e12", [0]).stopped == ["VALUE MUST BE > 0"]


def test_solve_course_three_op_amps():
    # M2 HW1 P2: vo1 + 0.5 vo2 + vo3 = -5, 2 vo1 + vo2 = 0, 2 vo2 + vo3 = 0
    r = run_tool("solve", [[1, 0.5, 1, -5, 2, 1, 0, 0, 0, 2, 1, 0]])
    assert r.calc.lists["L₂"] == [approx(-1.25), approx(2.5), approx(-5)]
    assert r.answers == ["SOLVE LINEAR EQUATIONS", "x1=-1.25", "x2=2.5", "x3=-5"]
    assert r.work == [
        "EQ1: 1*x1+500m*x2+1*x3=(-5)",
        "EQ2: 2*x1+1*x2+0*x3=0",
        "EQ3: 0*x1+2*x2+1*x3=0",
        "SOLVED BY ELIMINATION",
    ]


def test_solve_two_unknowns():
    r = run_tool("solve", [[1, 1, 3, 1, -1, 1]])
    assert r.calc.lists["L₂"] == [approx(2), approx(1)]


def test_solve_needs_a_row_swap():
    r = run_tool("solve", [[0, 1, 2, 1, 1, 3]])
    assert r.calc.lists["L₂"] == [approx(1), approx(2)]


def test_solve_four_unknowns():
    rows = [2, 1, 0, 0, 0, 1, 3, 1, 0, -2, 0, 1, 4, 1, 10.5, 0, 0, 1, 5, 5.5]
    r = run_tool("solve", [rows])
    assert r.calc.lists["L₂"] == [approx(1), approx(-2), approx(3), approx(0.5)]


def test_solve_complex_coefficients():
    r = run_tool("solve", [["1", "𝑖", "1+𝑖", "1", "⁻𝑖", "1-𝑖"]])
    assert r.calc.lists["L₂"] == [approx(1), approx(1)]


def test_solve_guards():
    assert run_tool("solve", [[1, 2, 3, 4]]).stopped == ["NEED N*(N+1) NUMBERS", "FOR N EQUATIONS, N=2-4"]
    assert run_tool("solve", [[1, 1, 2, 2, 2, 4]]).stopped == ["NO UNIQUE SOLUTION"]


def test_solve_nearly_singular_is_reported_not_solved():
    assert run_tool("solve", [[1, 1, 2, 1, 1.0000000001, 2]]).stopped == ["NO UNIQUE SOLUTION"]


def test_solve_small_but_valid_conductances():
    # Node equations with 1/R terms around 1e-4 still solve.
    r = run_tool("solve", [[3e-4, -1e-4, 1e-3, -1e-4, 2e-4, 0]])
    assert r.calc.lists["L₂"] == [approx(4), approx(2)]
