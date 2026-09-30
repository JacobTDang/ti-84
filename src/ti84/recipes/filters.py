from ti84.model import Calc, Case, Guard, Input, Note, Tool, Topic, Verdict

rclp = Tool(
    id="rclp",
    label="RC LOW-PASS",
    title="RC LOW-PASS FILTER",
    picture=(
        "VIN > R > VOUT",
        "C FROM VOUT TO GROUND",
        "H = 1/(1+jw/wc)",
    ),
    inputs=(
        Input("R", "R Ω="),
        Input("C", "C F="),
        Input("F", "F Hz="),
    ),
    steps=(
        Calc("W", "wc", "1/(R*C)", "1/(R*C)", "rad/s"),
        Calc("T", "fc", "wc/(2*PI)", "W/(2*pi)", "Hz"),
        Calc("X", "w", "2*PI*F", "2*pi*F", "rad/s"),
        Calc("G", "H", "1/(1+j*w/wc)", "1/(1+𝑖*X/W)", "", "cplx"),
        Calc("M", "|H|", "ABS(H)", "abs(G)", "V/V"),
        Calc("D", "DB", "20*LOG|H|", "20*log(M)", "dB", "fix2"),
        Calc("P", "∠H", "ANGLE(H)", "angle(G)*180/pi", "°", "fix2"),
    ),
    answers=("fc", "|H|", "DB", "∠H"),
)

rchp = Tool(
    id="rchp",
    label="RC HIGH-PASS",
    title="RC HIGH-PASS FILTER",
    picture=(
        "VIN > C > VOUT",
        "R FROM VOUT TO GROUND",
        "H = (jw/wc)/(1+jw/wc)",
    ),
    inputs=(
        Input("R", "R Ω="),
        Input("C", "C F="),
        Input("F", "F Hz="),
    ),
    steps=(
        Calc("W", "wc", "1/(R*C)", "1/(R*C)", "rad/s"),
        Calc("T", "fc", "wc/(2*PI)", "W/(2*pi)", "Hz"),
        Calc("X", "w", "2*PI*F", "2*pi*F", "rad/s"),
        Calc("G", "H", "(j*w/wc)/(1+j*w/wc)", "(𝑖*X/W)/(1+𝑖*X/W)", "", "cplx"),
        Calc("M", "|H|", "ABS(H)", "abs(G)", "V/V"),
        Calc("D", "DB", "20*LOG|H|", "20*log(M)", "dB", "fix2"),
        Calc("P", "∠H", "ANGLE(H)", "angle(G)*180/pi", "°", "fix2"),
    ),
    answers=("fc", "|H|", "DB", "∠H"),
)

rcload = Tool(
    id="rcload",
    label="LOADED RC LP",
    title="LOADED RC LOW-PASS",
    picture=(
        "VIN > R > VOUT",
        "C AND RL FROM VOUT TO GND",
        "LOAD LOWERS GAIN,",
        "RAISES CUTOFF",
    ),
    inputs=(
        Input("R", "R Ω="),
        Input("C", "C F="),
        Input("L", "RL Ω="),
    ),
    steps=(
        Calc("K", "K", "RL/(R+RL)", "L/(R+L)", "V/V"),
        Calc("W", "wc NO LOAD", "1/(R*C)", "1/(R*C)", "rad/s"),
        Calc("V", "wc LOADED", "wc/K", "W/K", "rad/s"),
        Calc("T", "fc LOADED", "wc/(2*PI)", "V/(2*pi)", "Hz"),
    ),
    answers=("K", "wc LOADED", "fc LOADED"),
)

actlp = Tool(
    id="actlp",
    label="ACTIVE INV LP",
    title="ACTIVE INVERTING LOW-PASS",
    picture=(
        "VIN > R1 > (-) INPUT",
        "R2 AND C IN PARALLEL",
        " FROM (-) TO VOUT",
        "(+) TO GROUND",
    ),
    inputs=(
        Input("R", "R1 Ω="),
        Input("F", "R2 Ω="),
        Input("C", "C F="),
        Input("X", "F Hz="),
    ),
    steps=(
        Calc("G", "G0", "-R2/R1", "⁻F/R", "V/V"),
        Calc("W", "wc", "1/(R2*C)", "1/(F*C)", "rad/s"),
        Calc("T", "fc", "wc/(2*PI)", "W/(2*pi)", "Hz"),
        Calc("Y", "w", "2*PI*F", "2*pi*X", "rad/s"),
        Calc("H", "H", "G0/(1+j*w/wc)", "G/(1+𝑖*Y/W)", "", "cplx"),
        Calc("M", "|H|", "ABS(H)", "abs(H)", "V/V"),
        Calc("D", "DB", "20*LOG|H|", "20*log(M)", "dB", "fix2"),
        Calc("P", "∠H", "ANGLE(H)", "angle(H)*180/pi", "°", "fix2"),
    ),
    answers=("G0", "fc", "|H|", "DB", "∠H"),
)

