import re
from dataclasses import dataclass
from typing import Literal, Sequence

from ti84.tokens import display_problems, lint, LintError

Kind = Literal["real", "complex", "list"]
Fmt = Literal["si", "fix2", "cplx"]

class ModelError(ValueError):
    pass

@dataclass(frozen=True)
class Input:
    var: str
    prompt: str
    kind: Kind = "real"

@dataclass(frozen=True)
class Calc:
    var: str
    name: str
    formula: str
    expr: str
    unit: str = ""
    fmt: Fmt = "si"
    sub: bool = True

@dataclass(frozen=True)
class Poly:
    var: str
    name: str
    formula: str
    coeffs: str
    at: str
    loop: str
    unit: str = ""
    fmt: Fmt = "cplx"

@dataclass(frozen=True)
class Note:
    text: str

@dataclass(frozen=True)
class Case:
    cond: str
    text: str

@dataclass(frozen=True)
class Verdict:
    var: str
    name: str
    cases: tuple[Case, ...]
    otherwise: str

@dataclass(frozen=True)
class Guard:
    cond: str
    message: tuple[str, ...]

@dataclass(frozen=True)
class Raw:
    writes: tuple[str, ...]
    compute: tuple[str, ...] = ()
    answers: tuple[str, ...] = ()
    work: tuple[str, ...] = ()

Step = Calc | Poly | Note | Verdict | Guard | Raw

@dataclass(frozen=True)
class Tool:
    id: str
    label: str
    title: str
    picture: tuple[str, ...]
    inputs: tuple[Input, ...]
    steps: tuple[Step, ...]
    answers: tuple[str, ...]

@dataclass(frozen=True)
class Topic:
    program: str
    title: str
    tools: tuple[Tool, ...]

