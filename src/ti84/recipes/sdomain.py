from ti84.model import Calc, Case, Guard, Input, Note, Poly, Raw, Tool, Topic, Verdict

L1, L2, L3, L4, L5, L6 = "L₁", "L₂", "L₃", "L₄", "L₅", "L₆"


def _copy(src, dst):
    return [f"seq({src}(K),K,1,dim({src}))→{dst}"]


def _strip(src, tmp):
    """Drop leading zeros. tmp must not be src."""
    return [
        "0→I",
        f"Repeat I=dim({src}) or {src}(I)≠0",
        "I+1→I",
        "End",
        f"seq({src}(I+K-1),K,1,dim({src})-I+1)→{tmp}",
        *_copy(tmp, src),
    ]


def _cancel(a, b, t1, t2):
    """Cancel a shared trailing factor of s. Temps must not be a or b."""
    return [
        "0→N",
        f"For(I,1,min(dim({a}),dim({b}))-1)",
        f"If {a}(dim({a})-I+1)=0 and {b}(dim({b})-I+1)=0 and N=I-1",
        "N+1→N",
        "End",
        "If N>0",
        "Then",
        f"seq({a}(K),K,1,dim({a})-N)→{t1}",
        f"seq({b}(K),K,1,dim({b})-N)→{t2}",
        *_copy(t1, a),
        *_copy(t2, b),
        "End",
    ]


def _mul(a, b, dest):
    return [
        f"dim({a})+dim({b})-1→W",
        f"seq(0,K,1,W)→{dest}",
        f"For(I,1,dim({a}))",
        f"For(J,1,dim({b}))",
        f"{dest}(I+J-1)+{a}(I)*{b}(J)→{dest}(I+J-1)",
        "End",
        "End",
    ]


def _add(a, b, dest):
    return [
        f"If dim({a})>dim({b})",
        "Then",
        f"dim({a})→W",
        "Else",
        f"dim({b})→W",
        "End",
        f"seq(0,K,1,W)→{dest}",
        f"For(I,1,dim({a}))",
        f"{dest}(W-dim({a})+I)+{a}(I)→{dest}(W-dim({a})+I)",
        "End",
        f"For(I,1,dim({b}))",
        f"{dest}(W-dim({b})+I)+{b}(I)→{dest}(W-dim({b})+I)",
        "End",
    ]


def _neg(lst):
    return [
        f"For(I,1,dim({lst}))",
        f"⁻{lst}(I)→{lst}(I)",
        "End",
    ]


def _arm(typ, r, l, c):
    """Series (type 1) or parallel (type 2) arm into L₃ over L₄."""
    series = [
        f"If {c}=0",
        "Then",
        "0→E",
        "Else",
        f"1/{c}→E",
        "End",
        f"{{{l},{r},E}}→{L3}",
        f"{{1,0}}→{L4}",
    ]
    parallel = [
        f"If {r}=0",
        "Then",
        "0→E",
        "Else",
        f"1/{r}→E",
        "End",
        f"If {l}=0",
        "Then",
        "0→F",
        "Else",
        f"1/{l}→F",
        "End",
        f"{{1,0}}→{L3}",
        f"{{{c},E,F}}→{L4}",
    ]
    return [
        f"If {typ}=1",
        "Then",
        *series,
        "Else",
        *parallel,
        "End",
        *_strip(L3, L5),
        *_strip(L4, L5),
        *_cancel(L3, L4, L5, L6),
    ]


def _poly_text(src):
    """Str0 becomes the polynomial text of src. Uses Str1 for one term."""
    return [
        "0→Q",
        f"For(I,1,dim({src}))",
        f"If {src}(I)≠0",
        "Then",
        f"{src}(I)",
        "prgmZS",
        f"dim({src})-I→P",
        "If P=0",
        "Str9→Str1",
        "If P=1",
        'Str9+"*s"→Str1',
        "If P=2",
        'Str9+"*s²"→Str1',
        "If P>2",
        'Str9+"*s^"+toString(P)→Str1',
        "If Q=0",
        "Then",
        "Str1→Str0",
        "Else",
        'Str0+"+"+Str1→Str0',
        "End",
        "Q+1→Q",
        "End",
        "End",
        "If Q=0",
        '"0"→Str0',
    ]


