from ti84.model import Calc, Case, Guard, Input, Poly, Raw, Tool, Topic, Verdict

taurc = Tool(
    id="taurc",
    label="TAU OF RC",
    title="RC TIME CONSTANT",
    picture=(
        "R AND C IN ONE LOOP",
        "TAU = R*C",
        "AFTER 5 TAU: SETTLED",
    ),
    inputs=(
        Input("R", "R Ω="),
        Input("C", "C F="),
    ),
    steps=(
        Calc("T", "TAU", "R*C", "R*C", "s"),
        Calc("U", "5TAU", "5*TAU", "5*T", "s"),
        Calc("W", "wc", "1/TAU", "1/T", "rad/s"),
        Calc("F", "fc", "wc/(2*PI)", "W/(2*pi)", "Hz"),
    ),
    answers=("TAU", "5TAU", "wc", "fc"),
)

taurl = Tool(
    id="taurl",
    label="TAU OF RL",
    title="RL TIME CONSTANT",
    picture=(
        "R AND L IN ONE LOOP",
        "TAU = L/R",
        "AFTER 5 TAU: SETTLED",
    ),
    inputs=(
        Input("L", "L H="),
        Input("R", "R Ω="),
    ),
    steps=(
        Calc("T", "TAU", "L/R", "L/R", "s"),
        Calc("U", "5TAU", "5*TAU", "5*T", "s"),
        Calc("W", "wc", "1/TAU", "1/T", "rad/s"),
        Calc("F", "fc", "wc/(2*PI)", "W/(2*pi)", "Hz"),
    ),
    answers=("TAU", "5TAU", "wc", "fc"),
)

step1 = Tool(
    id="step1",
    label="1ST ORDER STEP",
    title="FIRST-ORDER STEP RESPONSE",
    picture=(
        "V(0): JUST AFTER SWITCH",
        " C KEEPS V, L KEEPS I",
        "V(INF): LONG AFTER",
        " C OPEN, L SHORT",
    ),
    inputs=(
        Input("A", "V(0)="),
        Input("B", "V(INF)="),
        Input("T", "TAU s="),
        Input("X", "t s="),
    ),
    steps=(
        Calc("V", "v(t)", "VINF+(V0-VINF)*e^(-t/TAU)", "B+(A-B)*𝑒^(⁻X/T)", ""),
    ),
    answers=("v(t)",),
)

treach = Tool(
    id="treach",
    label="TIME TO REACH",
    title="TIME TO REACH A VALUE",
    picture=(
        "FIRST-ORDER CIRCUIT",
        "GOING FROM V(0) TO V(INF)",
        "WHEN DOES IT HIT TARGET?",
    ),
    inputs=(
        Input("A", "V(0)="),
        Input("B", "V(INF)="),
        Input("T", "TAU s="),
        Input("V", "TARGET="),
    ),
    steps=(
        Guard("(A-B)/(V-B)≤1", ("TARGET NOT BETWEEN", "V(0) AND V(INF)")),
        Calc("X", "t", "TAU*LN((V0-VINF)/(V-VINF))", "T*ln((A-B)/(V-B))", "s"),
    ),
    answers=("t",),
)

srlc = Tool(
    id="srlc",
    label="SERIES RLC",
    title="SERIES RLC POLES",
    picture=(
        "SOURCE,R,L,C IN ONE LOOP",
        "OUTPUT ACROSS C",
        "H=w0²/(s²+2as+w0²)",
    ),
    inputs=(
        Input("R", "R Ω="),
        Input("L", "L H="),
        Input("C", "C F="),
    ),
    steps=(
        Calc("A", "a", "R/(2L)", "R/(2*L)", "1/s"),
        Calc("W", "w0", "1/SQRT(LC)", "1/√(L*C)", "rad/s"),
        Calc("Z", "ZETA", "a/w0", "A/W", ""),
        Calc("Q", "Q", "w0/(2a)", "W/(2*A)", ""),
        Calc("P", "p1", "-a+SQRT(a²-w0²)", "⁻A+√(A²-W²)", "1/s", "cplx"),
        Calc("N", "p2", "-a-SQRT(a²-w0²)", "⁻A-√(A²-W²)", "1/s", "cplx"),
        Verdict(
            "Str1",
            "TYPE",
            (
                Case("A>W", "OVERDAMPED: 2 REAL POLES"),
                Case("A=W", "CRITICAL: REPEATED POLE"),
            ),
            "UNDERDAMPED: RINGS"
        ),
    ),
    answers=("a", "w0", "TYPE", "p1", "p2"),
)