acthp = Tool(
    id="acthp",
    label="ACTIVE INV HP",
    title="ACTIVE INVERTING HIGH-PASS",
    picture=(
        "VIN > C > R1 > (-) IN",
        "R2 FROM (-) TO VOUT",
        "(+) TO GROUND",
    ),
    inputs=(
        Input("R", "R1 Ω="),
        Input("C", "C F="),
        Input("F", "R2 Ω="),
        Input("X", "F Hz="),
    ),
    steps=(
        Calc("G", "G0", "-R2/R1", "⁻F/R", "V/V"),
        Calc("W", "wc", "1/(R1*C)", "1/(R*C)", "rad/s"),
        Calc("T", "fc", "wc/(2*PI)", "W/(2*pi)", "Hz"),
        Calc("Y", "w", "2*PI*F", "2*pi*X", "rad/s"),
        Calc("H", "H", "G0*(j*w/wc)/(1+j*w/wc)", "G*(𝑖*Y/W)/(1+𝑖*Y/W)", "", "cplx"),
        Calc("M", "|H|", "ABS(H)", "abs(H)", "V/V"),
        Calc("D", "DB", "20*LOG|H|", "20*log(M)", "dB", "fix2"),
        Calc("P", "∠H", "ANGLE(H)", "angle(H)*180/pi", "°", "fix2"),
    ),
    answers=("G0", "fc", "|H|", "DB", "∠H"),
)

so2 = Tool(
    id="so2",
    label="2ND ORDER",
    title="SECOND ORDER w0 Q CUTOFFS",
    picture=(
        "D(s) = AS²+BS+C",
        "G0 = PASSBAND GAIN",
        "GIVES LP/HP CUTOFF AND",
        "BP EDGES + BANDWIDTH",
    ),
    inputs=(
        Input("A", "A="),
        Input("B", "B="),
        Input("C", "C="),
        Input("G", "G0="),
    ),
    steps=(
        Calc("W", "w0", "SQRT(C/A)", "√(C/A)", "rad/s"),
        Calc("F", "f0", "w0/(2*PI)", "W/(2*pi)", "Hz"),
        Calc("Q", "Q", "SQRT(A*C)/B", "√(A*C)/B", ""),
        Calc("P", "|HLP(jw0)|", "Q*G0", "Q*G", "V/V"),
        Calc("X", "wc LP", "w0*SQRT(1-1/(2Q²)+SQRT(1+(1-1/(2Q²))²))", "W*√(1-1/(2*Q²)+√(1+(1-1/(2*Q²))²))", "rad/s"),
        Calc("U", "wc HP", "w0²/wc LP", "W²/X", "rad/s"),
        Calc("L", "wL BP", "w0*SQRT(1+1/(4Q²))-w0/(2Q)", "W*√(1+1/(4*Q²))-W/(2*Q)", "rad/s"),
        Calc("H", "wH BP", "w0*SQRT(1+1/(4Q²))+w0/(2Q)", "W*√(1+1/(4*Q²))+W/(2*Q)", "rad/s"),
        Calc("D", "BW", "w0/Q", "W/Q", "rad/s"),
    ),
    answers=("w0", "Q", "wc LP", "wc HP", "BW"),
)

sklpa = Tool(
    id="sklpa",
    label="SK LP ANALYZE",
    title="SALLEN-KEY LOW-PASS",
    picture=(
        "VIN>R1>VX>R2>(+)",
        "C1 FROM VX TO VOUT",
        "C2 FROM (+) TO GROUND",
        "FOLLOWER: VOUT = V+",
    ),
    inputs=(
        Input("R", "R1 Ω="),
        Input("S", "R2 Ω="),
        Input("C", "C1 F="),
        Input("D", "C2 F="),
    ),
    steps=(
        Calc("M", "m", "R1/R2", "R/S", ""),
        Calc("N", "n", "C1/C2", "C/D", ""),
        Calc("W", "w0", "1/SQRT(R1R2C1C2)", "1/√(R*S*C*D)", "rad/s"),
        Calc("F", "f0", "w0/(2*PI)", "W/(2*pi)", "Hz"),
        Calc("Q", "Q", "SQRT(mn)/(m+1)", "√(M*N)/(M+1)", ""),
    ),
    answers=("w0", "f0", "Q"),
)

