"""Generate, lint and write every calculator program: the `ti84-build` command."""

import argparse
import sys
from importlib import import_module
from pathlib import Path

from ti84.gen import gen_main, gen_topic
from ti84.model import ModelError, Topic
from ti84.tokens import LintError, lint, write_8xp

MAIN = "EE"
TOPIC_MODULES = ("basics", "cplx", "sdomain", "opamps", "filters", "util")
HELPERS = ("ZF", "ZR", "ZC", "ZS", "ZP", "ZE")
HELPER_DIR = Path(__file__).parent / "helpers"


class BuildError(Exception):
    """One or more programs broke a dialect rule; nothing was written."""


def all_topics() -> list[Topic]:
    return [import_module(f"ti84.recipes.{name}").TOPIC for name in TOPIC_MODULES]


def helper_programs() -> dict[str, str]:
    return {name: (HELPER_DIR / f"{name}.basic").read_text(encoding="utf-8") for name in HELPERS}


def programs(topics: list[Topic] | None = None) -> dict[str, str]:
    """Every program's source text, by calculator name: the main menu, each topic, each helper."""
    topics = all_topics() if topics is None else topics
    result = {MAIN: gen_main(topics)}
    for topic in topics:
        result[topic.program] = gen_topic(topic)
    result.update(helper_programs())
    return result


def build(out: Path, sources: dict[str, str] | None = None) -> list[Path]:
    sources = programs() if sources is None else sources
    problems = []
    for name, text in sources.items():
        try:
            lint(text, name)
        except LintError as err:
            problems.append(str(err))
    if problems:
        raise BuildError("\n".join(problems))

    src = out / "src"
    src.mkdir(parents=True, exist_ok=True)
    for stale in [*out.glob("*.8xp"), *src.glob("*.txt")]:
        stale.unlink()
    written = []
    for name, text in sources.items():
        path = out / f"{name}.8xp"
        write_8xp(name, text, path)
        (src / f"{name}.txt").write_text(text, encoding="utf-8")
        written.append(path)
    return written


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ti84-build", description="Write every calculator program as .8xp.")
    parser.add_argument("--out", type=Path, default=Path("dist"), help="output folder (default: dist)")
    args = parser.parse_args(argv)
    try:
        paths = build(args.out, programs())
    except (BuildError, ModelError) as err:
        print(err, file=sys.stderr)
        return 1
    print(f"wrote {len(paths)} programs to {args.out}")
    return 0
