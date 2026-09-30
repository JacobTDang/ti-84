import pytest

from ti84.harness import run_tool

approx = pytest.approx


def test_ohmv():
    r = run_tool("ohmv", [0.002, 4700])
    assert r.value("V") == approx(9.4)
    assert r.value("P") == approx(0.0188)
    assert r.answers == ["OHMS LAW: FIND V", "V=9.4 V", "P=18.8m W"]
    assert r.work[:3] == ["V=I*R", "=2m*4.7k", "=9.4 V"]


def test_ohmi():
    r = run_tool("ohmi", [12, 3000])
    assert r.value("I") == approx(0.004)
    assert r.value("P") == approx(0.048)


def test_ohmr():
    r = run_tool("ohmr", [5, 0.0025])
    assert r.value("R") == approx(2000)
    assert r.value("P") == approx(0.0125)


def test_rser_treats_zero_as_missing():
    r = run_tool("rser", [1000, 2200, 0])
    assert r.value("RS") == approx(3200)
    assert "RS=3.2k Ω" in r.answers


def test_rpar2():
    r = run_tool("rpar2", [1000, 1000])
    assert r.value("RP") == approx(500)
    assert r.work == ["RP=R1*R2/(R1+R2)", "=1k*1k/(1k+1k)", "=500 Ω"]


def test_rpar3():
    r = run_tool("rpar3", [300, 600, 200])
    assert r.value("RP") == approx(100)


def test_vdiv():
    r = run_tool("vdiv", [10, 1000, 2000])
    assert r.value("VOUT") == approx(20 / 3)
    assert r.value("I") == approx(10 / 3000)
    assert r.answers == ["VOLTAGE DIVIDER", "VOUT=6.667 V", "I=3.333m A"]
    assert r.work == [
        "VOUT=VS*R2/(R1+R2)",
        "=10*2k/(1k+2k)",
        "=6.667 V",
        "I=VS/(R1+R2)",
        "=10/(1k+2k)",
        "=3.333m A",
    ]


def test_idiv():
    r = run_tool("idiv", [0.006, 1000, 2000])
    assert r.value("I1") == approx(0.004)
    assert r.value("I2") == approx(0.002)
    assert r.value("I1") + r.value("I2") == approx(0.006)