sklpd = Tool(
    id="sklpd",
    label="SK LP DESIGN",
    title="DESIGN SALLEN-KEY LOW-PASS",
    picture=(
        "R2=R, R1=mR, C2=C, C1=nC",
        "PICK C AND n (n ≥ 4Q²)",
        "F0 IS w0/(2PI); FOR",
        "Q=0.707 FC = F0",
    ),
    inputs=(
        Input("F", "F0 Hz="),
        Input("Q", "Q="),
        Input("C", "C2 F="),
        Input("N", "n=C1/C2="),
    ),
    steps=(
        Guard("N<4*Q²", ("n TOO SMALL:", "NEED n ≥ 4Q²")),
        Calc("W", "w0", "2*PI*F0", "2*pi*F", "rad/s"),
        Calc("K", "k", "n/(2Q²)-1", "N/(2*Q²)-1", ""),
        Calc("M", "m", "k+SQRT(k²-1)", "K+√(K²-1)", ""),
        Calc("S", "R2", "1/(w0*C*SQRT(mn))", "1/(W*C*√(M*N))", "Ω"),
        Calc("R", "R1", "m*R2", "M*S", "Ω"),
        Calc("D", "C1", "n*C", "N*C", "F"),
    ),
    answers=("R1", "R2", "C1", "m"),
)

skhpa = Tool(
    id="skhpa",
    label="SK HP ANALYZE",
    title="SALLEN-KEY HIGH-PASS",
    picture=(
        "VIN>C1>VX>C2>(+)",
        "R1 FROM VX TO VOUT",
        "R2 FROM (+) TO GROUND",
        "FOLLOWER: VOUT = V+",
    ),
    inputs=(
        Input("C", "C1 F="),
        Input("D", "C2 F="),
        Input("R", "R1 Ω="),
        Input("S", "R2 Ω="),
    ),
    steps=(
        Calc("M", "m", "R1/R2", "R/S", ""),
        Calc("N", "n", "C1/C2", "C/D", ""),
        Calc("W", "w0", "1/SQRT(R1R2C1C2)", "1/√(R*S*C*D)", "rad/s"),
        Calc("F", "f0", "w0/(2*PI)", "W/(2*pi)", "Hz"),
        Calc("Q", "Q", "SQRT(n/m)/(n+1)", "√(N/M)/(N+1)", ""),
    ),
    answers=("w0", "f0", "Q"),
)

skhpd = Tool(
    id="skhpd",
    label="SK HP DESIGN",
    title="DESIGN SALLEN-KEY HP",
    picture=(
        "EQUAL CAPACITORS C1=C2=C",
        "m = R1/R2 = 1/(4Q²)",
    ),
    inputs=(
        Input("F", "F0 Hz="),
        Input("Q", "Q="),
        Input("C", "C F="),
    ),
    steps=(
        Calc("W", "w0", "2*PI*F0", "2*pi*F", "rad/s"),
        Calc("M", "m", "1/(4Q²)", "1/(4*Q²)", ""),
        Calc("S", "R2", "1/(w0*C*SQRT(m))", "1/(W*C*√(M))", "Ω"),
        Calc("R", "R1", "m*R2", "M*S", "Ω"),
    ),
    answers=("R1", "R2", "m"),
)

ladda = Tool(
    id="ladda",
    label="RC LADDER",
    title="RC LADDER ANALYZE",
    picture=(
        "VIN>R1>V1>R2>VOUT",
        "C1 FROM V1 TO GROUND",
        "C2 FROM VOUT TO GROUND",
        "Q IS ALWAYS BELOW 0.5",
    ),
    inputs=(
        Input("R", "R1 Ω="),
        Input("C", "C1 F="),
        Input("S", "R2 Ω="),
        Input("D", "C2 F="),
    ),
    steps=(
        Calc("A", "s² COEF", "R1C1R2C2", "R*C*S*D", "s²"),
        Calc("B", "s COEF", "R1C1+C2(R1+R2)", "R*C+D*(R+S)", "s"),
        Calc("W", "w0", "1/SQRT(s² COEF)", "1/√(A)", "rad/s"),
        Calc("F", "f0", "w0/(2*PI)", "W/(2*pi)", "Hz"),
        Calc("Q", "Q", "SQRT(s² COEF)/s COEF", "√(A)/B", ""),
    ),
    answers=("w0", "f0", "Q"),
)

