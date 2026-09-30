import cmath
import math

import pytest

from ti84.harness import run_tool

approx = pytest.approx


def test_r2p():
    r = run_tool("r2p", ["3+4𝑖"])
    assert r.value("|Z|") == approx(5)
    assert r.value("∠Z") == approx(math.degrees(math.atan2(4, 3)))
    assert "∠Z=53.13 °" in r.answers


def test_r2p_left_half_plane_uses_the_right_quadrant():
    r = run_tool("r2p", ["⁻1-𝑖"])
    assert r.value("∠Z") == approx(-135)


def test_p2r():
    r = run_tool("p2r", [10, 30])
    assert r.value("A") == approx(10 * math.cos(math.radians(30)))
    assert r.value("B") == approx(5)
    assert r.value("Z") == approx(complex(10 * math.cos(math.radians(30)), 5))


def test_zc_course_numbers():
    r = run_tool("zc", [1000, 1e-6])
    assert r.value("w") == approx(2 * math.pi * 1000)
    assert r.value("XC") == approx(1 / (2 * math.pi * 1000 * 1e-6))
    assert r.value("ZC") == approx(-1j / (2 * math.pi * 1000 * 1e-6))
    assert r.answers == ["CAPACITOR IMPEDANCE", "w=6.283k rad/s", "XC=159.2 Ω", "ZC=-j159.2 Ω"]


def test_zl():
    r = run_tool("zl", [1000, 0.01])
    assert r.value("XL") == approx(2 * math.pi * 10)
    assert r.value("ZL") == approx(2j * math.pi * 10)


def test_zser():
    r = run_tool("zser", ["100+50𝑖", "⁻20𝑖", 0])
    assert r.value("Z") == approx(100 + 30j)
    assert r.value("|Z|") == approx(abs(100 + 30j))
    assert r.value("∠Z") == approx(math.degrees(cmath.phase(100 + 30j)))


def test_zpar():
    z1, z2 = 100, -100j
    r = run_tool("zpar", [100, "⁻100𝑖"])
    expected = z1 * z2 / (z1 + z2)
    assert r.value("Z") == approx(expected)
    assert r.value("∠Z") == approx(-45)


def test_zrlc_at_resonance_is_just_r():
    f0 = 1 / (2 * math.pi * math.sqrt(0.01 * 1e-6))
    r = run_tool("zrlc", [100, 0.01, 1e-6, f0])
    assert r.value("Z") == approx(100, abs=1e-6)
    assert r.value("∠Z") == approx(0, abs=1e-6)


def test_zrlc_off_resonance():
    w = 2 * math.pi * 1000
    expected = 100 + 1j * w * 0.01 + 1 / (1j * w * 1e-6)
    r = run_tool("zrlc", [100, 0.01, 1e-6, 1000])
    assert r.value("ZL") == approx(1j * w * 0.01)
    assert r.value("ZC") == approx(1 / (1j * w * 1e-6))
    assert r.value("Z") == approx(expected)
    assert r.value("|Z|") == approx(abs(expected))


def test_pdiv():
    vs, z1, z2 = 10, 1000, -1000j
    r = run_tool("pdiv", [10, 1000, "⁻1000𝑖"])
    expected = vs * z2 / (z1 + z2)
    assert r.value("VOUT") == approx(expected)
    assert r.value("|VOUT|") == approx(abs(expected))
    assert r.value("∠VOUT") == approx(-45)
