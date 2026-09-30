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
    assert run_tool("pfrac", [[1], [-1, -1, -1]]).stopped == ["REPEATED POLES:", "ONLY ONE DOUBLE POLE"]
    assert run_tool("pfrac", [[1], [-1, -1, -2, -2]]).stopped == ["REPEATED POLES:", "ONLY ONE DOUBLE POLE"]


def in_order(lines, expected):
    """Every expected line appears in `lines`, in this order."""
    position = 0
    for line in expected:
        assert line in lines[position:], f"{line!r} missing after line {position}: {lines}"
        position = lines.index(line, position) + 1


def test_pfrac_double_pole():
    # (s+3)/((s+1)²(s+2)) = -1/(s+1) + 2/(s+1)² + 1/(s+2)
    r = run_tool("pfrac", [[1, 3], [-1, -1, -2]])
    assert r.calc.lists["L₃"] == [approx(-1), approx(2), approx(1)]
    assert r.answers == ["PARTIAL FRACTIONS", "K1=-1 OVER (s-p)", "K2=2 OVER (s-p)²", "K3=1"]
    assert r.work == [
        "DOUBLE POLE AT s=(-1)",
        "K2 OVER (s-p)²=N(p)/REST(p)",
        "=2/1",
        "=2",
        "K1 OVER (s-p)=(dN/ds-K2*dREST/ds)/REST",
        "=-1",
        "TERM: 2*t*e^((-1)t)+(-1)*e^((-1)t)",
        "K3 AT s=(-2)",
        "=1/((-1)*(-1))",
        "=1",
        "TERM: 1*e^((-2)t)",
    ]


def test_pfrac_double_pole_alone():
    r = run_tool("pfrac", [[1], [-1, -1]])
    assert r.calc.lists["L₃"] == [approx(0), approx(1)]


def test_pfrac_double_pole_not_next_to_each_other():
    r = run_tool("pfrac", [[1, 3], [-1, -2, -1]])
    assert r.calc.lists["L₃"] == [approx(-1), approx(1), approx(2)]
    assert r.answers == ["PARTIAL FRACTIONS", "K1=-1 OVER (s-p)", "K2=1", "K3=2 OVER (s-p)²"]


def test_pfrac_critically_damped_step():
    # 1/(s(s+1)²) = 1/s - 1/(s+1) - 1/(s+1)²
    r = run_tool("pfrac", [[1], [0, -1, -1]])
    assert r.calc.lists["L₃"] == [approx(1), approx(-1), approx(-1)]


def test_hdiv_course_homework_1_problem_1():
    # L in series, then R parallel C to ground: H = (1/LC)/(s² + s/RC + 1/LC)
    r = run_tool("hdiv", [1, 0, 0.01, 0, 2, 1000, 0, 1e-6])
    assert r.calc.lists["L₁"] == [approx(1e8)]
    assert r.calc.lists["L₂"] == [approx(1), approx(1000), approx(1e8)]
    assert r.answers == [
        "H(s) OF A Z DIVIDER",
        "N(s)=100M",
        "D(s)=1*s²+1k*s+100M",
        "DC GAIN=1",
        "w0=10k rad/s",
        "Q=10",
        "p1=-500+j9.987k",
        "p2=-500-j9.987k",
    ]
    in_order(r.work, [
        "Z1=(10m*s)/(1)",
        "Z2=(1)/(1μ*s+1m)",
        "H=Z2/(Z1+Z2)",
        "=(1)/(10n*s²+10μ*s+1)",
        "DIVIDE TOP AND BOTTOM BY 10n",
        "N(s)=100M",
        "D(s)=1*s²+1k*s+100M",
        "SAVED: L1=TOP, L2=BOTTOM",
    ])


def test_hdiv_rc_low_pass_is_first_order():
    r = run_tool("hdiv", [1, 1000, 0, 0, 1, 0, 0, 1e-6])
    assert r.calc.lists["L₁"] == [approx(1000)]
    assert r.calc.lists["L₂"] == [approx(1), approx(1000)]
    assert r.answers == ["H(s) OF A Z DIVIDER", "N(s)=1k", "D(s)=1*s+1k", "DC GAIN=1", "POLE=-1k"]


def test_hdiv_guards():
    assert run_tool("hdiv", [3, 1000, 0, 0, 1, 1000, 0, 0]).stopped == ["TYPE MUST BE 1 OR 2"]
    assert run_tool("hdiv", [1, 0, 0, 0, 1, 1000, 0, 0]).stopped == ["Z1 HAS NO PARTS"]
    assert run_tool("hdiv", [1, 1000, 0, 0, 2, 0, 0, 0]).stopped == ["Z2 HAS NO PARTS"]


