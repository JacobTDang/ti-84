from ti84.model import Calc, Case, Guard, Input, Note, Tool, Topic, Verdict

inv = Tool(
    id="inv",
    label="INVERTING",
    title="INVERTING AMPLIFIER",
    picture=(
        "VIN > R1 > (-) INPUT",
        "R2 FROM (-) TO VOUT",
        "(+) INPUT TO GROUND",
        "GAIN = -R2/R1",
    ),
    inputs=(
        Input("V", "VIN V="),
        Input("R", "R1 Ω="),
        Input("F", "R2 Ω="),
        Input("P", "VCC V="),
        Input("N", "VEE V="),
    ),
    steps=(
        Calc("G", "GAIN", "-R2/R1", "⁻F/R", "V/V"),
        Calc("O", "VOUT", "GAIN*VIN", "G*V", "V"),
        Calc("H", "VOMAX", "VCC-2", "P-2", "V"),
        Calc("L", "VOMIN", "VEE+2", "N+2", "V"),
        Calc("X", "|VIN|MAX", "VLIM/|GAIN|", "min(H,abs(L))/abs(G)", "V"),
        Verdict(
            "Str1",
            "RAILS",
            (Case("O>H or O<L", "CLIPS: PAST RAILS-2V"),),
            "OK: INSIDE RAILS",
        ),
    ),
    answers=("GAIN", "VOUT", "RAILS", "|VIN|MAX"),
)

noninv = Tool(
    id="noninv",
    label="NON-INVERTING",
    title="NON-INVERTING AMPLIFIER",
    picture=(
        "VIN > (+) INPUT",
        "R2 FROM (-) TO VOUT",
        "R1 FROM (-) TO GROUND",
        "GAIN = 1+R2/R1",
    ),
    inputs=(
        Input("V", "VIN V="),
        Input("R", "R1 Ω="),
        Input("F", "R2 Ω="),
        Input("P", "VCC V="),
        Input("N", "VEE V="),
    ),
    steps=(
        Calc("G", "GAIN", "1+R2/R1", "1+F/R", "V/V"),
        Calc("O", "VOUT", "GAIN*VIN", "G*V", "V"),
        Calc("H", "VOMAX", "VCC-2", "P-2", "V"),
        Calc("L", "VOMIN", "VEE+2", "N+2", "V"),
        Calc("X", "|VIN|MAX", "VLIM/|GAIN|", "min(H,abs(L))/abs(G)", "V"),
        Verdict(
            "Str1",
            "RAILS",
            (Case("O>H or O<L", "CLIPS: PAST RAILS-2V"),),
            "OK: INSIDE RAILS",
        ),
        Note("VCM = VIN: CHECK INPUT RANGE"),
    ),
    answers=("GAIN", "VOUT", "RAILS", "|VIN|MAX"),
)


limits = Tool(
    id="limits",
    label="OUTPUT LIMITS",
    title="OUTPUT SWING LIMITS",
    picture=(
        "VOUT = GAIN*VIN UNTIL IT",
        " HITS VO MAX OR VO MIN",
        "DATASHEET VALUES, OR",
        " VCC-2 AND VEE+2",
    ),
    inputs=(
        Input("G", "GAIN V/V="),
        Input("V", "VIN V="),
        Input("H", "VO MAX V="),
        Input("L", "VO MIN V="),
    ),
    steps=(
        Calc("O", "IDEAL VOUT", "GAIN*VIN", "G*V", "V"),
        Calc("A", "ACTUAL VOUT", "CLIP TO LIMITS", "min(H,max(L,O))", "V"),
        Calc("X", "VIN AT VO MAX", "VO MAX/GAIN", "H/G", "V"),
        Calc("Y", "VIN AT VO MIN", "VO MIN/GAIN", "L/G", "V"),
        Verdict(
            "Str1",
            "CLIPS",
            (Case("O>H or O<L", "YES: OUTPUT CLIPS"),),
            "NO: INSIDE LIMITS",
        ),
    ),
    answers=("IDEAL VOUT", "ACTUAL VOUT", "CLIPS", "VIN AT VO MAX", "VIN AT VO MIN"),
)

sum3 = Tool(
    id="sum3",
    label="SUMMER",
    title="INVERTING SUMMER",
    picture=(
        "V1>R1, V2>R2, V3>R3",
        "ALL MEET AT (-) INPUT",
        "RF FROM (-) TO VOUT",
        "UNUSED INPUT: V=0, R=1",
    ),
    inputs=(
        Input("A", "V1="),
        Input("R", "R1 Ω="),
        Input("B", "V2="),
        Input("S", "R2 Ω="),
        Input("C", "V3="),
        Input("T", "R3 Ω="),
        Input("F", "RF Ω="),
    ),
    steps=(
        Calc("O", "VOUT", "-RF*(V1/R1+V2/R2+V3/R3)", "⁻F*(A/R+B/S+C/T)", "V"),
    ),
    answers=("VOUT",),
)

