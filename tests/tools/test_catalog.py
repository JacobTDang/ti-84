import importlib
import re
from pathlib import Path

import pytest

from ti84.gen import gen_topic
from ti84.tokens import lint

DOCS = Path(__file__).parents[2] / "docs" / "tools.md"
MODULES = {
    "EEBASIC": "basics",
    "EECPLX": "cplx",
    "EES": "sdomain",
    "EEOPAMP": "opamps",
    "EEFILT": "filters",
    "EEUTIL": "util",
}


def catalog():
    text = DOCS.read_text(encoding="utf-8")
    topics = {}
    for match in re.finditer(r"^## ([^\n]+?) · `(\w+)`[^\n]*$(.*?)(?=^## |\Z)", text, re.M | re.S):
        title, program, body = match.groups()
        tools = [
            (tool_id, label.strip(), re.sub(r" \(priority 2\)$", "", tool_title.strip()))
            for tool_id, label, tool_title in re.findall(r"^### (\S+) · (.+?) · (.+)$", body, re.M)
        ]
        topics[program] = (title.strip(), tools)
    return topics


CATALOG = catalog()


def test_catalog_lists_every_topic():
    assert list(CATALOG) == list(MODULES)


def load(program):
    return importlib.import_module(f"ti84.recipes.{MODULES[program]}").TOPIC


@pytest.mark.parametrize("program", list(MODULES))
def test_topic_matches_the_catalog(program):
    topic = load(program)
    title, tools = CATALOG[program]
    assert topic.program == program
    assert topic.title == title
    assert [(t.id, t.label, t.title) for t in topic.tools] == tools


@pytest.mark.parametrize("program", list(MODULES))
def test_topic_generates_clean_code(program):
    lint(gen_topic(load(program)), program)
