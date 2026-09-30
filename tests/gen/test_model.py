from dataclasses import replace

import pytest

from ti84.model import Calc, Case, Guard, Input, ModelError, Poly, Raw, Tool, Topic, Verdict, validate


def test_a_good_topic_validates(topic):
    validate(topic)


def check(topic, message):
    with pytest.raises(ModelError) as err:
        validate(topic)
    assert message in str(err.value)
    return str(err.value)


def with_tool(topic, **changes):
    tool = replace(topic.tools[0], **changes)
    return replace(topic, tools=(tool, *topic.tools[1:]))


@pytest.mark.parametrize("program", ["", "eetest", "EE-TEST", "TOOLONGNAME", "1EE"])
def test_program_name(topic, program):
    check(replace(topic, program=program), "program name")


def test_topic_title_fits_a_menu_item(topic):
    check(replace(topic, title="A TITLE THAT IS TOO LONG"), "topic title")


def test_tool_ids_are_unique(topic):
    check(replace(topic, tools=(topic.tools[0], topic.tools[0])), "duplicate tool id 'vdiv'")


def test_at_most_24_tools(topic):
    tools = tuple(replace(topic.tools[0], id=f"t{k}") for k in range(25))
    check(replace(topic, tools=tools), "at most 24 tools")


@pytest.mark.parametrize(
    "changes, message",
    [
        ({"label": "A LABEL TOO LONG"}, "label"),
        ({"title": "A TITLE THAT IS MUCH TOO LONG"}, "title"),
        ({"picture": tuple(f"LINE {k}" for k in range(9))}, "picture has 9 lines"),
        ({"picture": ("A PICTURE LINE THAT IS TOO WIDE",)}, "picture line"),
        ({"picture": ('SAY "HI"',)}, "contains '\"'"),
        ({"answers": ("VOUT", "NOPE")}, "answer 'NOPE' is not a step name"),
    ],
)
def test_tool_text_rules(topic, changes, message):
    check(with_tool(topic, **changes), message)


@pytest.mark.parametrize(
    "inputs, message",
    [
        ((Input("V", "A PROMPT TOO LONG="),), "prompt"),
        ((Input("v", "V="),), "input variable 'v'"),
        ((Input("θ", "T="),), "reserved"),
        ((Input("V", "V="), Input("V", "V2=")), "'V' is stored twice"),
        ((Input("L₁", "N="),), "list variable 'L₁' needs kind='list'"),
        ((Input("A", "N=", "list"),), "kind='list' needs a list variable"),
    ],
)
def test_input_rules(topic, inputs, message):
    check(with_tool(topic, inputs=inputs), message)


@pytest.mark.parametrize(
    "step, message",
    [
        (Calc("V", "X", "VS", "V*2"), "'V' is stored twice"),
        (Calc("Str1", "X", "X", "V"), "calc variable 'Str1'"),
        (Calc("X", "VOUT", "X", "V"), "duplicate step name 'VOUT'"),
        (Calc("X", "X", "X", "θ*2"), "reserved"),
        (Calc("X", "X", "X", "Str9"), "reserved"),
        (Calc("X", "X", "X", "⌊ZF(1)"), "reserved"),
        (Calc("X", "X", "X", "-V"), "'-' starts an expression"),
        (Calc("X", "X", "X", "sum(L₁)"), "sub=False"),
        (Calc("X", "|N|", "X", "V"), "is not a plain character"),
        (Calc("X", "X", "X", "V", fmt="big"), "fmt 'big'"),
        (Poly("X", "P", "P", "L₁", "V", "V"), "loop variable 'V' is also"),
        (Poly("X", "P", "P", "A", "V", "K"), "coefficient list 'A'"),
        (Verdict("Str9", "T", (Case("V>1", "BIG"),), "SMALL"), "reserved"),
        (Verdict("Str1", "T", (), "SMALL"), "needs at least one case"),
        (Guard("V=0", ()), "guard message"),
        (Guard("V=0", ("A GUARD MESSAGE THAT IS TOO WIDE",)), "guard message"),
        (Raw(writes=("θ",), compute=("1→θ",)), "reserved"),
        (Raw(writes=("V",), compute=("1→V",)), "'V' is stored twice"),
    ],
)
def test_step_rules(topic, step, message):
    tool = topic.tools[0]
    check(with_tool(topic, steps=(*tool.steps, step)), message)


def test_every_problem_is_reported_with_its_tool(topic):
    bad = with_tool(topic, label="A LABEL TOO LONG", title="A TITLE THAT IS MUCH TOO LONG")
    text = check(bad, "label")
    assert "EETEST/vdiv: label" in text
    assert "EETEST/vdiv: title" in text


def test_a_tool_needs_inputs_and_answers(topic):
    check(with_tool(topic, inputs=()), "needs at least one input")
    check(with_tool(topic, answers=()), "needs at least one answer")


def test_tool_type(topic):
    assert isinstance(topic.tools[0], Tool)
    assert isinstance(topic, Topic)


def test_menu_label_is_display_checked(topic):
    check(with_tool(topic, label="|N TOOL"), "label")


def test_topic_title_is_display_checked(topic):
    check(replace(topic, title="|N"), "topic title")


def test_topic_level_problems_name_only_the_program(topic):
    text = check(replace(topic, program="bad"), "program name")
    assert text.startswith("bad: program name")


def test_at_most_nine_guards_per_tool(topic):
    tool = topic.tools[0]
    guards = tuple(Guard("V=0", ("ZERO",)) for _ in range(10))
    check(with_tool(topic, steps=(*tool.steps, *guards)), "at most 9 guards")
