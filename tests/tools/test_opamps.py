import math

import pytest

from ti84.harness import run_tool

approx = pytest.approx


def test_inv_inside_the_rails():
    r = run_tool("inv", [0.1, 1000, 10000, 10, -10])
    assert r.value("GAIN") == approx(-10)
    assert r.value("VOUT") == approx(-1)
    assert r.value("VOMAX") == approx(8)
    assert r.value("VOMIN") == approx(-8)
    assert r.value("|VIN|MAX") == approx(0.8)
    assert r.value("RAILS") == "OK: INSIDE RAILS"
    assert r.work[:3] == ["GAIN=-R2/R1", "=-10k/1k", "=-10 V/V"]


def test_inv_clips():
    r = run_tool("inv", [1, 1000, 10000, 10, -10])
    assert r.value("VOUT") == approx(-10)
    assert r.value("RAILS") == "CLIPS: PAST RAILS-2V"


def test_noninv():
    r = run_tool("noninv", [1, 1000, 4000, 12, -12])
    assert r.value("GAIN") == approx(5)
    assert r.value("VOUT") == approx(5)
    assert r.value("RAILS") == "OK: INSIDE RAILS"
    assert "VCM = VIN: CHECK INPUT RANGE" in r.work


def test_sum3_with_an_unused_input():
    r = run_tool("sum3", [1, 10000, 2, 20000, 0, 1, 10000])
    assert r.value("VOUT") == approx(-2)


def test_diff_matched_resistors():
    r = run_tool("diff", [1, 3, 10000, 20000, 10000, 20000])
    assert r.value("V+") == approx(2)
    assert r.value("VOUT") == approx(4)


def test_diff_unmatched_resistors():
    va, vb, ra, rb, rc, rd = 1, 3, 10000, 20000, 5000, 15000
    r = run_tool("diff", [va, vb, ra, rb, rc, rd])
    vp = vb * rd / (rc + rd)
    assert r.value("VOUT") == approx(vp * (1 + rb / ra) - va * rb / ra)


def test_iout():
    r = run_tool("iout", [5, 1000, 10000, 0])
    assert r.value("IL") == approx(5e-3)
    assert r.value("IF") == approx(0.5e-3)
    assert r.value("IO") == approx(5.5e-3)


def test_offset_and_bias():
    r = run_tool("offset", [2e-3, 100e-9, 10e-9, 1000, 100000])
    assert r.value("NOISE GAIN") == approx(101)
    assert r.value("VO(VOS)") == approx(0.202)
    assert r.value("VO(IB), NO R3") == approx(0.01)
    assert r.value("R3") == approx(1000 * 100000 / 101000)
    assert r.value("VO(IOS), WITH R3") == approx(1e-3)
    assert r.value("WORST, WITH R3") == approx(0.203)
    assert r.value("WORST, NO R3") == approx(0.212)


def test_offset_uses_the_size_of_a_negative_vos():
    r = run_tool("offset", [-2e-3, 100e-9, 10e-9, 1000, 100000])
    assert r.value("VO(VOS)") == approx(0.202)


def test_finite_gain_course_example():
    r = run_tool("finite", [1000, 100000, 1000])
    assert r.value("INV IDEAL") == approx(-100)
    assert r.value("INV REAL") == approx(-100 / (1 + 101 / 1000))
    assert r.value("NONINV REAL") == approx(101 / (1 + 101 / 1000))
    assert r.value("ERROR") == approx(100 * (1 - 1 / (1 + 101 / 1000)))
    assert "INV REAL=-90.83 V/V" in r.answers


def test_finite_gain_large_aol():
    r = run_tool("finite", [1000, 100000, 1e5])
    assert r.value("INV REAL") == approx(-99.9, abs=0.01)


def test_gbw_lm324():
    r = run_tool("gbw", [1.2e6, 1000, 9000, 10000])
    assert r.value("NOISE GAIN") == approx(10)
    assert r.value("FC") == approx(120000)
    assert r.value("AMAX AT F") == approx(120)


def test_slew_ok():
    r = run_tool("slew", [0.5, 5, 10000])
    assert r.value("SR") == approx(5e5)
    assert r.value("NEEDED") == approx(2 * math.pi * 1e4 * 5)
    assert r.value("FMAX") == approx(5e5 / (2 * math.pi * 5))
    assert r.value("VMMAX") == approx(5e5 / (2 * math.pi * 1e4))
    assert r.value("SLEW") == "OK: NO SLEW LIMIT"


def test_slew_limited():
    r = run_tool("slew", [0.5, 5, 20000])
    assert r.value("SLEW") == "SLEW LIMITED: DISTORTS"


def test_limits_datasheet_values_clip():
    # LM324 at ±10 V: +8.74 V / -9.27 V
    r = run_tool("limits", [-10, 1, 8.74, -9.27])
    assert r.value("IDEAL VOUT") == approx(-10)
    assert r.value("ACTUAL VOUT") == approx(-9.27)
    assert r.value("VIN AT VO MAX") == approx(-0.874)
    assert r.value("VIN AT VO MIN") == approx(0.927)
    assert r.value("CLIPS") == "YES: OUTPUT CLIPS"


def test_limits_inside():
    r = run_tool("limits", [-10, 0.5, 8.74, -9.27])
    assert r.value("ACTUAL VOUT") == approx(-5)
    assert r.value("CLIPS") == "NO: INSIDE LIMITS"


def test_vosm_course_homework_2_problem_1():
    r = run_tool("vosm", [-0.08, 2000, 20000])
    assert r.value("NOISE GAIN") == approx(11)
    assert r.value("VOS") == approx(-0.08 / 11)
    assert "VOS=-7.273m V" in r.answers


def test_ibcap_course_homework_2_problem_2():
    r = run_tool("ibcap", [-20e-9, -18e-9, 1e-6, 1000, 10000, 10, 6.5, -6.5])
    assert r.value("dVP/dt") == approx(0.02)
    assert r.value("GAIN") == approx(11)
    assert r.value("VO(t)") == approx(2.2)
    assert r.value("LIMIT") == approx(6.5)
    assert r.value("tSAT") == approx(6.5 / 0.22)
    assert r.value("IB") == approx(-19e-9)
    assert r.value("IOS") == approx(-2e-9)
    assert r.answers == ["BIAS CURRENT INTO A CAP", "VO(t)=2.2 V", "tSAT=29.55 s", "IB=-19n A", "IOS=-2n A"]


def test_ibcap_current_into_the_pin_ramps_down():
    r = run_tool("ibcap", [20e-9, 18e-9, 1e-6, 1000, 10000, 10, 6.5, -6.5])
    assert r.value("VO(t)") == approx(-2.2)
    assert r.value("LIMIT") == approx(-6.5)
    assert r.value("tSAT") == approx(6.5 / 0.22)


def test_ibcap_guard():
    assert run_tool("ibcap", [0, 0, 1e-6, 1000, 10000, 10, 6.5, -6.5]).stopped == ["IP=0: NO RAMP"]
