from typing import Sequence
from ti84.model import Topic, Calc, Poly, Note, Verdict, Guard, Raw, ModelError, validate
from ti84.tokens import encode, decode

PIECES_MAP = {
    "π": "PI",
    "√(": "SQRT(",
    "𝑖": "j",
    "⁻": "-",
    "𝑒": "e",
    "𝑒^(": "e^(",
    "abs(": "ABS(",
    "ln(": "LN(",
    "log(": "LOG(",
    "int(": "INT(",
    "round(": "ROUND(",
    "min(": "MIN(",
    "max(": "MAX(",
    "real(": "REAL(",
    "imag(": "IMAG(",
    "angle(": "ANGLE(",
    "conj(": "CONJ(",
    "sin(": "SIN(",
    "cos(": "COS(",
    "tan⁻¹(": "ATAN(",
    " and ": "AND",
    " or ": "OR",
    "not(": "NOT(",
    "⁻¹": "^-1",
}

def pieces(expr: str) -> list[tuple[str, str]]:
    tokens = decode(encode(expr))
    result = []
    text_buffer = []

    def flush():
        if text_buffer:
            result.append(("text", "".join(text_buffer)))
            text_buffer.clear()

    for t in tokens:
        if len(t.text) == 1 and "A" <= t.text <= "Z":
            flush()
            result.append(("var", t.text))
        else:
            text_buffer.append(PIECES_MAP.get(t.text, t.text))
    flush()
    return result

def gen_main(topics: Sequence[Topic]) -> str:
    if len(topics) > 6:
        raise ModelError(f"main menu: at most 6 topics fit, got {len(topics)}")
    lines = ["Lbl M"]
    menu_items = ['"EE"']
    for i, topic in enumerate(topics, 1):
        menu_items.extend([f'"{topic.title}"', str(i)])
    menu_items.extend(['"QUIT"', "Q"])
    
    lines.append(f"Menu({','.join(menu_items)})")
    for i, topic in enumerate(topics, 1):
        lines.append(f"Lbl {i}")
        lines.append(f"prgm{topic.program}")
        lines.append("Goto M")
    
    lines.extend(["Lbl Q", "ClrHome", ""])
    return "\n".join(lines)

