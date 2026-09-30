from dataclasses import replace

import pytest

from ti84.gen import gen_main, gen_topic, pieces
from ti84.model import Calc, Input, Tool, Topic
from ti84.tokens import lint

EXPECTED_TOPIC = """\
Radian
Float
Normal
a+b𝑖
Lbl M
Menu("TEST","VOLT DIVIDER",A,"MIX",B,"BACK",Q)
Lbl Q
ClrHome
Return
Lbl A
ClrHome
Output(1,1,"VOLTAGE DIVIDER")
Output(2,1,"VS + TO TOP OF R1")
Output(10,1,"ENTER:GO")
Pause
ClrHome
Input "VS V=",V
Input "R1 Ω=",R
Input "R2 Ω=",S
V*S/(R+S)→O
ClrHome
1→θ
"VOLTAGE DIVIDER"→Str0
prgmZP
O
prgmZF
"VOUT="+Str9+" V"→Str0
prgmZP
"ENTER:WORK  CLEAR:QUIT"→Str0
prgmZE
If not(θ)
Goto M
"VOUT=VS*R2/(R1+R2)"→Str0
prgmZP
"="→Str0
V
prgmZS
Str0+Str9+"*"→Str0
S
prgmZS
Str0+Str9+"/("→Str0
R
prgmZS
Str0+Str9+"+"→Str0
S
prgmZS
Str0+Str9+")"→Str0
prgmZP
O
prgmZF
"="+Str9+" V"→Str0
prgmZP
"VOUT IS ACROSS R2"→Str0
prgmZP
"DONE  ENTER:MENU"→Str0
prgmZE
Goto M
Lbl B
ClrHome
Output(1,1,"MIXED STEPS")
Output(2,1,"LINE")
Output(10,1,"ENTER:GO")
Pause
ClrHome
Input "N {..}=",L₁
Input "F Hz=",F
2*pi*F→W
𝑖*W→S
0→N
For(K,1,dim(L₁))
N*S+L₁(K)→N
End
If W=0
Goto B1
abs(N)→M
20*log(M)→D
If M>1
Then
"BIG"→Str1
Else
If M=1
Then
"ONE"→Str1
Else
"SMALL"→Str1
End
End
M*2→X
ClrHome
1→θ
"MIXED STEPS"→Str0
prgmZP
M
prgmZF
"MAG="+Str9→Str0
prgmZP
D
prgmZR
"DB="+Str9+" dB"→Str0
prgmZP
"SIZE: "+Str1→Str0
prgmZP
"RAW ANSWER"→Str0
prgmZP
"ENTER:WORK  CLEAR:QUIT"→Str0
prgmZE
If not(θ)
Goto M
"w=2*PI*F"→Str0
prgmZP
"=2*PI*"→Str0
F
prgmZS
Str0+Str9→Str0
prgmZP
W
prgmZF
"="+Str9+" rad/s"→Str0
prgmZP
"s=j*w"→Str0
prgmZP
"=j*"→Str0
W
prgmZS
Str0+Str9→Str0
prgmZP
S
prgmZC
"="+Str9+" 1/s"→Str0
prgmZP
"N(s)=NUM AT s"→Str0
prgmZP
N
prgmZC
"="+Str9→Str0
prgmZP
"MAG=ABS(N)"→Str0
prgmZP
"=ABS("→Str0
N
prgmZS
Str0+Str9+")"→Str0
prgmZP
M
prgmZF
"="+Str9→Str0
prgmZP
"DB=20*LOG(MAG)"→Str0
prgmZP
"=20*LOG("→Str0
M
prgmZS
Str0+Str9+")"→Str0
prgmZP
D
prgmZR
"="+Str9+" dB"→Str0
prgmZP
"SIZE: "+Str1→Str0
prgmZP
"RAW WORK"→Str0
prgmZP
"DONE  ENTER:MENU"→Str0
prgmZE
Goto M
Lbl B1
ClrHome
Output(1,1,"MIXED STEPS")
Output(3,1,"F MUST NOT BE 0")
Output(10,1,"ENTER:MENU")
Pause
Goto M
""".replace("\nPause\n", "\nPause \n")  # the Pause token is spelled with a trailing space


def test_gen_topic_matches_the_expected_program(topic):
    assert gen_topic(topic) == EXPECTED_TOPIC


def test_generated_topic_lints_clean(topic):
    lint(gen_topic(topic), topic.program)


def test_calc_without_substitution_skips_the_numbers_line(vdiv):
    step = replace(vdiv.steps[0], sub=False)
    tool = replace(vdiv, steps=(step,))
    text = gen_topic(Topic("EETEST", "TEST", (tool,)))
    assert '"="→Str0' not in text
    assert '"VOUT=VS*R2/(R1+R2)"→Str0\nprgmZP\nO\nprgmZF\n' in text