def test_hopamp_course_homework_1_problem_5():
    # R1 + sL in, R2 parallel C feedback: H = -2e9/(s² + 3e4 s + 2e8)
    r = run_tool("hopamp", [1, 1, 1000, 0.05, 0, 2, 10000, 0, 1e-8])
    assert r.calc.lists["L₁"] == [approx(-2e9)]
    assert r.calc.lists["L₂"] == [approx(1), approx(3e4), approx(2e8)]
    assert r.answers == [
        "H(s) OF AN OP AMP STAGE",
        "N(s)=(-2G)",
        "D(s)=1*s²+30k*s+200M",
        "DC GAIN=-10",
        "w0=14.14k rad/s",
        "Q=471.4m",
        "p1=-10k",
        "p2=-20k",
    ]
    in_order(r.work, [
        "ZIN=(50m*s+1k)/(1)",
        "ZF=(1)/(10n*s+100μ)",
        "H=-ZF/ZIN",
        "=((-1))/(500p*s²+15μ*s+100m)",
        "DIVIDE TOP AND BOTTOM BY 500p",
        "SAVED: L1=TOP, L2=BOTTOM",
    ])


def test_hopamp_non_inverting():
    r = run_tool("hopamp", [2, 1, 1000, 0, 0, 2, 9000, 0, 1e-8])
    assert r.calc.lists["L₁"] == [approx(1), approx(1e5 / 0.9)]
    assert r.calc.lists["L₂"] == [approx(1), approx(1e4 / 0.9)]
    assert r.answers == [
        "H(s) OF AN OP AMP STAGE",
        "N(s)=1*s+111.1k",
        "D(s)=1*s+11.11k",
        "DC GAIN=10",
        "POLE=-11.11k",
    ]
    assert "H=1+ZF/ZIN" in r.work


def test_hopamp_guard():
    assert run_tool("hopamp", [3, 1, 1000, 0, 0, 1, 1000, 0, 0]).stopped == ["AMP MUST BE 1 OR 2"]


def test_ends_course_homework_1_problem_5():
    # A -0.5 V step into -2e9/(s² + 3e4 s + 2e8) settles at 5 V, starting from 0.
    r = run_tool("ends", [[-2e9], [1, 3e4, 2e8], -0.5])
    assert r.value("y(INF)") == approx(5)
    assert r.value("y(0+)") == approx(0)
    assert r.answers == ["STEP START AND END VALUES", "y(0+)=0", "y(INF)=5"]


def test_ends_high_pass_starts_at_the_step():
    r = run_tool("ends", [[1, 0], [1, 10], 2])
    assert r.value("y(0+)") == approx(2)
    assert r.value("y(INF)") == approx(0)


def test_ends_guards():
    assert run_tool("ends", [[1], [1, 0], 1]).stopped == ["POLE AT s=0:", "NO FINAL VALUE"]
    assert run_tool("ends", [[1, 2, 3], [1, 2], 1]).stopped == ["IMPROPER H(s)"]


def test_bode_lines():
    # 10(1+s/100)/((1+s/10)(1+s/1000))
    r = run_tool("bode", [10, 0, [100], [10, 1000]])
    assert r.answers == [
        "STRAIGHT-LINE BODE PLOT",
        "LOW F SLOPE=0 dB/DEC",
        "20*LOG|K0|=20 dB",
        "w=10: 20 dB, THEN -20",
        "w=100: 0 dB, THEN 0",
        "w=1k: 0 dB, THEN -20",
    ]
    assert r.work == [
        "LOW F: 20*LOG|K0|+SLOPE*LOG(w)",
        "20*LOG|K0|=20 dB, SLOPE 0",
        "w=10: SLOPE CHANGE -20",
        "=20+(0)*LOG(10)",
        "=20 dB, SLOPE NOW -20",
        "w=100: SLOPE CHANGE 20",
        "=20+(-20)*LOG(100/10)",
        "=0 dB, SLOPE NOW 0",
        "w=1k: SLOPE CHANGE -20",
        "=0+(0)*LOG(1k/100)",
        "=0 dB, SLOPE NOW -20",
    ]


def test_bode_with_a_pole_at_the_origin():
    # 1000/(s(1+s/100))
    r = run_tool("bode", [1000, 1, [0], [100]])
    assert r.answers == [
        "STRAIGHT-LINE BODE PLOT",
        "LOW F SLOPE=-20 dB/DEC",
        "20*LOG|K0|=60 dB",
        "w=100: 20 dB, THEN -40",
    ]
    assert r.work[-3:] == ["w=100: SLOPE CHANGE -20", "=60+(-20)*LOG(100)", "=20 dB, SLOPE NOW -40"]


def test_bode_merges_a_double_pole_and_uses_the_size_of_k():
    r = run_tool("bode", [-10, 0, [0], [10, 10]])
    assert r.answers == ["STRAIGHT-LINE BODE PLOT", "LOW F SLOPE=0 dB/DEC", "20*LOG|K0|=20 dB", "w=10: 20 dB, THEN -40"]


def test_bode_with_no_corners():
    r = run_tool("bode", [1, 0, [0], [0]])
    assert r.answers == ["STRAIGHT-LINE BODE PLOT", "LOW F SLOPE=0 dB/DEC", "20*LOG|K0|=0 dB"]


def test_bode_guards():
    assert run_tool("bode", [0, 0, [0], [10]]).stopped == ["K0 CANNOT BE 0"]
    assert run_tool("bode", [1, 0, [0], [-5]]).stopped == ["CORNERS MUST BE > 0"]