diff = Tool(
    id="diff",
    label="DIFFERENCE AMP",
    title="DIFFERENCE AMPLIFIER",
    picture=(
        "VA > RA > (-) INPUT",
        "RB FROM (-) TO VOUT",
        "VB > RC > (+) INPUT",
        "RD FROM (+) TO GROUND",
    ),
    inputs=(
        Input("A", "VA="),
        Input("B", "VB="),
        Input("R", "RA Ω="),
        Input("F", "RB Ω="),
        Input("S", "RC Ω="),
        Input("T", "RD Ω="),
    ),
    steps=(
        Calc("P", "V+", "VB*RD/(RC+RD)", "B*T/(S+T)", "V"),
        Calc("O", "VOUT", "V+*(1+RB/RA)-VA*RB/RA", "P*(1+F/R)-A*F/R", "V"),
        Note("RA=RC, RB=RD: RB/RA*(VB-VA)"),
    ),
    answers=("VOUT",),
)

iout = Tool(
    id="iout",
    label="OUTPUT CURRENT",
    title="OP AMP OUTPUT CURRENT",
    picture=(
        "OUTPUT FEEDS THE LOAD RL",
        "AND THE FEEDBACK RF",
        "V- = 0 FOR INVERTING",
        "V- = VIN FOR NON-INVERTING",
    ),
    inputs=(
        Input("O", "VOUT V="),
        Input("L", "RL Ω="),
        Input("F", "RF Ω="),
        Input("N", "V- V="),
    ),
    steps=(
        Calc("A", "IL", "VOUT/RL", "O/L", "A"),
        Calc("B", "IF", "(VOUT-V-)/RF", "(O-N)/F", "A"),
        Calc("I", "IO", "IL+IF", "A+B", "A"),
    ),
    answers=("IL", "IF", "IO"),
)

offset = Tool(
    id="offset",
    label="OFFSET + BIAS",
    title="OFFSET AND BIAS ERROR",
    picture=(
        "INVERTING OR NON-INV AMP",
        "R1 IN, R2 FEEDBACK",
        "R3 AT (+) CANCELS IB",
        "SIGNS UNKNOWN: ADD SIZES",
    ),
    inputs=(
        Input("V", "VOS V="),
        Input("B", "IB A="),
        Input("I", "IOS A="),
        Input("R", "R1 Ω="),
        Input("F", "R2 Ω="),
    ),
    steps=(
        Calc("G", "NOISE GAIN", "1+R2/R1", "1+F/R", "V/V"),
        Calc("E", "VO(VOS)", "|VOS|*(1+R2/R1)", "abs(V)*G", "V"),
        Calc("A", "VO(IB), NO R3", "IB*R2", "B*F", "V"),
        Calc("C", "R3", "R1*R2/(R1+R2)", "R*F/(R+F)", "Ω"),
        Calc("D", "VO(IOS), WITH R3", "IOS*R2", "I*F", "V"),
        Calc("W", "WORST, WITH R3", "VO(VOS)+VO(IOS)", "E+D", "V"),
        Calc("X", "WORST, NO R3", "VO(VOS)+VO(IB)", "E+A", "V"),
    ),
    answers=("R3", "WORST, WITH R3", "WORST, NO R3"),
)


vosm = Tool(
    id="vosm",
    label="VOS FROM VO",
    title="OFFSET FROM MEASURED VO",
    picture=(
        "INPUT GROUNDED (VS=0)",
        "VO IS THE MEASURED OUTPUT",
        "R1 IN, R2 FEEDBACK",
        "VO = VOS*(1+R2/R1)",
    ),
    inputs=(
        Input("O", "VO V="),
        Input("R", "R1 Ω="),
        Input("F", "R2 Ω="),
    ),
    steps=(
        Calc("G", "NOISE GAIN", "1+R2/R1", "1+F/R", "V/V"),
        Calc("V", "VOS", "VO/NOISE GAIN", "O/G", "V"),
    ),
    answers=("VOS",),
)