def test_expression_without_variables_skips_the_numbers_line():
    tool = Tool(
        id="k",
        label="K",
        title="K",
        picture=("P",),
        inputs=(Input("A", "A="),),
        steps=(Calc("B", "B", "2*PI", "2*pi"),),
        answers=("B",),
    )
    text = gen_topic(Topic("EETEST", "TEST", (tool,)))
    assert '"B=2*PI"→Str0\nprgmZP\nB\nprgmZF\n' in text


def _tools(count):
    return tuple(
        Tool(
            id=f"t{k}",
            label=f"TOOL {k}",
            title=f"TOOL {k}",
            picture=("P",),
            inputs=(Input("A", "A="),),
            steps=(Calc("B", "B", "A", "A"),),
            answers=("B",),
        )
        for k in range(1, count + 1)
    )


def test_menu_pages_hold_six_tools_then_more():
    text = gen_topic(Topic("EETEST", "TEST", _tools(14)))
    assert (
        'Lbl M\nMenu("TEST","TOOL 1",A,"TOOL 2",B,"TOOL 3",C,"TOOL 4",D,"TOOL 5",E,"TOOL 6",F,"MORE",M1)\n'
        'Lbl M1\nMenu("TEST","TOOL 7",G,"TOOL 8",H,"TOOL 9",I,"TOOL 10",J,"TOOL 11",K,"TOOL 12",L,"MORE",M2)\n'
        'Lbl M2\nMenu("TEST","TOOL 13",N,"TOOL 14",O,"BACK",Q)\n'
        "Lbl Q\n"
    ) in text


def test_menu_with_seven_tools_needs_two_pages():
    text = gen_topic(Topic("EETEST", "TEST", _tools(7)))
    assert '"MORE",M1)\nLbl M1\nMenu("TEST","TOOL 7",G,"BACK",Q)\n' in text


def test_gen_main():
    topics = (
        Topic("EETEST", "TEST", _tools(1)),
        Topic("EEOTHER", "OTHER", _tools(1)),
    )
    assert gen_main(topics) == (
        "Lbl M\n"
        'Menu("EE","TEST",1,"OTHER",2,"QUIT",Q)\n'
        "Lbl 1\nprgmEETEST\nGoto M\n"
        "Lbl 2\nprgmEEOTHER\nGoto M\n"
        "Lbl Q\nClrHome\n"
    )
    lint(gen_main(topics), "EE")


@pytest.mark.parametrize(
    "expr, expected",
    [
        ("V*S/(R+S)", [("var", "V"), ("text", "*"), ("var", "S"), ("text", "/("), ("var", "R"), ("text", "+"), ("var", "S"), ("text", ")")]),
        ("1/√(L*C)", [("text", "1/SQRT("), ("var", "L"), ("text", "*"), ("var", "C"), ("text", ")")]),
        ("⁻𝑖/(W*C)", [("text", "-j/("), ("var", "W"), ("text", "*"), ("var", "C"), ("text", ")")]),
        ("2*pi*F", [("text", "2*PI*"), ("var", "F")]),
        ("1.5ᴇ3*A", [("text", "1.5ᴇ3*"), ("var", "A")]),
        ("W²/X", [("var", "W"), ("text", "²/"), ("var", "X")]),
        ("angle(G)*180/pi", [("text", "ANGLE("), ("var", "G"), ("text", ")*180/PI")]),
        (
            "B+(A-B)*𝑒^(⁻X/T)",
            [("var", "B"), ("text", "+("), ("var", "A"), ("text", "-"), ("var", "B"), ("text", ")*e^(-"), ("var", "X"), ("text", "/"), ("var", "T"), ("text", ")")],
        ),
        ("min(H,abs(L))/abs(G)", [("text", "MIN("), ("var", "H"), ("text", ",ABS("), ("var", "L"), ("text", "))/ABS("), ("var", "G"), ("text", ")")]),
    ],
)
def test_pieces_split_an_expression_into_display_text_and_variables(expr, expected):
    assert pieces(expr) == expected


def test_guard_labels_count_per_tool():
    from ti84.model import Guard

    def guarded(k):
        return Tool(
            id=f"g{k}",
            label=f"G{k}",
            title=f"G{k}",
            picture=("P",),
            inputs=(Input("A", "A="),),
            steps=(Guard("A=0", ("ZERO",)), Calc("B", "B", "A", "A")),
            answers=("B",),
        )

    text = gen_topic(Topic("EETEST", "TEST", (guarded(1), guarded(2))))
    assert "If A=0\nGoto A1\n" in text
    assert "If A=0\nGoto B1\n" in text
    assert "Lbl B1\n" in text


def test_gen_main_rejects_more_than_six_topics():
    from ti84.model import ModelError

    topics = tuple(Topic(f"EE{k}", f"T{k}", _tools(1)) for k in range(7))
    with pytest.raises(ModelError, match="at most 6 topics"):
        gen_main(topics)
