from ti84.model import Calc, Input, Tool, Topic

ohmv = Tool(
    id="ohmv",
    label="OHM: FIND V",
    title="OHMS LAW: FIND V",
    picture=(
        "V ACROSS R, I THROUGH R",
        "V = I*R",
    ),
    inputs=(
        Input("I", "I A="),
        Input("R", "R Ω="),
    ),
    steps=(
        Calc("V", "V", "I*R", "I*R", "V"),
        Calc("P", "P", "V*I", "V*I", "W"),
    ),
    answers=("V", "P"),
)

ohmi = Tool(
    id="ohmi",
    label="OHM: FIND I",
    title="OHMS LAW: FIND I",
    picture=(
        "V ACROSS R, I THROUGH R",
        "V = I*R",
    ),
    inputs=(
        Input("V", "V V="),
        Input("R", "R Ω="),
    ),
    steps=(
        Calc("I", "I", "V/R", "V/R", "A"),
        Calc("P", "P", "V*I", "V*I", "W"),
    ),
    answers=("I", "P"),
)

ohmr = Tool(
    id="ohmr",
    label="OHM: FIND R",
    title="OHMS LAW: FIND R",
    picture=(
        "V ACROSS R, I THROUGH R",
        "V = I*R",
    ),
    inputs=(
        Input("V", "V V="),
        Input("I", "I A="),
    ),
    steps=(
        Calc("R", "R", "V/I", "V/I", "Ω"),
        Calc("P", "P", "V*I", "V*I", "W"),
    ),
    answers=("R", "P"),
)

rser = Tool(
    id="rser",
    label="SERIES R",
    title="RESISTORS IN SERIES",
    picture=(
        "R1, R2, R3 END TO END",
        "SAME CURRENT IN EACH",
        "TYPE 0 FOR A MISSING R",
    ),
    inputs=(
        Input("A", "R1 Ω="),
        Input("B", "R2 Ω="),
        Input("C", "R3 Ω="),
    ),
    steps=(
        Calc("S", "RS", "R1+R2+R3", "A+B+C", "Ω"),
    ),
    answers=("RS",),
)

rpar2 = Tool(
    id="rpar2",
    label="PARALLEL 2R",
    title="TWO R IN PARALLEL",
    picture=(
        "R1 AND R2 SIDE BY SIDE",
        "SAME VOLTAGE ACROSS EACH",
        "PRODUCT OVER SUM",
    ),
    inputs=(
        Input("A", "R1 Ω="),
        Input("B", "R2 Ω="),
    ),
    steps=(
        Calc("P", "RP", "R1*R2/(R1+R2)", "A*B/(A+B)", "Ω"),
    ),
    answers=("RP",),
)

rpar3 = Tool(
    id="rpar3",
    label="PARALLEL 3R",
    title="THREE R IN PARALLEL",
    picture=(
        "R1, R2, R3 SIDE BY SIDE",
        "SAME VOLTAGE ACROSS EACH",
    ),
    inputs=(
        Input("A", "R1 Ω="),
        Input("B", "R2 Ω="),
        Input("C", "R3 Ω="),
    ),
    steps=(
        Calc("P", "RP", "1/(1/R1+1/R2+1/R3)", "1/(1/A+1/B+1/C)", "Ω"),
    ),
    answers=("RP",),
)

vdiv = Tool(
    id="vdiv",
    label="VOLT DIVIDER",
    title="VOLTAGE DIVIDER",
    picture=(
        "VS + TO TOP OF R1",
        "R1 MEETS R2 AT VOUT",
        "R2 BOTTOM TO GROUND",
        "VOUT IS ACROSS R2",
    ),
    inputs=(
        Input("V", "VS V="),
        Input("R", "R1 Ω="),
        Input("S", "R2 Ω="),
    ),
    steps=(
        Calc("O", "VOUT", "VS*R2/(R1+R2)", "V*S/(R+S)", "V"),
        Calc("I", "I", "VS/(R1+R2)", "V/(R+S)", "A"),
    ),
    answers=("VOUT", "I"),
)

idiv = Tool(
    id="idiv",
    label="CURRENT DIV",
    title="CURRENT DIVIDER",
    picture=(
        "IS SPLITS INTO R1 AND R2",
        "R1 AND R2 IN PARALLEL",
        "I1 IN R1, I2 IN R2",
    ),
    inputs=(
        Input("I", "IS A="),
        Input("R", "R1 Ω="),
        Input("S", "R2 Ω="),
    ),
    steps=(
        Calc("A", "I1", "IS*R2/(R1+R2)", "I*S/(R+S)", "A"),
        Calc("B", "I2", "IS*R1/(R1+R2)", "I*R/(R+S)", "A"),
    ),
    answers=("I1", "I2"),
)

TOPIC = Topic(
    program="EEBASIC",
    title="BASICS",
    tools=(ohmv, ohmi, ohmr, rser, rpar2, rpar3, vdiv, idiv),
)
