import pytest

from ti84.harness import HarnessError, run_tool
from ti84.model import Calc, Guard, Input, Note, Tool, Topic, Verdict, Case

VDIV = Tool(
    id="vdiv",
    label="VOLT DIVIDER",
    title="VOLTAGE DIVIDER",
    picture=("VS + TO TOP OF R1", "R1 MEETS R2 AT VOUT"),
    inputs=(Input("V", "VS V="), Input("R", "R1 Ω="), Input("S", "R2 Ω=")),
    steps=(
        Calc("O", "VOUT", "VS*R2/(R1+R2)", "V*S/(R+S)", "V"),
        Calc("I", "I", "VS/(R1+R2)", "V/(R+S)", "A"),
        Verdict("Str1", "SIGN", (Case("O<0", "NEGATIVE"),), "POSITIVE"),
        Note("VOUT IS ACROSS R2"),
    ),
    answers=("VOUT", "I", "SIGN"),
)

GUARDED = Tool(
    id="inverse",
    label="INVERSE",
    title="ONE OVER X",
    picture=("X MUST NOT BE 0",),
    inputs=(Input("X", "X="),),
    steps=(Guard("X=0", ("X IS ZERO:", "TRY AGAIN")), Calc("Y", "Y", "1/X", "1/X")),
    answers=("Y",),
)


def filler(k):
    return Tool(
        id=f"f{k}",
        label=f"FILL {k}",
        title=f"FILL {k}",
        picture=("P",),
        inputs=(Input("A", "A="),),
        steps=(Calc("B", "B", "A*2", "A*2"),),
        answers=("B",),
    )


TOPICS = [
    Topic("EEFIRST", "FIRST", (filler(1),)),
    Topic("EETEST", "TEST", (VDIV, *[filler(k) for k in range(2, 7)], GUARDED)),
]


def test_run_tool_reads_answers_work_and_values():
    r = run_tool("vdiv", [10, 1000, 2000], topics=TOPICS)
    assert r.answers == ["VOLTAGE DIVIDER", "VOUT=6.667 V", "I=3.333m A", "SIGN: POSITIVE"]
    assert r.work == [
        "VOUT=VS*R2/(R1+R2)",
        "=10*2k/(1k+2k)",
        "=6.667 V",
        "I=VS/(R1+R2)",
        "=10/(1k+2k)",
        "=3.333m A",
        "SIGN: POSITIVE",
        "VOUT IS ACROSS R2",
    ]
    assert r.value("VOUT") == pytest.approx(20 / 3)
    assert r.value("SIGN") == "POSITIVE"
    assert r.stopped == []
    assert r.run.leaks == 0
    assert r.run.prompts == ["VS V=", "R1 Ω=", "R2 Ω="]


def test_run_tool_shows_the_picture_before_the_inputs():
    r = run_tool("vdiv", [10, 1000, 2000], topics=TOPICS)
    picture = r.run.screens[0]
    assert picture[0].rstrip() == "VOLTAGE DIVIDER"
    assert picture[1].rstrip() == "VS + TO TOP OF R1"
    assert picture[9].rstrip() == "ENTER:GO"


def test_run_tool_negative_inputs_and_text_inputs():
    r = run_tool("vdiv", ["⁻10", 1000, 2000], topics=TOPICS)
    assert r.value("SIGN") == "NEGATIVE"
    assert r.work[1] == "=(-10)*2k/(1k+2k)"


def test_run_tool_goes_through_the_more_page():
    r = run_tool("inverse", [4], topics=TOPICS)
    assert r.value("Y") == 0.25
    assert [m.chosen for m in r.run.menus[:3]] == ["TEST", "MORE", "INVERSE"]


def test_run_tool_reports_a_guard():
    r = run_tool("inverse", [0], topics=TOPICS)
    assert r.stopped == ["X IS ZERO:", "TRY AGAIN"]
    assert r.answers == []
    assert r.work == []


def test_run_tool_pages_long_work():
    tool = Tool(
        id="long",
        label="LONG",
        title="LONG",
        picture=("P",),
        inputs=(Input("A", "A="),),
        steps=tuple(Calc(chr(ord("B") + k), f"S{k}", "A+1", "A+1") for k in range(6)),
        answers=("S0",),
    )
    r = run_tool("long", [1], topics=[Topic("EELONG", "LONG", (tool,))])
    assert len(r.work) == 18
    assert r.work[-3:] == ["S5=A+1", "=1+1", "=2"]


def test_run_tool_checks_the_number_of_inputs():
    with pytest.raises(HarnessError, match="takes 3 inputs, got 1"):
        run_tool("vdiv", [10], topics=TOPICS)


def test_run_tool_unknown_tool():
    with pytest.raises(KeyError, match="no tool with id 'nope'"):
        run_tool("nope", [], topics=TOPICS)