prlc = Tool(
    id="prlc",
    label="PARALLEL RLC",
    title="PARALLEL RLC POLES",
    picture=(
        "R, L, C ALL IN PARALLEL",
        "SAME VOLTAGE ACROSS ALL",
    ),
    inputs=(
        Input("R", "R Ω="),
        Input("L", "L H="),
        Input("C", "C F="),
    ),
    steps=(
        Calc("A", "a", "1/(2RC)", "1/(2*R*C)", "1/s"),
        Calc("W", "w0", "1/SQRT(LC)", "1/√(L*C)", "rad/s"),
        Calc("Z", "ZETA", "a/w0", "A/W", ""),
        Calc("Q", "Q", "w0/(2a)", "W/(2*A)", ""),
        Calc("P", "p1", "-a+SQRT(a²-w0²)", "⁻A+√(A²-W²)", "1/s", "cplx"),
        Calc("N", "p2", "-a-SQRT(a²-w0²)", "⁻A-√(A²-W²)", "1/s", "cplx"),
        Verdict(
            "Str1",
            "TYPE",
            (
                Case("A>W", "OVERDAMPED: 2 REAL POLES"),
                Case("A=W", "CRITICAL: REPEATED POLE"),
            ),
            "UNDERDAMPED: RINGS"
        ),
    ),
    answers=("a", "w0", "TYPE", "p1", "p2"),
)

quad = Tool(
    id="quad",
    label="AS²+BS+C",
    title="SECOND-ORDER POLES",
    picture=(
        "DENOMINATOR AS²+BS+C",
        "TYPE A, B, C",
    ),
    inputs=(
        Input("A", "A="),
        Input("B", "B="),
        Input("C", "C="),
    ),
    steps=(
        Calc("W", "w0", "SQRT(C/A)", "√(C/A)", "rad/s"),
        Calc("Q", "Q", "SQRT(A*C)/B", "√(A*C)/B", ""),
        Calc("Z", "ZETA", "1/(2Q)", "1/(2*Q)", ""),
        Calc("D", "DISC", "B²-4AC", "B²-4*A*C", ""),
        Calc("P", "p1", "(-B+SQRT(DISC))/2A", "(⁻B+√(D))/(2*A)", "1/s", "cplx"),
        Calc("N", "p2", "(-B-SQRT(DISC))/2A", "(⁻B-√(D))/(2*A)", "1/s", "cplx"),
        Verdict(
            "Str1",
            "POLES",
            (
                Case("Q<.5", "Q<0.5: 2 REAL POLES"),
                Case("Q=.5", "Q=0.5: REPEATED POLE"),
            ),
            "Q>0.5: COMPLEX PAIR"
        ),
        Verdict(
            "Str2",
            "PEAK",
            (
                Case("Q>1/√(2)", "Q>0.707: PEAKS"),
            ),
            "NO PEAK"
        ),
    ),
    answers=("w0", "Q", "POLES", "p1", "p2", "PEAK"),
)

hjw = Tool(
    id="hjw",
    label="H(jw) AT F",
    title="EVALUATE H(s) AT s=jw",
    picture=(
        "H(s)=N(s)/D(s)",
        "TYPE COEFFICIENT LISTS,",
        "HIGHEST POWER FIRST:",
        "s²+800s+1ᴇ6 IS {1,800,1ᴇ6}",
        "F=0 GIVES DC GAIN H(0)",
    ),
    inputs=(
        Input("L₁", "N {..}=", "list"),
        Input("L₂", "D {..}=", "list"),
        Input("F", "F Hz="),
    ),
    steps=(
        Calc("W", "w", "2*PI*F", "2*pi*F", "rad/s"),
        Calc("S", "s", "j*w", "𝑖*W", "1/s", "cplx"),
        Poly("N", "N(s)", "L1(S)", "L₁", "S", "K"),
        Poly("D", "D(s)", "L2(S)", "L₂", "S", "K"),
        Calc("H", "H", "N/D", "N/D", "", "cplx"),
        Calc("M", "|H|", "ABS(H)", "abs(H)", "V/V"),
        Calc("G", "DB", "20*LOG|H|", "20*log(M)", "dB", "fix2"),
        Calc("P", "∠H", "ANGLE(H)", "angle(H)*180/pi", "°", "fix2"),
    ),
    answers=("|H|", "DB", "∠H"),
)

sine = Tool(
    id="sine",
    label="SINE IN TO OUT",
    title="SINUSOIDAL STEADY STATE",
    picture=(
        "IN: A*COS(wt+PHASE)",
        "OUT: A|H|COS(wt+PHASE+∠H)",
        "H AS COEFFICIENT LISTS,",
        "HIGHEST POWER FIRST",
    ),
    inputs=(
        Input("L₁", "N {..}=", "list"),
        Input("L₂", "D {..}=", "list"),
        Input("A", "IN AMPLITUDE="),
        Input("P", "IN PHASE °="),
        Input("F", "F Hz="),
    ),
    steps=(
        Calc("W", "w", "2*PI*F", "2*pi*F", "rad/s"),
        Calc("S", "s", "j*w", "𝑖*W", "1/s", "cplx"),
        Poly("N", "N(s)", "L1(S)", "L₁", "S", "K"),
        Poly("D", "D(s)", "L2(S)", "L₂", "S", "K"),
        Calc("H", "H", "N/D", "N/D", "", "cplx"),
        Calc("M", "|H|", "ABS(H)", "abs(H)", "V/V"),
        Calc("G", "∠H", "ANGLE(H)", "angle(H)*180/pi", "°", "fix2"),
        Calc("Y", "OUT AMP", "A*|H|", "A*M", ""),
        Calc("Q", "OUT PHASE", "PHASE+∠H", "P+G", "°", "fix2"),
    ),
    answers=("OUT AMP", "OUT PHASE"),
)

