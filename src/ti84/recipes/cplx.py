from ti84.model import Calc, Input, Tool, Topic

r2p = Tool(
    id="r2p",
    label="RECT TO POLAR",
    title="RECTANGULAR TO POLAR",
    picture=(
        "Z = A + jB",
        "TYPE Z LIKE 3+4i",
        "(i IS 2ND . )",
    ),
    inputs=(
        Input("Z", "Z=", "complex"),
    ),
    steps=(
        Calc("A", "A", "REAL(Z)", "real(Z)", ""),
        Calc("B", "B", "IMAG(Z)", "imag(Z)", ""),
        Calc("M", "|Z|", "SQRT(A²+B²)", "√(A²+B²)", ""),
        Calc("D", "∠Z", "ANGLE(Z)*180/PI", "angle(Z)*180/pi", "°", "fix2"),
    ),
    answers=("|Z|", "∠Z"),
)

p2r = Tool(
    id="p2r",
    label="POLAR TO RECT",
    title="POLAR TO RECTANGULAR",
    picture=(
        "Z = M ∠ ANGLE",
        "ANGLE IN DEGREES",
    ),
    inputs=(
        Input("M", "|Z|="),
        Input("D", "ANGLE °="),
    ),
    steps=(
        Calc("A", "A", "M*COS(ANGLE)", "M*cos(D*pi/180)", ""),
        Calc("B", "B", "M*SIN(ANGLE)", "M*sin(D*pi/180)", ""),
        Calc("Z", "Z", "A+jB", "A+B*𝑖", "", "cplx"),
    ),
    answers=("Z",),
)

zc = Tool(
    id="zc",
    label="Z OF CAPACITOR",
    title="CAPACITOR IMPEDANCE",
    picture=(
        "ZC = 1/(jwC) = -j/(wC)",
        "BIG AT LOW F, SMALL AT HI",
    ),
    inputs=(
        Input("F", "F Hz="),
        Input("C", "C F="),
    ),
    steps=(
        Calc("W", "w", "2*PI*F", "2*pi*F", "rad/s"),
        Calc("X", "XC", "1/(w*C)", "1/(W*C)", "Ω"),
        Calc("Z", "ZC", "-j*XC", "⁻𝑖*X", "Ω", "cplx"),
    ),
    answers=("w", "XC", "ZC"),
)

zl = Tool(
    id="zl",
    label="Z OF INDUCTOR",
    title="INDUCTOR IMPEDANCE",
    picture=(
        "ZL = jwL",
        "SMALL AT LOW F, BIG AT HI",
    ),
    inputs=(
        Input("F", "F Hz="),
        Input("L", "L H="),
    ),
    steps=(
        Calc("W", "w", "2*PI*F", "2*pi*F", "rad/s"),
        Calc("X", "XL", "w*L", "W*L", "Ω"),
        Calc("Z", "ZL", "j*XL", "𝑖*X", "Ω", "cplx"),
    ),
    answers=("w", "XL", "ZL"),
)

zser = Tool(
    id="zser",
    label="SERIES Z",
    title="IMPEDANCES IN SERIES",
    picture=(
        "Z1, Z2, Z3 END TO END",
        "TYPE 0 FOR A MISSING Z",
        "TYPE Z LIKE 100-50i",
    ),
    inputs=(
        Input("A", "Z1=", "complex"),
        Input("B", "Z2=", "complex"),
        Input("C", "Z3=", "complex"),
    ),
    steps=(
        Calc("Z", "Z", "Z1+Z2+Z3", "A+B+C", "Ω", "cplx"),
        Calc("M", "|Z|", "ABS(Z)", "abs(Z)", "Ω"),
        Calc("D", "∠Z", "ANGLE(Z)", "angle(Z)*180/pi", "°", "fix2"),
    ),
    answers=("Z", "|Z|", "∠Z"),
)

zpar = Tool(
    id="zpar",
    label="PARALLEL Z",
    title="IMPEDANCES IN PARALLEL",
    picture=(
        "Z1 AND Z2 SIDE BY SIDE",
        "PRODUCT OVER SUM",
        "TYPE Z LIKE 100-50i",
    ),
    inputs=(
        Input("A", "Z1=", "complex"),
        Input("B", "Z2=", "complex"),
    ),
    steps=(
        Calc("Z", "Z", "Z1*Z2/(Z1+Z2)", "A*B/(A+B)", "Ω", "cplx"),
        Calc("M", "|Z|", "ABS(Z)", "abs(Z)", "Ω"),
        Calc("D", "∠Z", "ANGLE(Z)", "angle(Z)*180/pi", "°", "fix2"),
    ),
    answers=("Z", "|Z|", "∠Z"),
)

zrlc = Tool(
    id="zrlc",
    label="SERIES RLC Z",
    title="SERIES RLC IMPEDANCE",
    picture=(
        "R, L, C END TO END",
        "DRIVEN AT FREQUENCY F",
    ),
    inputs=(
        Input("R", "R Ω="),
        Input("L", "L H="),
        Input("C", "C F="),
        Input("F", "F Hz="),
    ),
    steps=(
        Calc("W", "w", "2*PI*F", "2*pi*F", "rad/s"),
        Calc("A", "ZL", "j*w*L", "𝑖*W*L", "Ω", "cplx"),
        Calc("B", "ZC", "-j/(w*C)", "⁻𝑖/(W*C)", "Ω", "cplx"),
        Calc("Z", "Z", "R+ZL+ZC", "R+A+B", "Ω", "cplx"),
        Calc("M", "|Z|", "ABS(Z)", "abs(Z)", "Ω"),
        Calc("D", "∠Z", "ANGLE(Z)", "angle(Z)*180/pi", "°", "fix2"),
    ),
    answers=("Z", "|Z|", "∠Z"),
)

pdiv = Tool(
    id="pdiv",
    label="PHASOR DIVIDER",
    title="PHASOR VOLTAGE DIVIDER",
    picture=(
        "VS + TO TOP OF Z1",
        "Z1 MEETS Z2 AT VOUT",
        "Z2 BOTTOM TO GROUND",
        "TYPE Z LIKE 100-50i",
    ),
    inputs=(
        Input("V", "VS=", "complex"),
        Input("A", "Z1=", "complex"),
        Input("B", "Z2=", "complex"),
    ),
    steps=(
        Calc("O", "VOUT", "VS*Z2/(Z1+Z2)", "V*B/(A+B)", "V", "cplx"),
        Calc("M", "|VOUT|", "ABS(VOUT)", "abs(O)", "V"),
        Calc("D", "∠VOUT", "ANGLE(VOUT)", "angle(O)*180/pi", "°", "fix2"),
    ),
    answers=("VOUT", "|VOUT|", "∠VOUT"),
)

TOPIC = Topic(
    program="EECPLX",
    title="COMPLEX+Z",
    tools=(r2p, p2r, zc, zl, zser, zpar, zrlc, pdiv),
)
