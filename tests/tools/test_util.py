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