pfrac = Tool(
    id="pfrac",
    label="PARTIAL FRAC",
    title="PARTIAL FRACTIONS",
    picture=(
        "F(s)=N(s)/((s-p1)(s-p2)..)",
        "DENOMINATOR STARTS AT 1s^n",
        "POLES MUST BE DIFFERENT",
        "STEP INPUT: ADD POLE 0",
        "POLES LIKE {0,-2,-1+3i}",
    ),
    inputs=(
        Input("L₁", "N {..}=", "list"),
        Input("L₂", "POLES {..}=", "list"),
    ),
    steps=(
        Raw(
            writes=("R", "D", "I", "J"),
            compute=(
                "dim(L₂)→D",
                "0→R",
                "If D>1",
                "Then",
                "For(I,1,D-1)",
                "For(J,I+1,D)",
                "If L₂(I)=L₂(J)",
                "1→R",
                "End",
                "End",
                "End",
            ),
            answers=(),
            work=(),
        ),
        Guard("dim(L₁)>dim(L₂)", ("IMPROPER: DEG N ≥ DEG D", "DIVIDE FIRST")),
        Guard("R", ("REPEATED POLE:", "NOT HANDLED HERE")),
        Raw(
            writes=("K", "P", "A", "B", "L₃", "C", "E"),
            compute=(
                "seq(0,I,1,D)→L₃",
                "For(I,1,D)",
                "L₂(I)→P",
                "0→A",
                "For(K,1,dim(L₁))",
                "A*P+L₁(K)→A",
                "End",
                "1→B",
                "For(J,1,D)",
                "If I≠J",
                "B*(P-L₂(J))→B",
                "End",
                "A/B→L₃(I)",
                "End",
            ),
            answers=(
                "For(I,1,D)",
                "L₃(I)",
                "prgmZC",
                '"K"+toString(I)+"="+Str9→Str0',
                "prgmZP",
                "End",
            ),
            work=(
                "For(I,1,D)",
                "L₂(I)→P",
                "L₃(I)→E",
                "P",
                "prgmZS",
                '"K"+toString(I)+" AT s="+Str9→Str0',
                "prgmZP",
                "0→A",
                "For(K,1,dim(L₁))",
                "A*P+L₁(K)→A",
                "End",
                "A",
                "prgmZS",
                '"="+Str9+"/"→Str0',
                "If D>1",
                "Then",
                'Str0+"("→Str0',
                "0→C",
                "For(J,1,D)",
                "If I≠J",
                "Then",
                "If C>0",
                'Str0+"*"→Str0',
                "P-L₂(J)",
                "prgmZS",
                'Str0+Str9→Str0',
                "C+1→C",
                "End",
                "End",
                'Str0+")"→Str0',
                "Else",
                'Str0+"1"→Str0',
                "End",
                "prgmZP",
                "E",
                "prgmZC",
                '"="+Str9→Str0',
                "prgmZP",
                "If imag(P)=0",
                "Then",
                "E",
                "prgmZS",
                '"TERM: "+Str9+"*e^("→Str0',
                "P",
                "prgmZS",
                'Str0+Str9+"t)"→Str0',
                "prgmZP",
                "Else",
                "If imag(P)>0",
                "Then",
                '"PAIR: 2|K|*e^(at)*COS(bt+∠K)"→Str0',
                "prgmZP",
                "2*abs(E)",
                "prgmZF",
                '"="+Str9+"*e^("→Str0',
                "real(P)",
                "prgmZS",
                'Str0+Str9+"t)*COS("→Str0',
                "imag(P)",
                "prgmZF",
                'Str0+Str9+"t"→Str0',
                "angle(E)*180/pi→A",
                "If A≥0",
                'Str0+"+"→Str0',
                "A",
                "prgmZR",
                'Str0+Str9+"°)"→Str0',
                "prgmZP",
                "Else",
                '"(CONJUGATE OF PAIR ABOVE)"→Str0',
                "prgmZP",
                "End",
                "End",
                "End",
            ),
        ),
    ),
    answers=(),
)

TOPIC = Topic(
    program="EES",
    title="S-DOMAIN",
    tools=(taurc, taurl, step1, treach, srlc, prlc, quad, hjw, sine, pfrac),
)
