import pytest

from ti84 import build
from ti84.build import BuildError
from ti84.tokens import encode, read_8xp

HELLO = 'ClrHome\nOutput(1,1,"HI")\n'


def test_build_writes_8xp_and_source(tmp_path):
    paths = build.build(tmp_path, {"HELLO": HELLO, "ZZ": "1→A\n"})
    assert paths == [tmp_path / "HELLO.8xp", tmp_path / "ZZ.8xp"]
    assert read_8xp(tmp_path / "HELLO.8xp") == ("HELLO", encode(HELLO))
    assert (tmp_path / "src" / "HELLO.txt").read_text(encoding="utf-8") == HELLO


def test_build_lints_everything_first_and_writes_nothing_on_error(tmp_path):
    with pytest.raises(BuildError) as err:
        build.build(tmp_path, {"GOOD": HELLO, "BAD": "-5→A\n", "WORSE": "1E3→A\n"})
    assert "BAD:1: '-' starts an expression" in str(err.value)
    assert "WORSE:1: ASCII E after a number" in str(err.value)
    assert list(tmp_path.iterdir()) == []


def test_build_removes_programs_that_no_longer_exist(tmp_path):
    build.build(tmp_path, {"OLD": HELLO})
    build.build(tmp_path, {"NEW": HELLO})
    assert sorted(p.name for p in tmp_path.glob("*.8xp")) == ["NEW.8xp"]
    assert sorted(p.name for p in (tmp_path / "src").iterdir()) == ["NEW.txt"]


def test_main_reports_errors_and_exits_1(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(build, "programs", lambda: {"BAD": "-5→A\n"})
    assert build.main(["--out", str(tmp_path)]) == 1
    assert "BAD:1: '-' starts an expression" in capsys.readouterr().err


def test_main_writes_the_programs(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(build, "programs", lambda: {"HELLO": HELLO})
    assert build.main(["--out", str(tmp_path)]) == 0
    assert (tmp_path / "HELLO.8xp").exists()
    assert "wrote 1 programs" in capsys.readouterr().out
