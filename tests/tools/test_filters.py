import cmath
import math

import pytest

from ti84.harness import run_tool

approx = pytest.approx


def test_rclp_at_the_cutoff():
    fc = 1 / (2 * math.pi * 1000 * 1e-6)
    r = run_tool("rclp", [1000, 1e-6, fc])
    assert r.value("wc") == approx(1000)
    assert r.value("fc") == approx(fc)
    assert r.value("|H|") == approx(1 / math.sqrt(2))
    assert r.value("DB") == approx(20 * math.log10(1 / math.sqrt(2)))
    assert r.value("∠H") == approx(-45)
    assert r.answers == ["RC LOW-PASS FILTER", "fc=159.2 Hz", "|H|=707.1m V/V", "DB=-3.01 dB", "∠H=-45 °"]


def test_rchp_a_decade_below_the_cutoff():
    fc = 1 / (2 * math.pi * 1000 * 1e-6)
    r = run_tool("rchp", [1000, 1e-6, fc / 10])
    h = (0.1j) / (1 + 0.1j)
    assert r.value("H") == approx(h)
    assert r.value("∠H") == approx(math.degrees(cmath.phase(h)))


def test_rcload():
    r = run_tool("rcload", [1000, 1e-6, 1000])
    assert r.value("K") == approx(0.5)
    assert r.value("wc LOADED") == approx(2000)
    assert r.value("fc LOADED") == approx(2000 / (2 * math.pi))


def test_actlp():
    r = run_tool("actlp", [1000, 10000, 1e-8, 1000])
    wc = 1 / (10000 * 1e-8)
    w = 2 * math.pi * 1000
    h = -10 / (1 + 1j * w / wc)
    assert r.value("G0") == approx(-10)
    assert r.value("wc") == approx(wc)
    assert r.value("H") == approx(h)
    assert r.value("∠H") == approx(math.degrees(cmath.phase(h)))


def test_acthp():
    r = run_tool("acthp", [1000, 1e-6, 10000, 1000])
    wc = 1 / (1000 * 1e-6)
    x = 2j * math.pi * 1000 / wc
    assert r.value("wc") == approx(wc)
    assert r.value("H") == approx(-10 * x / (1 + x))


def test_so2_course_example():
    r = run_tool("so2", [1, 800, 1e6, 1])
    q = 1.25
    assert r.value("w0") == approx(1000)
    assert r.value("Q") == approx(q)
    assert r.value("|HLP(jw0)|") == approx(q)
    k = 1 - 1 / (2 * q * q)
    wc = 1000 * math.sqrt(k + math.sqrt(1 + k * k))
    assert r.value("wc LP") == approx(wc)
    assert r.value("wc HP") == approx(1e6 / wc)
    half = math.sqrt(1 + 1 / (4 * q * q))
    assert r.value("wL BP") == approx(1000 * half - 400)
    assert r.value("wH BP") == approx(1000 * half + 400)
    assert r.value("BW") == approx(800)


def test_so2_butterworth_cutoff_is_w0():
    r = run_tool("so2", [1, math.sqrt(2) * 1000, 1e6, 1])
    assert r.value("wc LP") == approx(1000)


def test_sklpa():
    r = run_tool("sklpa", [146.47e3, 78.61e3, 2.2e-9, 1e-9])
    assert r.value("m") == approx(146.47 / 78.61)
    assert r.value("n") == approx(2.2)
    assert r.value("w0") == approx(1 / math.sqrt(146.47e3 * 78.61e3 * 2.2e-9 * 1e-9))
    assert r.value("Q") == approx(1 / math.sqrt(2), rel=1e-3)


def test_sklpd_course_example():
    # M3_L5 slides 14-18: fc = 1 kHz, Q = 1/sqrt(2), C2 = 1 nF, C1 = 2.2 nF.
    r = run_tool("sklpd", [1000, 1 / math.sqrt(2), 1e-9, 2.2])
    assert r.value("k") == approx(1.2)
    assert r.value("m") == approx(1.2 + math.sqrt(1.2**2 - 1))
    assert r.value("R2") == approx(78.61e3, rel=1e-3)
    assert r.value("R1") == approx(146.47e3, rel=1e-3)
    assert r.value("C1") == approx(2.2e-9)
    assert "R1=146.5k Ω" in r.answers


def test_sklpd_guard():
    r = run_tool("sklpd", [1000, 1 / math.sqrt(2), 1e-9, 1])
    assert r.stopped == ["n TOO SMALL:", "NEED n ≥ 4Q²"]


def test_skhpa():
    r = run_tool("skhpa", [1e-9, 1e-9, 112.5e3, 225.1e3])
    assert r.value("n") == approx(1)
    assert r.value("m") == approx(112.5 / 225.1)
    assert r.value("Q") == approx(1 / math.sqrt(2), rel=1e-3)
    assert r.value("f0") == approx(1000, rel=1e-3)


def test_skhpd_course_example():
    r = run_tool("skhpd", [1000, 1 / math.sqrt(2), 1e-9])
    assert r.value("m") == approx(0.5)
    assert r.value("R2") == approx(225.1e3, rel=1e-3)
    assert r.value("R1") == approx(112.5e3, rel=1e-3)


def test_ladda_course_example():
    # M3_L5 slide 7 parts.
    r = run_tool("ladda", [1000, 5.28e-9, 3.25e3, 0.528e-9])
    assert r.value("w0") == approx(3.32e5, rel=2e-3)
    assert r.value("Q") == approx(0.4, rel=2e-3)


def test_laddd_course_example():
    r = run_tool("laddd", [3.32e5, 0.4, 1000, 10])
    assert r.value("MAX Q") == approx(0.5 * math.sqrt(10 / 11))
    assert r.value("R2") == approx(3.248e3, rel=1e-3)
    assert r.value("C2") == approx(0.5285e-9, rel=1e-3)
    assert r.value("C1") == approx(5.285e-9, rel=1e-3)


def test_laddd_guard():
    r = run_tool("laddd", [3.32e5, 0.49, 1000, 10])
    assert r.stopped == ["Q TOO HIGH FOR", "THIS C1/C2"]


def test_mfb():
    r1, r2, r3, c1, c2 = 10e3, 100e3, 1e3, 10e-9, 10e-9
    r = run_tool("mfb", [r1, r2, r3, c1, c2])
    w0 = math.sqrt((1 + r1 / r3) / (r1 * r2 * c1 * c2))
    bw = (c1 + c2) / (r2 * c1 * c2)
    assert r.value("w0") == approx(w0)
    assert r.value("BW") == approx(bw)
    assert r.value("Q") == approx(w0 / bw)
    assert r.value("G0") == approx(-r2 / (2 * r1))


def test_sv_made_up_course_values():
    # M3_L6 slides 5-6 with the practice values from the deck.
    r = run_tool("sv", [10e3, 40e3, 10e3, 40e3, 10e3, 10e-9])
    assert r.value("G3") == approx(4)
    assert r.value("w0") == approx(2e4)
    assert r.value("Q") == approx(2)
    assert r.value("HP GAIN") == approx(4)
    assert r.value("BP GAIN") == approx(-4)
    assert r.value("LP GAIN") == approx(1)
