import cmath
import math

import pytest

from ti84.harness import run_tool

approx = pytest.approx

# M3_L3 example: H(s) = 1e6 / (s² + 800s + 1e6), so w0 = 1000 rad/s and Q = 1.25.
F0 = 1000 / (2 * math.pi)


def test_taurc():
    r = run_tool("taurc", [1000, 1e-6])
    assert r.value("TAU") == approx(1e-3)
    assert r.value("5TAU") == approx(5e-3)
    assert r.value("wc") == approx(1000)
    assert r.value("fc") == approx(F0)
    assert r.answers == ["RC TIME CONSTANT", "TAU=1m s", "5TAU=5m s", "wc=1k rad/s", "fc=159.2 Hz"]


def test_taurl():
    r = run_tool("taurl", [0.01, 100])
    assert r.value("TAU") == approx(1e-4)


def test_step1_one_time_constant_is_63_percent():
    r = run_tool("step1", [0, 5, 1e-3, 1e-3])
    assert r.value("v(t)") == approx(5 * (1 - math.exp(-1)))
    assert r.work == [
        "v(t)=VINF+(V0-VINF)*e^(-t/TAU)",
        "=5+(0-5)*e^(-1m/1m)",
        "=3.161",
    ]


def test_treach():
    r = run_tool("treach", [0, 5, 1e-3, 2.5])
    assert r.value("t") == approx(1e-3 * math.log(2))


def test_treach_guard_when_the_target_is_never_reached():
    r = run_tool("treach", [0, 5, 1e-3, 6])
    assert r.stopped == ["TARGET NOT BETWEEN", "V(0) AND V(INF)"]
    assert r.answers == []


def test_srlc_underdamped():
    r = run_tool("srlc", [100, 0.01, 1e-6])
    assert r.value("a") == approx(5000)
    assert r.value("w0") == approx(10000)
    assert r.value("ZETA") == approx(0.5)
    assert r.value("Q") == approx(1)
    assert r.value("p1") == approx(complex(-5000, math.sqrt(1e8 - 25e6)))
    assert r.value("p2") == approx(complex(-5000, -math.sqrt(1e8 - 25e6)))
    assert r.value("TYPE") == "UNDERDAMPED: RINGS"
    assert "p1=-5k+j8.66k 1/s" in r.answers


def test_srlc_overdamped():
    r = run_tool("srlc", [1000, 0.01, 1e-6])
    assert r.value("TYPE") == "OVERDAMPED: 2 REAL POLES"
    assert r.value("p1") == approx(-50000 + math.sqrt(50000**2 - 1e8))
    assert r.value("p2") == approx(-50000 - math.sqrt(50000**2 - 1e8))


def test_srlc_critical():
    r = run_tool("srlc", [2, 1, 1])
    assert r.value("TYPE") == "CRITICAL: REPEATED POLE"


def test_prlc():
    r = run_tool("prlc", [1000, 0.01, 1e-6])
    assert r.value("a") == approx(500)
    assert r.value("w0") == approx(10000)
    assert r.value("TYPE") == "UNDERDAMPED: RINGS"


def test_quad_course_example():
    r = run_tool("quad", [1, 800, 1e6])
    assert r.value("w0") == approx(1000)
    assert r.value("Q") == approx(1.25)
    assert r.value("ZETA") == approx(0.4)
    p1 = (-800 + cmath.sqrt(800**2 - 4e6)) / 2
    assert r.value("p1") == approx(p1)
    assert r.value("p2") == approx(p1.conjugate())
    assert r.value("POLES") == "Q>0.5: COMPLEX PAIR"
    assert r.value("PEAK") == "Q>0.707: PEAKS"


def test_quad_real_poles():
    r = run_tool("quad", [1, 3, 2])
    assert r.value("p1") == approx(-1)
    assert r.value("p2") == approx(-2)
    assert r.value("POLES") == "Q<0.5: 2 REAL POLES"
    assert r.value("PEAK") == "NO PEAK"


def test_hjw_at_w0_is_q_times_g0_and_minus_90():
    r = run_tool("hjw", [[1e6], [1, 800, 1e6], F0])
    assert r.value("H") == approx(-1.25j)
    assert r.value("|H|") == approx(1.25)
    assert r.value("DB") == approx(20 * math.log10(1.25))
    assert r.value("∠H") == approx(-90)
    assert r.answers == ["EVALUATE H(s) AT s=jw", "|H|=1.25 V/V", "DB=1.94 dB", "∠H=-90 °"]


def test_hjw_dc_gain():
    r = run_tool("hjw", [[2, 4], [1, 3, 2], 0])
    assert r.value("H") == approx(2)
    assert r.value("∠H") == approx(0)


def test_sine_steady_state():
    r = run_tool("sine", [[1e6], [1, 800, 1e6], 2, 30, F0])
    assert r.value("OUT AMP") == approx(2.5)
    assert r.value("OUT PHASE") == approx(-60)


def test_pfrac_real_poles():
    r = run_tool("pfrac", [[10], [0, -2, -5]])
    assert r.calc.lists["L₃"] == [approx(1), approx(-5 / 3), approx(2 / 3)]
    assert r.answers == ["PARTIAL FRACTIONS", "K1=1", "K2=-1.667", "K3=666.7m"]
    assert r.work == [
        "K1 AT s=0",
        "=10/(2*5)",
        "=1",
        "TERM: 1*e^(0t)",
        "K2 AT s=(-2)",
        "=10/((-2)*3)",
        "=-1.667",
        "TERM: (-1.667)*e^((-2)t)",
        "K3 AT s=(-5)",
        "=10/((-5)*(-3))",
        "=666.7m",
        "TERM: 666.7m*e^((-5)t)",
    ]


def test_pfrac_complex_pair():
    r = run_tool("pfrac", [[1], ["⁻1+2𝑖", "⁻1-2𝑖"]])
    assert r.calc.lists["L₃"] == [approx(-0.25j), approx(0.25j)]
    assert r.work == [
        "K1 AT s=(-1+j2)",
        "=1/((j4))",
        "=-j250m",
        "PAIR: 2|K|*e^(at)*COS(bt+∠K)",
        "=500m*e^((-1)t)*COS(2t-90°)",
        "K2 AT s=(-1-j2)",
        "=1/((-j4))",
        "=j250m",
        "(CONJUGATE OF PAIR ABOVE)",
    ]


def test_pfrac_guards():
    assert run_tool("pfrac", [[1, 2, 3], [-1, -2]]).stopped == ["IMPROPER: DEG N ≥ DEG D", "DIVIDE FIRST"]
    assert run_tool("pfrac", [[1], [-1, -1]]).stopped == ["REPEATED POLE:", "NOT HANDLED HERE"]