def _show_frac(prefix, num, den):
    return [
        *_poly_text(num),
        "Str0→Str2",
        *_poly_text(den),
        f'"{prefix}("+Str2+")/("+Str0+")"→Str0',
        "prgmZP",
    ]


def _report():
    """N(s), D(s), DC gain and poles from the normalized L₁, L₂."""
    return [
        *_poly_text(L1),
        '"N(s)="+Str0→Str0',
        "prgmZP",
        *_poly_text(L2),
        '"D(s)="+Str0→Str0',
        "prgmZP",
        f"If {L2}(dim({L2}))=0",
        "Then",
        '"DC GAIN: POLE AT s=0"→Str0',
        "prgmZP",
        "Else",
        f"{L1}(dim({L1}))/{L2}(dim({L2}))",
        "prgmZF",
        '"DC GAIN="+Str9→Str0',
        "prgmZP",
        "End",
        f"If dim({L2})=2",
        "Then",
        f"⁻{L2}(2)",
        "prgmZC",
        '"POLE="+Str9→Str0',
        "prgmZP",
        "Else",
        f"If dim({L2})=3",
        "Then",
        f"{L2}(dim({L2}))→E",
        f"{L2}(dim({L2})-1)→F",
        "√(E)",
        "prgmZF",
        '"w0="+Str9+" rad/s"→Str0',
        "prgmZP",
        "√(E)/F",
        "prgmZF",
        '"Q="+Str9→Str0',
        "prgmZP",
        "(⁻F+√(F²-4*E))/2",
        "prgmZC",
        '"p1="+Str9→Str0',
        "prgmZP",
        "(⁻F-√(F²-4*E))/2",
        "prgmZC",
        '"p2="+Str9→Str0',
        "prgmZP",
        "Else",
        f"If dim({L2})>3",
        "Then",
        f'"ORDER "+toString(dim({L2})-1)+": USE PLYSMLT2"→Str0',
        "prgmZP",
        "End",
        "End",
        "End",
    ]


def _combine_div():
    return [*_mul(L3, L2, L5), *_mul(L1, L4, L6), *_add(L6, L5, L3)]


def _combine_inv():
    return [*_mul(L3, L2, L5), *_neg(L5), *_mul(L4, L1, L6), *_copy(L6, L3)]


def _combine_non():
    return [
        *_mul(L1, L4, L6),
        *_mul(L3, L2, L5),
        *_add(L6, L5, L3),
        *_copy(L3, L5),
        *_copy(L6, L3),
    ]


def _build_h(kind, show):
    """kind: div or amp. show prints the work lines and leaves L₁, L₂ normalized."""
    z1 = "Z1=" if kind == "div" else "ZIN="
    z2 = "Z2=" if kind == "div" else "ZF="
    lines = [*_arm("T", "R", "L", "C")]
    if show:
        lines += _show_frac(z1, L3, L4)
    lines += [*_copy(L3, L1), *_copy(L4, L2), *_arm("U", "S", "M", "D")]
    if show:
        lines += _show_frac(z2, L3, L4)
        if kind == "div":
            lines += ['"H=Z2/(Z1+Z2)"→Str0', "prgmZP"]
        else:
            lines += [
                "If A=2",
                "Then",
                '"H=1+ZF/ZIN"→Str0',
                "Else",
                '"H=-ZF/ZIN"→Str0',
                "End",
                "prgmZP",
            ]
    if kind == "div":
        lines += _combine_div()
    else:
        lines += [
            "If A=2",
            "Then",
            *_combine_non(),
            "Else",
            *_combine_inv(),
            "End",
        ]
    lines += [*_strip(L5, L6), *_strip(L3, L6), *_cancel(L5, L3, L6, L4)]
    if show:
        lines += _show_frac("=", L5, L3)
    lines += [
        f"{L3}(1)→G",
        f"For(I,1,dim({L5}))",
        f"{L5}(I)/G→{L5}(I)",
        "End",
        f"For(I,1,dim({L3}))",
        f"{L3}(I)/G→{L3}(I)",
        "End",
        *_copy(L3, L2),
        *_copy(L5, L1),
    ]
    if show:
        lines += ["G", "prgmZF", '"DIVIDE TOP AND BOTTOM BY "+Str9→Str0', "prgmZP"]
    return lines


