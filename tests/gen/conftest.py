import pytest

from ti84.model import Calc, Case, Guard, Input, Note, Poly, Raw, Tool, Topic, Verdict


def make_vdiv():
    return Tool(
        id="vdiv",
        label="VOLT DIVIDER",
        title="VOLTAGE DIVIDER",
        picture=("VS + TO TOP OF R1",),
        inputs=(Input("V", "VS V="), Input("R", "R1 Ω="), Input("S", "R2 Ω=")),
        steps=(
            Calc("O", "VOUT", "VS*R2/(R1+R2)", "V*S/(R+S)", "V"),
            Note("VOUT IS ACROSS R2"),
        ),
        answers=("VOUT",),
    )


def make_mix():
    return Tool(
        id="mix",
        label="MIX",
        title="MIXED STEPS",
        picture=("LINE",),
        inputs=(Input("L₁", "N {..}=", "list"), Input("F", "F Hz=")),
        steps=(
            Calc("W", "w", "2*PI*F", "2*pi*F", "rad/s"),
            Calc("S", "s", "j*w", "𝑖*W", "1/s", "cplx"),
            Poly("N", "N(s)", "NUM AT s", "L₁", "S", "K"),
            Guard("W=0", ("F MUST NOT BE 0",)),
            Calc("M", "MAG", "ABS(N)", "abs(N)"),
            Calc("D", "DB", "20*LOG(MAG)", "20*log(M)", "dB", "fix2"),
            Verdict("Str1", "SIZE", (Case("M>1", "BIG"), Case("M=1", "ONE")), "SMALL"),
            Raw(
                writes=("X",),
                compute=("M*2→X",),
                answers=('"RAW ANSWER"→Str0', "prgmZP"),
                work=('"RAW WORK"→Str0', "prgmZP"),
            ),
        ),
        answers=("MAG", "DB", "SIZE"),
    )


@pytest.fixture
def vdiv():
    return make_vdiv()


@pytest.fixture
def topic():
    return Topic(program="EETEST", title="TEST", tools=(make_vdiv(), make_mix()))