def gen_topic(topic: Topic) -> str:
    validate(topic)
    
    lines = [
        "Radian",
        "Float",
        "Normal",
        "a+b𝑖"
    ]
    
    LETTERS = "ABCDEFGHIJKLNOPRSTUVWXYZ"
    
    tool_letter = []
    for i in range(len(topic.tools)):
        tool_letter.append(LETTERS[i])
        
    lines.append("Lbl M")
    tools = topic.tools
    page_idx = 0
    while page_idx * 6 < len(tools) or len(tools) == 0:
        if page_idx > 0:
            lines.append(f"Lbl M{page_idx}")
        
        start = page_idx * 6
        end = start + 6
        page_tools = tools[start:end]
        
        menu_args = [f'"{topic.title}"']
        for i, tool in enumerate(page_tools):
            menu_args.extend([f'"{tool.label}"', tool_letter[start + i]])
            
        if end < len(tools):
            menu_args.extend(['"MORE"', f"M{page_idx + 1}"])
        else:
            menu_args.extend(['"BACK"', "Q"])
            
        lines.append(f"Menu({','.join(menu_args)})")
        page_idx += 1
        if end >= len(tools):
            break
            
    lines.extend([
        "Lbl Q",
        "ClrHome",
        "Return"
    ])
    
    for i, tool in enumerate(topic.tools):
        guard_id = 1
        lines.append(f"Lbl {tool_letter[i]}")
        lines.append("ClrHome")
        
        lines.append(f'Output(1,1,"{tool.title}")')
        for r, pic_line in enumerate(tool.picture, 2):
            lines.append(f'Output({r},1,"{pic_line}")')
        lines.append('Output(10,1,"ENTER:GO")')
        lines.append("Pause ") # Trailing space as required
        lines.append("ClrHome")
        
        for inp in tool.inputs:
            lines.append(f'Input "{inp.prompt}",{inp.var}')
            
        tool_guards = []
        for step in tool.steps:
            if isinstance(step, Calc):
                lines.append(f"{step.expr}→{step.var}")
            elif isinstance(step, Poly):
                lines.append(f"0→{step.var}")
                lines.append(f"For({step.loop},1,dim({step.coeffs}))")
                lines.append(f"{step.var}*{step.at}+{step.coeffs}({step.loop})→{step.var}")
                lines.append("End")
            elif isinstance(step, Verdict):
                for case in step.cases:
                    lines.append(f"If {case.cond}")
                    lines.append("Then")
                    lines.append(f'"{case.text}"→{step.var}')
                    lines.append("Else")
                lines.append(f'"{step.otherwise}"→{step.var}')
                for _ in step.cases:
                    lines.append("End")
            elif isinstance(step, Guard):
                g_lbl = f"{tool_letter[i]}{guard_id}"
                tool_guards.append((g_lbl, step.message))
                lines.append(f"If {step.cond}")
                lines.append(f"Goto {g_lbl}")
                guard_id += 1
            elif isinstance(step, Raw):
                for comp in step.compute:
                    lines.append(comp)
        
        lines.append("ClrHome")
        lines.append("1→θ")
        lines.append(f'"{tool.title}"→Str0')
        lines.append("prgmZP")
        
        step_dict = {s.name: s for s in tool.steps if hasattr(s, 'name')}
        
        def fmt_helper(fmt):
            return {"si": "prgmZF", "fix2": "prgmZR", "cplx": "prgmZC"}[fmt]
            
        for ans_name in tool.answers:
            step = step_dict[ans_name]
            if isinstance(step, (Calc, Poly)):
                lines.append(step.var)
                lines.append(fmt_helper(step.fmt))
                if step.unit:
                    lines.append(f'"{step.name}="+Str9+" {step.unit}"→Str0')
                else:
                    lines.append(f'"{step.name}="+Str9→Str0')
                lines.append("prgmZP")
            elif isinstance(step, Verdict):
                lines.append(f'"{step.name}: "+{step.var}→Str0')
                lines.append("prgmZP")
                
        for step in tool.steps:
            if isinstance(step, Raw):
                lines.extend(step.answers)
                
        lines.append('"ENTER:WORK  CLEAR:QUIT"→Str0')
        lines.append("prgmZE")
        lines.append("If not(θ)")
        lines.append("Goto M")
        
        for step in tool.steps:
            if isinstance(step, Calc):
                lines.append(f'"{step.name}={step.formula}"→Str0')
                lines.append("prgmZP")
                
                p = pieces(step.expr)
                has_vars = any(kind == "var" for kind, _ in p)
                if step.sub and has_vars:
                    first = p[0]
                    if first[0] == "text":
                        lines.append(f'"={first[1]}"→Str0')
                        rest = p[1:]
                    else:
                        lines.append('"="→Str0')
                        rest = p
                    
                    for k, (kind, val) in enumerate(rest):
                        if kind == "var":
                            lines.append(val)
                            lines.append("prgmZS")
                            if k == len(rest) - 1:
                                lines.append("Str0+Str9→Str0")
                            else:
                                next_item = rest[k+1]
                                if next_item[0] == "text":
                                    lines.append(f'Str0+Str9+"{next_item[1]}"→Str0')
                                else:
                                    lines.append("Str0+Str9→Str0")
                    lines.append("prgmZP")
                    
                lines.append(step.var)
                lines.append(fmt_helper(step.fmt))
                if step.unit:
                    lines.append(f'"="+Str9+" {step.unit}"→Str0')
                else:
                    lines.append(f'"="+Str9→Str0')
                lines.append("prgmZP")
                
            elif isinstance(step, Poly):
                lines.append(f'"{step.name}={step.formula}"→Str0')
                lines.append("prgmZP")
                lines.append(step.var)
                lines.append(fmt_helper(step.fmt))
                if step.unit:
                    lines.append(f'"="+Str9+" {step.unit}"→Str0')
                else:
                    lines.append(f'"="+Str9→Str0')
                lines.append("prgmZP")
                
            elif isinstance(step, Note):
                lines.append(f'"{step.text}"→Str0')
                lines.append("prgmZP")
                
            elif isinstance(step, Verdict):
                lines.append(f'"{step.name}: "+{step.var}→Str0')
                lines.append("prgmZP")
                
            elif isinstance(step, Raw):
                lines.extend(step.work)
                
        lines.append('"DONE  ENTER:MENU"→Str0')
        lines.append("prgmZE")
        lines.append("Goto M")
        
        for g_lbl, msgs in tool_guards:
            lines.append(f"Lbl {g_lbl}")
            lines.append("ClrHome")
            lines.append(f'Output(1,1,"{tool.title}")')
            for r, msg in enumerate(msgs, 3):
                lines.append(f'Output({r},1,"{msg}")')
            lines.append('Output(10,1,"ENTER:MENU")')
            lines.append("Pause ")
            lines.append("Goto M")
            
    lines.append("")
    return "\n".join(lines)