_H_WRITES = ("I", "J", "K", "E", "F", "G", "W", "P", "Q", "N", "Str1", "Str2", L1, L2, L3, L4, L5, L6)


def _h_tool(kind, tool_id, label, title, picture, guards):
    return Tool(
        id=tool_id,
        label=label,
        title=title,
        picture=picture,
        inputs=(
            Input("A", "AMP 1/2="),
            Input("T", "ZIN TYPE="),
            Input("R", "ZIN R Ω="),
            Input("L", "ZIN L H="),
            Input("C", "ZIN C F="),
            Input("U", "ZF TYPE="),
            Input("S", "ZF R Ω="),
            Input("M", "ZF L H="),
            Input("D", "ZF C F="),
        ) if kind != "div" else (
            Input("T", "Z1 TYPE="),
            Input("R", "Z1 R Ω="),
            Input("L", "Z1 L H="),
            Input("C", "Z1 C F="),
            Input("U", "Z2 TYPE="),
            Input("S", "Z2 R Ω="),
            Input("M", "Z2 L H="),
            Input("D", "Z2 C F="),
        ),
        steps=(
            *guards,
            Raw(writes=_H_WRITES, compute=tuple(_build_h(kind, False)), answers=tuple(_report()), work=tuple(_build_h(kind, True) + _report() + ['"SAVED: L1=TOP, L2=BOTTOM"→Str0', "prgmZP"])),
        ),
        answers=(),
    )


hdiv = _h_tool(
    "div",
    "hdiv",
    "H(s) Z DIVIDER",
    "H(s) OF A Z DIVIDER",
    (
        "VIN > Z1 > VOUT > Z2 > GND",
        "EACH Z IS R, L, C:",
        " TYPE 1 = IN SERIES",
        " TYPE 2 = IN PARALLEL",
        "0 = PART NOT THERE",
        "SAVES L1=TOP, L2=BOTTOM",
    ),
    (
        Guard("(T≠1 and T≠2) or (U≠1 and U≠2)", ("TYPE MUST BE 1 OR 2",)),
        Guard("R=0 and L=0 and C=0", ("Z1 HAS NO PARTS",)),
        Guard("S=0 and M=0 and D=0", ("Z2 HAS NO PARTS",)),
    ),
)

hopamp = _h_tool(
    "amp",
    "hopamp",
    "H(s) OP AMP",
    "H(s) OF AN OP AMP STAGE",
    (
        "ZF FROM (-) TO VOUT",
        "AMP 1 INV: VIN>ZIN>(-)",
        "AMP 2 NON-INV: VIN>(+),",
        " ZIN FROM (-) TO GND",
        "EACH Z: 1=SERIES 2=PAR",
        "0 = PART NOT THERE",
    ),
    (
        Guard("A≠1 and A≠2", ("AMP MUST BE 1 OR 2",)),
        Guard("(T≠1 and T≠2) or (U≠1 and U≠2)", ("TYPE MUST BE 1 OR 2",)),
        Guard("R=0 and L=0 and C=0", ("ZIN HAS NO PARTS",)),
        Guard("S=0 and M=0 and D=0", ("ZF HAS NO PARTS",)),
    ),
)

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