ibcap = Tool(
    id="ibcap",
    label="BIAS INTO CAP",
    title="BIAS CURRENT INTO A CAP",
    picture=(
        "(+) HAS ONLY C TO GROUND",
        "BIAS CURRENT CHARGES C",
        "IP<0: CURRENT OUT OF PIN",
        "GAIN 1+R2/R1 (NON-INV)",
    ),
    inputs=(
        Input("P", "IP A="),
        Input("N", "IN A="),
        Input("C", "C F="),
        Input("R", "R1 Ω="),
        Input("F", "R2 Ω="),
        Input("T", "t s="),
        Input("H", "VO MAX V="),
        Input("L", "VO MIN V="),
    ),
    steps=(
        Guard("P=0", ("IP=0: NO RAMP",)),
        Calc("S", "dVP/dt", "-IP/C", "⁻P/C", "V/s"),
        Calc("G", "GAIN", "1+R2/R1", "1+F/R", "V/V"),
        Calc("V", "VP(t)", "dVP/dt*t", "S*T", "V"),
        Calc("O", "VO(t)", "GAIN*VP(t)", "G*V", "V"),
        Calc("M", "LIMIT", "VO MAX IF RISING ELSE VO MIN", "(S≥0)*H+(S<0)*L", "V", "si", False),
        Calc("X", "tSAT", "LIMIT/(GAIN*dVP/dt)", "M/(G*S)", "s"),
        Calc("B", "IB", "(IP+IN)/2", "(P+N)/2", "A"),
        Calc("D", "IOS", "IP-IN", "P-N", "A"),
    ),
    answers=("VO(t)", "tSAT", "IB", "IOS"),
)

finite = Tool(
    id="finite",
    label="FINITE GAIN",
    title="FINITE OPEN-LOOP GAIN",
    picture=(
        "REAL OP AMP GAIN AOL",
        "R1 IN, R2 FEEDBACK",
    ),
    inputs=(
        Input("R", "R1 Ω="),
        Input("F", "R2 Ω="),
        Input("A", "AOL V/V="),
    ),
    steps=(
        Calc("G", "NOISE GAIN", "1+R2/R1", "1+F/R", "V/V"),
        Calc("I", "INV IDEAL", "-R2/R1", "⁻F/R", "V/V"),
        Calc("J", "INV REAL", "IDEAL/(1+NG/AOL)", "I/(1+G/A)", "V/V"),
        Calc("N", "NONINV IDEAL", "1+R2/R1", "G", "V/V"),
        Calc("M", "NONINV REAL", "NG/(1+NG/AOL)", "G/(1+G/A)", "V/V"),
        Calc("E", "ERROR", "100*(1-REAL/IDEAL)", "100*(1-J/I)", "%"),
    ),
    answers=("INV REAL", "NONINV REAL", "ERROR"),
)

gbw = Tool(
    id="gbw",
    label="GBW BANDWIDTH",
    title="GAIN-BANDWIDTH",
    picture=(
        "GBW = GAIN * BANDWIDTH",
        "USE NOISE GAIN 1+R2/R1",
        "EVEN FOR INVERTING",
        "LM324: GBW ABOUT 1.2MHz",
    ),
    inputs=(
        Input("G", "GBW Hz="),
        Input("R", "R1 Ω="),
        Input("F", "R2 Ω="),
        Input("X", "F Hz="),
    ),
    steps=(
        Calc("N", "NOISE GAIN", "1+R2/R1", "1+F/R", "V/V"),
        Calc("C", "FC", "GBW/(1+R2/R1)", "G/N", "Hz"),
        Calc("A", "AMAX AT F", "GBW/F", "G/X", "V/V"),
    ),
    answers=("FC", "AMAX AT F"),
)

slew = Tool(
    id="slew",
    label="SLEW RATE",
    title="SLEW RATE LIMIT",
    picture=(
        "VM = OUTPUT PEAK VOLTAGE",
        "SR FROM DATASHEET V/μs",
        "NEED 2PI*F*VM ≤ SR",
    ),
    inputs=(
        Input("S", "SR V/μs="),
        Input("V", "VM V="),
        Input("F", "F Hz="),
    ),
    steps=(
        Calc("R", "SR", "SR*1ᴇ6", "S*1ᴇ6", "V/s"),
        Calc("N", "NEEDED", "2*PI*F*VM", "2*pi*F*V", "V/s"),
        Calc("M", "FMAX", "SR/(2*PI*VM)", "R/(2*pi*V)", "Hz"),
        Calc("X", "VMMAX", "SR/(2*PI*F)", "R/(2*pi*F)", "V"),
        Verdict(
            "Str1",
            "SLEW",
            (Case("N≤R", "OK: NO SLEW LIMIT"),),
            "SLEW LIMITED: DISTORTS",
        ),
    ),
    answers=("SLEW", "FMAX", "VMMAX"),
)

TOPIC = Topic(
    program="EEOPAMP",
    title="OP AMPS",
    tools=(inv, noninv, limits, sum3, diff, iout, offset, vosm, ibcap, finite, gbw, slew),
)