laddd = Tool(
    id="laddd",
    label="LADDER DESIGN",
    title="DESIGN RC LADDER",
    picture=(
        "SAME LADDER AS ANALYZE",
        "PICK R1 AND a = C1/C2",
        "MAX Q = SQRT(a/(a+1))/2",
    ),
    inputs=(
        Input("W", "w0 rad/s="),
        Input("Q", "Q="),
        Input("R", "R1 Ω="),
        Input("A", "a=C1/C2="),
    ),
    steps=(
        Guard("A-4*Q²*(A+1)<0", ("Q TOO HIGH FOR", "THIS C1/C2")),
        Calc("M", "MAX Q", "SQRT(a/(a+1))/2", "√(A/(A+1))/2", ""),
        Calc("X", "SQRT(R2/R1)", "(SQRT(a)-SQRT(a-4Q²(a+1)))/(2Q)", "(√(A)-√(A-4*Q²*(A+1)))/(2*Q)", ""),
        Calc("S", "R2", "X²*R1", "X²*R", "Ω"),
        Calc("D", "C2", "1/(w0*SQRT(R1*R2*a))", "1/(W*√(R*S*A))", "F"),
        Calc("C", "C1", "a*C2", "A*D", "F"),
    ),
    answers=("R2", "C1", "C2"),
)

mfb = Tool(
    id="mfb",
    label="MFB BANDPASS",
    title="MULTI-FEEDBACK BANDPASS",
    picture=(
        "VIN > R1 > NODE X",
        "R3 FROM X TO GROUND",
        "C1 FROM X TO (-) INPUT",
        "C2 FROM X TO VOUT",
        "R2 FROM (-) TO VOUT",
    ),
    inputs=(
        Input("R", "R1 Ω="),
        Input("S", "R2 Ω="),
        Input("T", "R3 Ω="),
        Input("C", "C1 F="),
        Input("D", "C2 F="),
    ),
    steps=(
        Calc("W", "w0", "SQRT((1+R1/R3)/(R1R2C1C2))", "√((1+R/T)/(R*S*C*D))", "rad/s"),
        Calc("F", "f0", "w0/(2*PI)", "W/(2*pi)", "Hz"),
        Calc("B", "BW", "(C1+C2)/(R2C1C2)", "(C+D)/(S*C*D)", "rad/s"),
        Calc("Q", "Q", "w0/BW", "W/B", ""),
        Calc("G", "G0", "-Q/(w0*R1*C2)", "⁻Q/(W*R*D)", "V/V"),
    ),
    answers=("w0", "f0", "Q", "BW", "G0"),
)

sv = Tool(
    id="sv",
    label="STATE-VARIABLE",
    title="STATE-VARIABLE FILTER",
    picture=(
        "SUMMER > INTEGRATOR >",
        " INTEGRATOR (R, C EACH)",
        "OUTPUTS: HP, BP, LP",
        "G3 = RF/R1",
    ),
    inputs=(
        Input("A", "R1 Ω="),
        Input("F", "RF Ω="),
        Input("B", "R2 Ω="),
        Input("D", "R3 Ω="),
        Input("R", "R Ω="),
        Input("C", "C F="),
    ),
    steps=(
        Calc("G", "G3", "RF/R1", "F/A", ""),
        Calc("W", "w0", "SQRT(G3)/(R*C)", "√(G)/(R*C)", "rad/s"),
        Calc("E", "f0", "w0/(2*PI)", "W/(2*pi)", "Hz"),
        Calc("U", "G1", "(1+RF/R1)/(1+R2/R3)", "(1+F/A)/(1+B/D)", ""),
        Calc("V", "G2", "(1+RF/R1)/(1+R3/R2)", "(1+F/A)/(1+D/B)", ""),
        Calc("Q", "Q", "SQRT(G3)/G2", "√(G)/V", ""),
        Calc("H", "HP GAIN", "G1", "U", "V/V"),
        Calc("P", "BP GAIN", "-G1/G2", "⁻U/V", "V/V"),
        Calc("L", "LP GAIN", "G1/G3", "U/G", "V/V"),
    ),
    answers=("w0", "Q", "HP GAIN", "BP GAIN", "LP GAIN"),
)

TOPIC = Topic(
    program="EEFILT",
    title="FILTERS",
    tools=(rclp, rchp, rcload, actlp, acthp, so2, sklpa, sklpd, skhpa, skhpd, ladda, laddd, mfb, sv),
)