bode = Tool(
    id="bode",
    label="BODE LINES",
    title="STRAIGHT-LINE BODE PLOT",
    picture=(
        "H=K0(1+s/z)../(1+s/p)..",
        " AND 1/s^N (N POLES AT 0)",
        "CORNERS z, p IN rad/s",
        "NO ZEROS OR POLES: {0}",
    ),
    inputs=(
        Input("K", "K0="),
        Input("N", "POLES AT 0="),
        Input("L₁", "ZEROS {..}=", "list"),
        Input("L₂", "POLES {..}=", "list"),
    ),
    steps=(
        Guard("K=0", ("K0 CANNOT BE 0",)),
        Guard("min(L₁)<0 or min(L₂)<0", ("CORNERS MUST BE > 0",)),
        Raw(
            writes=("H", "S", "C", "I", "J", "E", "T", "A", "P", "L₃", "L₄", "L₅", "L₆"),
            compute=(
                "20*log(abs(K))→H",
                "⁻20*N→S",
                "0→C",
                "For(I,1,dim(L₁))",
                "If L₁(I)≠0",
                "C+1→C",
                "End",
                "For(I,1,dim(L₂))",
                "If L₂(I)≠0",
                "C+1→C",
                "End",
                "If C>0",
                "Then",
                "seq(0,E,1,C)→L₃",
                "seq(0,E,1,C)→L₄",
                "0→J",
                "For(I,1,dim(L₁))",
                "If L₁(I)≠0",
                "Then",
                "J+1→J",
                "L₁(I)→L₃(J)",
                "20→L₄(J)",
                "End",
                "End",
                "For(I,1,dim(L₂))",
                "If L₂(I)≠0",
                "Then",
                "J+1→J",
                "L₂(I)→L₃(J)",
                "⁻20→L₄(J)",
                "End",
                "End",
                "For(I,1,C-1)",
                "For(J,I+1,C)",
                "If L₃(J)<L₃(I)",
                "Then",
                "L₃(I)→T",
                "L₃(J)→L₃(I)",
                "T→L₃(J)",
                "L₄(I)→T",
                "L₄(J)→L₄(I)",
                "T→L₄(J)",
                "End",
                "End",
                "End",
                "{L₃(1)}→L₅",
                "{L₄(1)}→L₆",
                "For(I,2,C)",
                "If L₃(I)=L₅(dim(L₅))",
                "Then",
                "L₆(dim(L₆))+L₄(I)→L₆(dim(L₆))",
                "Else",
                "L₃(I)→L₅(dim(L₅)+1)",
                "L₄(I)→L₆(dim(L₆)+1)",
                "End",
                "End",
                "End",
            ),
            answers=(
                "S",
                "prgmZR",
                '"LOW F SLOPE="+Str9+" dB/DEC"→Str0',
                "prgmZP",
                "H",
                "prgmZR",
                '"20*LOG|K0|="+Str9+" dB"→Str0',
                "prgmZP",
                "If C>0",
                "Then",
                "H→A",
                "S→P",
                "For(I,1,dim(L₅))",
                "If I=1",
                "Then",
                "A+P*log(L₅(1))→A",
                "Else",
                "A+P*log(L₅(I)/L₅(I-1))→A",
                "End",
                "P+L₆(I)→P",
                "L₅(I)",
                "prgmZF",
                '"w="+Str9+": "→Str0',
                "A",
                "prgmZR",
                'Str0+Str9+" dB, THEN "→Str0',
                "P",
                "prgmZR",
                "Str0+Str9→Str0",
                "prgmZP",
                "End",
                "End",
            ),
            work=(
                '"LOW F: 20*LOG|K0|+SLOPE*LOG(w)"→Str0',
                "prgmZP",
                "H",
                "prgmZR",
                '"20*LOG|K0|="+Str9+" dB, SLOPE "→Str0',
                "S",
                "prgmZR",
                "Str0+Str9→Str0",
                "prgmZP",
                "If C>0",
                "Then",
                "H→A",
                "S→P",
                "For(I,1,dim(L₅))",
                "L₅(I)",
                "prgmZF",
                '"w="+Str9+": SLOPE CHANGE "→Str0',
                "L₆(I)",
                "prgmZR",
                "Str0+Str9→Str0",
                "prgmZP",
                "A",
                "prgmZR",
                '"="+Str9+"+"→Str0',
                "P",
                "prgmZR",
                'Str0+"("+Str9+")*LOG("→Str0',
                "If I=1",
                "Then",
                "L₅(1)",
                "prgmZF",
                'Str0+Str9+")"→Str0',
                "A+P*log(L₅(1))→A",
                "Else",
                "L₅(I)",
                "prgmZF",
                'Str0+Str9+"/"→Str0',
                "L₅(I-1)",
                "prgmZF",
                'Str0+Str9+")"→Str0',
                "A+P*log(L₅(I)/L₅(I-1))→A",
                "End",
                "prgmZP",
                "P+L₆(I)→P",
                "A",
                "prgmZR",
                '"="+Str9+" dB, SLOPE NOW "→Str0',
                "P",
                "prgmZR",
                "Str0+Str9→Str0",
                "prgmZP",
                "End",
                "End",
            ),
        ),
    ),
    answers=(),
)

