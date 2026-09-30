from ti84.model import Calc, Case, Guard, Input, Note, Raw, Tool, Topic, Verdict


solve = Tool(
    id="solve",
    label="SOLVE EQNS",
    title="SOLVE LINEAR EQUATIONS",
    picture=(
        "UP TO 4 EQNS, 4 UNKNOWNS",
        "TYPE ALL ROWS IN ONE LIST",
        " a11,a12,b1,a21,a22,b2..",
        "2x1+3x2=5 AND x1-x2=0:",
        " {2,3,5,1,⁻1,0}",
        "COMPLEX VALUES ALLOWED",
    ),
    inputs=(
        Input("L₁", "ROWS {..}=", "list"),
    ),
    steps=(
        Raw(writes=("N",), compute=("(√(4*dim(L₁)+1)-1)/2→N",)),
        Guard("N≠int(N) or N<2 or N>4", ("NEED N*(N+1) NUMBERS", "FOR N EQUATIONS, N=2-4")),
        Raw(
            writes=("F", "K", "P", "M", "I", "V", "J", "T", "X", "S", "E", "L₂", "L₃"),
            compute=(
                "L₁→L₃",
                "1ᴇ⁻9*max(abs(L₁))→E",
                "0→F",
                "For(K,1,N)",
                "K→P",
                "0→M",
                "For(I,K,N)",
                "abs(L₃((I-1)*(N+1)+K))→V",
                "If V>M",
                "Then",
                "V→M",
                "I→P",
                "End",
                "End",
                "If M≤E",
                "Then",
                "1→F",
                "Else",
                "If P≠K",
                "Then",
                "For(J,K,N+1)",
                "L₃((P-1)*(N+1)+J)→T",
                "L₃((K-1)*(N+1)+J)→L₃((P-1)*(N+1)+J)",
                "T→L₃((K-1)*(N+1)+J)",
                "End",
                "End",
                "For(I,K+1,N)",
                "L₃((I-1)*(N+1)+K)/L₃((K-1)*(N+1)+K)→M",
                "For(J,K,N+1)",
                "L₃((I-1)*(N+1)+J)-M*L₃((K-1)*(N+1)+J)→L₃((I-1)*(N+1)+J)",
                "End",
                "End",
                "End",
                "End",
                "If F=0",
                "Then",
                "seq(0,X,1,N)→L₂",
                "For(K,1,N)",
                "N-K+1→I",
                "0→S",
                "If I<N",
                "Then",
                "For(J,I+1,N)",
                "S+L₃((I-1)*(N+1)+J)*L₂(J)→S",
                "End",
                "End",
                "(L₃((I-1)*(N+1)+N+1)-S)/L₃((I-1)*(N+1)+I)→L₂(I)",
                "End",
                "End",
            ),
            answers=(
                "For(I,1,N)",
                '"x"+toString(I)+"="→Str0',
                "L₂(I)",
                "prgmZC",
                "Str0+Str9→Str0",
                "prgmZP",
                "End",
            ),
            work=(
                "For(I,1,N)",
                '"EQ"+toString(I)+": "→Str0',
                "For(J,1,N)",
                "L₁((I-1)*(N+1)+J)",
                "prgmZS",
                'Str0+Str9+"*x"+toString(J)→Str0',
                "If J<N",
                "Then",
                'Str0+"+"→Str0',
                "End",
                "End",
                'Str0+"="→Str0',
                "L₁((I-1)*(N+1)+N+1)",
                "prgmZS",
                "Str0+Str9→Str0",
                "prgmZP",
                "End",
                '"SOLVED BY ELIMINATION"→Str0',
                "prgmZP",
            ),
        ),
        Guard("F", ("NO UNIQUE SOLUTION",)),
    ),
    answers=(),
)

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
    tools=(solve, todb, fromdb, hzrad, radhz, scope, e12),
)