def validate(topic: Topic) -> None:
    problems = []

    def add_problem(tool_id: str, msg: str):
        problems.append(f"{topic.program}/{tool_id}: {msg}")

    if not re.fullmatch(r"[A-Z][A-Z0-9]{0,7}", topic.program):
        problems.append(f"{topic.program}: program name must be 1-8 uppercase letters or digits, starting with a letter")

    if len(topic.title) > 14:
        problems.append(f"{topic.program}: topic title must be <= 14 characters")
    for p in display_problems(topic.title):
        problems.append(f"{topic.program}: topic title: {p}")

    tool_ids = set()
    if len(topic.tools) > 24:
        problems.append(f"{topic.program}: at most 24 tools are allowed")

    for tool in topic.tools:
        if tool.id in tool_ids:
            problems.append(f"{topic.program}/{tool.id}: duplicate tool id '{tool.id}'")
        tool_ids.add(tool.id)

        if len(tool.label) > 14:
            add_problem(tool.id, "label must be <= 14 characters")
        if len(tool.title) > 26:
            add_problem(tool.id, "title must be <= 26 characters")

        if len(tool.picture) > 8:
            add_problem(tool.id, f"picture has {len(tool.picture)} lines, maximum is 8")
        for line in tool.picture:
            if len(line) > 26:
                add_problem(tool.id, "picture line must be <= 26 characters")

        if not tool.inputs:
            add_problem(tool.id, "needs at least one input")
        if not tool.answers and not any(isinstance(s, Raw) and s.answers for s in tool.steps):
            add_problem(tool.id, "needs at least one answer")

        for inp in tool.inputs:
            if len(inp.prompt) > 13:
                add_problem(tool.id, "prompt must be <= 13 characters")
            
            if inp.kind == "list":
                if not re.fullmatch(r"L[₁-₆]", inp.var):
                    add_problem(tool.id, f"kind='list' needs a list variable L₁-L₆, got {inp.var!r}")
            else:
                if re.fullmatch(r"L[₁-₆]", inp.var):
                    add_problem(tool.id, f"list variable '{inp.var}' needs kind='list'")
                elif not re.fullmatch(r"[A-Z]", inp.var):
                    add_problem(tool.id, f"input variable '{inp.var}' must be A-Z (real/complex)")

        stored_vars = set()
        def check_store(var):
            if var in stored_vars:
                add_problem(tool.id, f"'{var}' is stored twice")
            stored_vars.add(var)

        for inp in tool.inputs:
            check_store(inp.var)

        step_names = set()
        def check_step_name(name):
            if name in step_names:
                add_problem(tool.id, f"duplicate step name '{name}'")
            step_names.add(name)

        reserved = {"θ", "Str0", "Str8", "Str9", "⌊"}
        def check_reserved(text, desc):
            for res in reserved:
                if res in text:
                    add_problem(tool.id, f"reserved {res} found in {desc}")
                    return True
            return False

        def check_display(text, desc):
            probs = display_problems(text)
            for p in probs:
                add_problem(tool.id, f"{desc}: {p}")

        def check_lint(code, desc, allow_reserved=False):
            if not allow_reserved:
                check_reserved(code, f"code in {desc}")
            try:
                lint(code, topic.program)
            except LintError as e:
                add_problem(tool.id, f"{desc}: {e}")

        check_display(tool.label, "label")
        check_display(tool.title, "title")
        if sum(isinstance(step, Guard) for step in tool.steps) > 9:
            add_problem(tool.id, "at most 9 guards per tool")
        for i, line in enumerate(tool.picture):
            check_display(line, f"picture line {i}")

        for inp in tool.inputs:
            check_display(inp.prompt, "prompt")
            check_reserved(inp.var, "input var")
            check_reserved(inp.prompt, "prompt")

        poly_loops = []

        for step in tool.steps:
            if isinstance(step, Calc):
                check_store(step.var)
                check_step_name(step.name)
                if not check_reserved(step.var, "calc var"):
                    if not re.fullmatch(r"[A-Z]", step.var):
                        add_problem(tool.id, f"calc variable '{step.var}' must be A-Z")
                if step.fmt not in ("si", "fix2", "cplx"):
                    add_problem(tool.id, f"fmt '{step.fmt}' is invalid")
                
                check_display(step.name, "step name")
                check_display(step.formula, "formula")
                if not step.formula:
                    add_problem(tool.id, f"step {step.name!r} has an empty formula")
                if step.unit:
                    check_display(step.unit, "unit")
                
                check_lint(step.expr, "expr")
                if step.sub:
                    if re.search(r"L[₁-₆]|⌊", step.expr):
                        add_problem(tool.id, f"sub=False is required when expression contains lists")
            
            elif isinstance(step, Poly):
                check_store(step.var)
                check_step_name(step.name)
                if not check_reserved(step.var, "poly var"):
                    if not re.fullmatch(r"[A-Z]", step.var):
                        add_problem(tool.id, f"poly variable '{step.var}' must be A-Z")
                if not check_reserved(step.coeffs, "poly coeffs"):
                    if not re.fullmatch(r"L[₁-₆]", step.coeffs):
                        add_problem(tool.id, f"coefficient list '{step.coeffs}' must be L₁-L₆")
                poly_loops.append(step.loop)
                check_lint(step.at, "at")
                check_display(step.name, "step name")
                check_display(step.formula, "formula")
                if not step.formula:
                    add_problem(tool.id, f"step {step.name!r} has an empty formula")
                if step.unit:
                    check_display(step.unit, "unit")
            
            elif isinstance(step, Note):
                check_display(step.text, "note text")
            
            elif isinstance(step, Verdict):
                check_store(step.var)
                check_step_name(step.name)
                if not check_reserved(step.var, "verdict var"):
                    if not re.fullmatch(r"Str[1-7]", step.var):
                        add_problem(tool.id, f"verdict variable '{step.var}' must be Str1-Str7")
                if not step.cases:
                    add_problem(tool.id, "needs at least one case")
                check_display(step.name, "step name")
                for case in step.cases:
                    check_lint(case.cond, "case cond")
                    check_display(case.text, "case text")
                check_display(step.otherwise, "otherwise text")
            
            elif isinstance(step, Guard):
                check_lint(step.cond, "guard cond")
                if not (1 <= len(step.message) <= 3):
                    add_problem(tool.id, f"guard message must be 1-3 lines, got {len(step.message)}")
                for line in step.message:
                    if len(line) > 26:
                        add_problem(tool.id, "guard message line must be <= 26 characters")
                    check_display(line, "guard message line")
            
            elif isinstance(step, Raw):
                for w in step.writes:
                    check_store(w)
                    check_reserved(w, "raw writes")
                for code in step.compute:
                    check_lint(code, "raw compute")
                for code in step.answers:
                    check_lint(code, "raw answers", allow_reserved=True)
                for code in step.work:
                    check_lint(code, "raw work", allow_reserved=True)

        for loop in poly_loops:
            for v in stored_vars:
                if v == loop:
                    add_problem(tool.id, f"loop variable '{loop}' is also stored")
            
            for inp in tool.inputs:
                if loop == inp.var:
                    add_problem(tool.id, f"loop variable '{loop}' is also used as an input")
            for step in tool.steps:
                if isinstance(step, Calc):
                    if loop == step.var or re.search(rf"\b{loop}\b", step.expr):
                        add_problem(tool.id, f"loop variable '{loop}' is also used in calc")
                elif isinstance(step, Poly):
                    if loop == step.var or loop == step.coeffs or re.search(rf"\b{loop}\b", step.at):
                        add_problem(tool.id, f"loop variable '{loop}' is also used in poly")
                elif isinstance(step, Verdict):
                    if loop == step.var:
                        add_problem(tool.id, f"loop variable '{loop}' is also used in verdict")
                    for case in step.cases:
                        if re.search(rf"\b{loop}\b", case.cond):
                            add_problem(tool.id, f"loop variable '{loop}' is also used in verdict case")
                elif isinstance(step, Guard):
                    if re.search(rf"\b{loop}\b", step.cond):
                        add_problem(tool.id, f"loop variable '{loop}' is also used in guard")
                elif isinstance(step, Raw):
                    if loop in step.writes:
                        add_problem(tool.id, f"loop variable '{loop}' is also used in raw writes")
                    for c in step.compute:
                        if re.search(rf"\b{loop}\b", c):
                            add_problem(tool.id, f"loop variable '{loop}' is also used in raw compute")

        for ans in tool.answers:
            if ans not in step_names:
                add_problem(tool.id, f"answer '{ans}' is not a step name")

    if problems:
        raise ModelError("\n".join(problems))