ends = Tool(
    id="ends",
    label="START AND END",
    title="STEP START AND END VALUES",
    picture=(
        "STEP OF SIZE V INTO H(s)",
        "H AS LISTS, HIGHEST POWER",
        "FIRST (L1 TOP, L2 BOTTOM)",
        "ONLY FOR A STABLE H(s)",
    ),
    inputs=(
        Input("L₁", "N {..}=", "list"),
        Input("L₂", "D {..}=", "list"),
        Input("V", "STEP V="),
    ),
    steps=(
        Guard("dim(L₁)>dim(L₂)", ("IMPROPER H(s)",)),
        Guard("L₂(dim(L₂))=0", ("POLE AT s=0:", "NO FINAL VALUE")),
        Calc("S", "y(0+)", "V*LEAD N/LEAD D IF SAME ORDER", "V*(dim(L₁)=dim(L₂))*L₁(1)/L₂(1)", "", "si", False),
        Calc("E", "y(INF)", "V*N(0)/D(0)", "V*L₁(dim(L₁))/L₂(dim(L₂))", "", "si", False),
        Note("FROM s*Y(s) AT s=0 AND s=INF"),
    ),
    answers=("y(0+)", "y(INF)"),
)

pfrac = Tool(
    id="pfrac",
    label="PARTIAL FRAC",
    title="PARTIAL FRACTIONS",
    picture=(
        "F(s)=N(s)/((s-p1)(s-p2)..)",
        "DENOMINATOR STARTS AT 1s^n",
        "ONE DOUBLE POLE ALLOWED",
        "STEP INPUT: ADD POLE 0",
        "POLES LIKE {0,-2,-1+3i}",
    ),
    inputs=(
        Input("L₁", "N {..}=", "list"),
        Input("L₂", "POLES {..}=", "list"),
    ),
    steps=(
        Raw(
            writes=("R", "D", "I", "J", "O", "V", "W"),
            compute=(
                "dim(L₂)→D",
                "0→R",
                "0→O",
                "For(I,1,D)",
                "0→W",
                "For(J,1,D)",
                "If L₂(I)=L₂(J)",
                "W+1→W",
                "End",
                "If W>2",
                "1→R",
                "If W=2",
                "Then",
                "1→V",
                "If I>1",
                "Then",
                "For(J,1,I-1)",
                "If L₂(J)=L₂(I)",
                "0→V",
                "End",
                "End",
                "O+V→O",
                "End",
                "End",
                "If O>1",
                "1→R",
            ),
            answers=(),
            work=(),
        ),
        Guard("dim(L₁)>dim(L₂)", ("IMPROPER: DEG N ≥ DEG D", "DIVIDE FIRST")),
        Guard("R", ("REPEATED POLES:", "ONLY ONE DOUBLE POLE")),
        Raw(
            writes=("K", "P", "A", "B", "L₃", "C", "E", "X", "F", "G", "H", "Y", "Z", "L₄", "L₅", "M"),
            compute=(
                "seq(0,I,1,D)→L₃",
                "0→X",
                "0→F",
                "0→G",
                "For(I,1,D)",
                "0→C",
                "For(J,1,D)",
                "If L₂(I)=L₂(J)",
                "C+1→C",
                "End",
                "If C=2 and not(X)",
                "Then",
                "1→H",
                "If I>1",
                "Then",
                "For(J,1,I-1)",
                "If L₂(J)=L₂(I)",
                "0→H",
                "End",
                "End",
                "If H",
                "Then",
                "1→X",
                "I→F",
                "L₂(I)→P",
                "For(J,I+1,D)",
                "If L₂(J)=L₂(I)",
                "J→G",
                "End",
                "End",
                "End",
                "End",
                "If X",
                "Then",
                "{1}→L₄",
                "For(J,1,D)",
                "If J≠F and J≠G",
                "Then",
                "dim(L₄)+1→M",
                "seq(0,K,1,M)→L₅",
                "For(I,1,dim(L₄))",
                "L₅(I)+L₄(I)→L₅(I)",
                "L₅(I+1)-L₂(J)*L₄(I)→L₅(I+1)",
                "End",
                "seq(L₅(K),K,1,dim(L₅))→L₄",
                "End",
                "End",
                "0→Y",
                "For(K,1,dim(L₁))",
                "Y*P+L₁(K)→Y",
                "End",
                "0→Z",
                "For(K,1,dim(L₄))",
                "Z*P+L₄(K)→Z",
                "End",
                "Y/Z→L₃(G)",
                "If dim(L₁)=1",
                "Then",
                "0→E",
                "Else",
                "0→E",
                "For(K,1,dim(L₁)-1)",
                "E*P+(dim(L₁)-K)*L₁(K)→E",
                "End",
                "End",
                "If dim(L₄)=1",
                "Then",
                "0→M",
                "Else",
                "0→M",
                "For(K,1,dim(L₄)-1)",
                "M*P+(dim(L₄)-K)*L₄(K)→M",
                "End",
                "End",
                "(E-L₃(G)*M)/Z→L₃(F)",
                "End",
                "For(I,1,D)",
                "If not(X) or (I≠F and I≠G)",
                "Then",
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
                "End",
            ),
            answers=(
                "For(I,1,D)",
                "L₃(I)",
                "prgmZC",
                '"K"+toString(I)+"="+Str9→Str0',
                "If X and I=F",
                'Str0+" OVER (s-p)"→Str0',
                "If X and I=G",
                'Str0+" OVER (s-p)²"→Str0',
                "prgmZP",
                "End",
            ),
            work=(
                "For(I,1,D)",
                "If not(X and I=G)",
                "Then",
                "If X and I=F",
                "Then",
                "L₂(F)",
                "prgmZS",
                '"DOUBLE POLE AT s="+Str9→Str0',
                "prgmZP",
                '"K"+toString(G)+" OVER (s-p)²=N(p)/REST(p)"→Str0',
                "prgmZP",
                "Y",
                "prgmZS",
                '"="+Str9+"/"→Str0',
                "Z",
                "prgmZS",
                "Str0+Str9→Str0",
                "prgmZP",
                "L₃(G)",
                "prgmZC",
                '"="+Str9→Str0',
                "prgmZP",
                '"K"+toString(F)+" OVER (s-p)=(dN/ds-K"+toString(G)+"*dREST/ds)/REST"→Str0',
                "prgmZP",
                "L₃(F)",
                "prgmZC",
                '"="+Str9→Str0',
                "prgmZP",
                "L₃(G)",
                "prgmZS",
                '"TERM: "+Str9+"*t*e^("→Str0',
                "L₂(F)",
                "prgmZS",
                'Str0+Str9+"t)+"→Str0',
                "L₃(F)",
                "prgmZS",
                'Str0+Str9+"*e^("→Str0',
                "L₂(F)",
                "prgmZS",
                'Str0+Str9+"t)"→Str0',
                "prgmZP",
                "Else",
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
    tools=(hdiv, hopamp, taurc, taurl, step1, treach, srlc, prlc, quad, hjw, sine, bode, ends, pfrac),
)
