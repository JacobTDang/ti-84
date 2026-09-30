"""Run one tool on the simulated calculator the way a student would, and read back what it showed."""

from dataclasses import dataclass

from ti84.build import MAIN, all_topics, programs
from ti84.model import Tool, Topic, Verdict
from ti84.sim import Calculator, Choose, Hold, Key, Out, Prompt, Run, Value

ANSWER_FOOTER = "ENTER:WORK  CLEAR:QUIT"
DONE_FOOTER = "DONE  ENTER:MENU"
GUARD_FOOTER = "ENTER:MENU"
TOOLS_PER_PAGE = 6


class HarnessError(Exception):
    """The run did not follow the screens a tool is supposed to show."""


@dataclass
class ToolRun:
    tool: Tool
    answers: list[str]
    work: list[str]
    stopped: list[str]
    calc: Calculator
    run: Run

    def value(self, name: str):
        """The final value of the Calc, Poly or Verdict step called `name`."""
        for step in self.tool.steps:
            if getattr(step, "name", None) == name:
                if isinstance(step, Verdict):
                    return self.calc.strings[step.var]
                return self.calc.vars[step.var]
        raise KeyError(f"tool {self.tool.id!r} has no step named {name!r}")


def _find(topics: list[Topic], tool_id: str) -> tuple[Topic, int, Tool]:
    for topic in topics:
        for index, tool in enumerate(topic.tools):
            if tool.id == tool_id:
                return topic, index, tool
    raise KeyError(f"no tool with id {tool_id!r}")


def _ti_number(x: float | int) -> str:
    return repr(x).replace("e", "ᴇ").replace("-", "⁻")


def _ti_text(x) -> str:
    if isinstance(x, str):
        return x
    if isinstance(x, list):
        return "{" + ",".join(_ti_text(item) for item in x) + "}"
    if isinstance(x, (int, float)):
        return _ti_number(x)
    raise TypeError(f"can't type {x!r} on the calculator")


def _input_event(x) -> Value:
    if isinstance(x, list) and any(isinstance(item, str) for item in x):
        return Value(_ti_text(x))
    return Value(x)


def _split(tool: Tool, run: Run) -> tuple[list[str], list[str], list[str]]:
    """Answer lines, work lines and guard message lines, from the screen log after the last input."""
    last_prompt = max(i for i, entry in enumerate(run.log) if isinstance(entry, Prompt))
    outs = [entry for entry in run.log[last_prompt + 1 :] if isinstance(entry, Out)]
    footers = [out.text for out in outs if out.row == 10]
    if GUARD_FOOTER in footers:
        return [], [], [out.text for out in outs if 3 <= out.row <= 9]
    if ANSWER_FOOTER not in footers or DONE_FOOTER not in footers:
        raise HarnessError(f"{tool.id}: expected {ANSWER_FOOTER!r} then {DONE_FOOTER!r}, saw footers {footers}")

    answers, work = [], []
    section = answers
    for out in outs:
        if out.row == 10:
            if out.text == ANSWER_FOOTER:
                section = work
            elif out.text == DONE_FOOTER:
                break
            continue
        section.append(out.text)
    return answers, work, []


def run_tool(tool_id: str, inputs: list, *, topics: list[Topic] | None = None) -> ToolRun:
    topics = all_topics() if topics is None else list(topics)
    topic, index, tool = _find(topics, tool_id)
    if len(inputs) != len(tool.inputs):
        raise HarnessError(f"{tool_id} takes {len(tool.inputs)} inputs, got {len(inputs)}")

    calc = Calculator()
    for name, text in programs(topics).items():
        calc.load_text(name, text)
    events = [
        Choose(topic.title),
        *[Choose("MORE")] * (index // TOOLS_PER_PAGE),
        Choose(tool.label),
        Key("ENTER"),
        *[_input_event(x) for x in inputs],
        Hold("ENTER"),
    ]
    run = calc.run(MAIN, events, stop_at_menu=True)
    if run.stopped_at_menu != topic.title:
        raise HarnessError(f"{tool_id}: expected to end at the {topic.title} menu, ended at {run.stopped_at_menu!r}")
    answers, work, stopped = _split(tool, run)
    return ToolRun(tool, answers, work, stopped, calc, run)
