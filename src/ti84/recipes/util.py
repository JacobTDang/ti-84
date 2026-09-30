from ti84.model import Calc, Case, Guard, Input, Note, Raw, Tool, Topic, Verdict

todb = Tool(
    id="todb",
    label="RATIO TO DB",
    title="RATIO TO DECIBELS",
    picture=(
        "VOLTAGE RATIO: 20 LOG",
        "POWER RATIO: 10 LOG",
        "x10=+20dB, x2=+6dB",
    ),
    inputs=(
        Input("X", "RATIO="),
    ),
    steps=(
        Calc("D", "DB (V)", "20*LOG|X|", "20*log(abs(X))", "dB", "fix2"),
        Calc("P", "DB (P)", "10*LOG|X|", "10*log(abs(X))", "dB", "fix2"),
    ),
    answers=("DB (V)", "DB (P)"),
)

fromdb = Tool(
    id="fromdb",
    label="DB TO RATIO",
    title="DECIBELS TO RATIO",
    picture=(
        "V RATIO = 10^(DB/20)",
        "P RATIO = 10^(DB/10)",
        "-3dB = 0.707 V/V",
    ),
    inputs=(
        Input("D", "DB="),
    ),
    steps=(
        Calc("X", "V RATIO", "10^(DB/20)", "10^(D/20)", "V/V"),
        Calc("P", "P RATIO", "10^(DB/10)", "10^(D/10)", "W/W"),
    ),
    answers=("V RATIO", "P RATIO"),
)

hzrad = Tool(
    id="hzrad",
    label="HZ TO RAD/S",
    title="HERTZ TO RAD/S",
    picture=(
        "w = 2*PI*F",
        "T = 1/F",
    ),
    inputs=(
        Input("F", "F Hz="),
    ),
    steps=(
        Calc("W", "w", "2*PI*F", "2*pi*F", "rad/s"),
        Calc("T", "T", "1/F", "1/F", "s"),
    ),
    answers=("w", "T"),
)

radhz = Tool(
    id="radhz",
    label="RAD/S TO HZ",
    title="RAD/S TO HERTZ",
    picture=(
        "F = w/(2*PI)",
        "T = 1/F",
    ),
    inputs=(
        Input("W", "w rad/s="),
    ),
    steps=(
        Calc("F", "F", "w/(2*PI)", "W/(2*pi)", "Hz"),
        Calc("T", "T", "1/F", "1/F", "s"),
    ),
    answers=("F", "T"),
)

scope = Tool(
    id="scope",
    label="PHASE FROM DT",
    title="PHASE FROM A SCOPE",
    picture=(
        "DT = TIME FROM INPUT PEAK",
        " TO OUTPUT PEAK",
        "NEGATIVE IF OUTPUT LAGS",
    ),
    inputs=(
        Input("F", "F Hz="),
        Input("T", "DT s="),
    ),
    steps=(
        Calc("P", "PHASE", "360*F*DT", "360*F*T", "°", "fix2"),
    ),
    answers=("PHASE",),
)

e12 = Tool(
    id="e12",
    label="NEAREST E12",
    title="NEAREST E12 VALUE",
    picture=(
        "E12: 1 1.2 1.5 1.8 2.2 2.7",
        " 3.3 3.9 4.7 5.6 6.8 8.2",
        "TIMES A POWER OF 10",
    ),
    inputs=(
        Input("X", "VALUE="),
    ),
    steps=(
        Guard("X≤0", ("VALUE MUST BE > 0",)),
        Calc("D", "DECADE", "10^INT(LOG(X))", "10^(int(log(X)))", ""),
        Calc("M", "MANTISSA", "X/DECADE", "X/D", ""),
        Raw(
            writes=("U", "V", "W", "I"),
            compute=(
                "{1,1.2,1.5,1.8,2.2,2.7,3.3,3.9,4.7,5.6,6.8,8.2,10}→L₆",
                "sum(L₆≤M)→I",
                "L₆(I)→V",
                "L₆(min(13,I+(V≠M)))→W",
                "V→U",
                "If abs(log(W/M))<abs(log(V/M))",
                "Then",
                "W→U",
                "End",
            ),
        ),
        Calc("E", "NEAREST", "E12*DECADE", "U*D", ""),
        Calc("B", "BELOW", "E12 BELOW*DECADE", "V*D", ""),
        Calc("A", "ABOVE", "E12 ABOVE*DECADE", "W*D", ""),
    ),
    answers=("NEAREST", "BELOW", "ABOVE"),
)

TOPIC = Topic(
    program="EEUTIL",
    title="UTILITIES",
    tools=(todb, fromdb, hzrad, radhz, scope, e12),
)
