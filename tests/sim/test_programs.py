import pytest

from ti84.sim import (
    Calculator,
    Choose,
    Clear,
    Hold,
    Key,
    MenuShown,
    Out,
    Prompt,
    SimError,
    Value,
    Wait,
)
from ti84.tokens import encode

BLANK = " " * 26


def calc_with(**programs):
    calc = Calculator()
    for name, text in programs.items():
        calc.load_text(name, text)
    return calc


def test_load_takes_token_bytes_and_load_text_encodes():
    calc = Calculator()
    calc.load("A", encode("5→X"))
    calc.load_text("B", "X+1→Y")
    calc.run("A")
    calc.run("B")
    assert calc.vars["Y"] == 6.0


def test_store_and_ans():
    calc = calc_with(P="2→A\nA*3\nAns+1→B\n")
    calc.run("P")
    assert calc.vars["A"] == 2.0
    assert calc.vars["B"] == 7.0
    assert calc.ans == 7.0


def test_store_targets():
    calc = calc_with(
        P='"HI"→Str1\n{1,2}→L₁\n5→L₁(3)\n{7}→⌊ZF\n8→⌊ZF(1)\n9→θ\n'
    )
    calc.run("P")
    assert calc.strings["Str1"] == "HI"
    assert calc.lists["L₁"] == [1.0, 2.0, 5.0]
    assert calc.lists["⌊ZF"] == [8.0]
    assert calc.vars["θ"] == 9.0


def test_store_past_end_of_list_plus_one_fails():
    calc = calc_with(P="{1,2}→L₁\n5→L₁(4)\n")
    with pytest.raises(SimError, match="ERR:INVALID DIM"):
        calc.run("P")


def test_modes():
    calc = calc_with(P="a+b𝑖\nRadian\nFloat\nNormal\n√(⁻4)→Z\n")
    calc.run("P")
    assert calc.complex_mode
    assert calc.vars["Z"] == 2j


def test_single_line_if_guards_only_the_next_statement():
    calc = calc_with(P="0→A\nIf 0\n1→A\n2→B\nIf 1:3→C\n")
    calc.run("P")
    assert calc.vars["A"] == 0.0
    assert calc.vars["B"] == 2.0
    assert calc.vars["C"] == 3.0


def test_if_then_else_end_with_nesting():
    text = (
        "5→X\n"
        "If X>3\nThen\n"
        "If X>10\nThen\n1→A\nElse\n2→A\nEnd\n"
        "Else\n3→A\nEnd\n"
        "If X<0\nThen\n9→B\nEnd\n"
    )
    calc = calc_with(P=text)
    calc.run("P")
    assert calc.vars["A"] == 2.0
    assert "B" not in calc.vars


def test_for_loop_and_repeat():
    calc = calc_with(
        P="0→S\nFor(K,1,4)\nS+K→S\nEnd\n0→N\nRepeat N≥3\nN+1→N\nEnd\nFor(J,5,1)\n99→S\nEnd\n"
    )
    calc.run("P")
    assert calc.vars["S"] == 10.0
    assert calc.vars["N"] == 3.0


def test_for_loop_with_step():
    calc = calc_with(P="0→S\nFor(K,10,1,⁻3)\nS+K→S\nEnd\n")
    calc.run("P")
    assert calc.vars["S"] == 10.0 + 7.0 + 4.0 + 1.0


def test_goto_and_lbl():
    calc = calc_with(P="0→A\nLbl A1\nA+1→A\nIf A<3\nGoto A1\nGoto Z\n99→A\nLbl Z\n")
    run = calc.run("P")
    assert calc.vars["A"] == 3.0
    assert run.leaks == 0


def test_goto_out_of_a_block_counts_a_leak():
    calc = calc_with(P="0→A\nLbl B\nA+1→A\nIf A<3\nThen\nGoto B\nEnd\n")
    run = calc.run("P")
    assert calc.vars["A"] == 3.0
    assert run.leaks == 2


def test_goto_missing_label():
    with pytest.raises(SimError, match="ERR:LABEL"):
        calc_with(P="Goto Q\n").run("P")


def test_subprogram_call_shares_variables_and_returns():
    calc = calc_with(
        MAIN="2→A\nprgmSUB\nA+100→B\n",
        SUB="A*10→A\nReturn\n999→A\n",
    )
    calc.run("MAIN")
    assert calc.vars["A"] == 20.0
    assert calc.vars["B"] == 120.0


def test_subprogram_sees_ans_from_caller():
    calc = calc_with(MAIN="7\nprgmSUB\n", SUB="Ans*2→A\n")
    calc.run("MAIN")
    assert calc.vars["A"] == 14.0


def test_stop_ends_everything():
    calc = calc_with(MAIN="prgmSUB\n1→A\n", SUB="Stop\n")
    calc.run("MAIN")
    assert "A" not in calc.vars


def test_missing_subprogram():
    with pytest.raises(SimError, match="ERR:UNDEFINED prgmNOPE"):
        calc_with(MAIN="prgmNOPE\n").run("MAIN")


def test_error_names_program_and_line():
    with pytest.raises(SimError, match=r"ERR:DIVIDE BY 0 at P:2"):
        calc_with(P="1→A\nA/0→B\n").run("P")


def test_step_limit():
    calc = Calculator(step_limit=1000)
    calc.load_text("P", "Lbl A\nGoto A\n")
    with pytest.raises(SimError, match="step limit"):
        calc.run("P")


def test_output_writes_wraps_and_truncates():
    calc = calc_with(P='ClrHome\nOutput(1,1,"HELLO")\nOutput(2,24,"ABCDEF")\nOutput(10,20,"123456789")\nOutput(5,1,12.5)\n')
    run = calc.run("P")
    assert run.screen[0] == "HELLO" + " " * 21
    assert run.screen[1] == " " * 23 + "ABC"
    assert run.screen[2] == "DEF" + " " * 23
    assert run.screen[4] == "12.5" + " " * 22
    assert run.screen[9] == " " * 19 + "1234567"
    assert run.log[:2] == [Clear(), Out(1, 1, "HELLO")]


def test_output_outside_the_screen():
    with pytest.raises(SimError, match="ERR:DOMAIN"):
        calc_with(P='Output(11,1,"X")\n').run("P")


def test_clrhome_blanks_the_screen():
    run = calc_with(P='Output(3,3,"X")\nClrHome\n').run("P")
    assert run.screen == [BLANK] * 10


def test_input_takes_values_and_text_expressions():
    calc = Calculator(complex_mode=True)
    calc.load_text("P", 'Input "R1 Ω=",R\nInput "C F=",C\nInput "Z=",Z\nInput "N {..}=",L₁\n')
    run = calc.run("P", [Value(1000), Value("10ᴇ⁻9"), Value("3+4𝑖"), Value([1, 800, 1e6])])
    assert calc.vars["R"] == 1000.0
    assert calc.vars["C"] == pytest.approx(1e-8)
    assert calc.vars["Z"] == 3 + 4j
    assert calc.lists["L₁"] == [1.0, 800.0, 1e6]
    assert run.prompts == ["R1 Ω=", "C F=", "Z=", "N {..}="]
    assert run.log[1] == Prompt("C F=", "10ᴇ⁻9")


def test_input_list_into_real_variable_fails():
    with pytest.raises(SimError, match="ERR:DATA TYPE"):
        calc_with(P='Input "R=",R\n').run("P", [Value([1, 2])])


def test_pause_waits_for_enter_and_snapshots():
    run = calc_with(P='ClrHome\nOutput(1,1,"PIC")\nPause \n1→A\n').run("P", [Key("ENTER")])
    assert run.screens[0][0].startswith("PIC")
    assert Wait("ENTER", tuple(run.screens[0])) in run.log


def test_pause_rejects_other_keys():
    with pytest.raises(SimError, match="Pause"):
        calc_with(P="Pause \n").run("P", [Key("CLEAR")])


def test_getkey_loop_idiom():
    text = "0\nRepeat max(Ans={45,105})\ngetKey\nEnd\nAns→K\n"
    calc = calc_with(P=text)
    calc.run("P", [Key("CLEAR")])
    assert calc.vars["K"] == 45.0
    calc.run("P", [Key("ENTER")])
    assert calc.vars["K"] == 105.0


def test_getkey_returns_zero_without_a_key_event():
    calc = calc_with(P="getKey→K\n")
    calc.run("P")
    assert calc.vars["K"] == 0.0


def test_waiting_for_a_key_that_never_comes_hits_the_step_limit():
    calc = Calculator(step_limit=5000)
    calc.load_text("P", "0\nRepeat Ans\ngetKey\nEnd\n")
    with pytest.raises(SimError, match="step limit"):
        calc.run("P")


def test_hold_answers_every_wait():
    text = "For(K,1,3)\nPause \nEnd\n0\nRepeat Ans=105\ngetKey\nEnd\n"
    run = calc_with(P=text).run("P", [Hold("ENTER")])
    assert sum(isinstance(e, Wait) for e in run.log) == 4


def test_menu_jumps_to_the_chosen_label():
    text = 'Menu("TOPIC","ONE",A,"TWO",B)\nLbl A\n1→X\nStop\nLbl B\n2→X\n'
    calc = calc_with(P=text)
    run = calc.run("P", [Choose("TWO")])
    assert calc.vars["X"] == 2.0
    assert run.menus == [MenuShown("TOPIC", ("ONE", "TWO"), "TWO")]


def test_menu_with_an_unknown_choice():
    with pytest.raises(SimError, match="ONE, TWO"):
        calc_with(P='Menu("T","ONE",A,"TWO",B)\nLbl A\nLbl B\n').run("P", [Choose("THREE")])


def test_menu_more_than_seven_items_fails():
    items = ",".join(f'"I{k}",A' for k in range(8))
    with pytest.raises(SimError, match="ERR:ARGUMENT"):
        calc_with(P=f'Menu("T",{items})\nLbl A\n').run("P", [Choose("I0")])


def test_stop_at_menu_ends_the_run_cleanly():
    text = 'Lbl M\nMenu("T","ONE",A)\nLbl A\n1→X\nGoto M\n'
    calc = calc_with(P=text)
    run = calc.run("P", [Choose("ONE")], stop_at_menu=True)
    assert calc.vars["X"] == 1.0
    assert run.stopped_at_menu == "T"
    assert run.menus[-1] == MenuShown("T", ("ONE",), None)


def test_wrong_event_type_fails():
    with pytest.raises(SimError, match="Input"):
        calc_with(P='Input "R=",R\n').run("P", [Key("ENTER")])


def test_running_out_of_events_for_input_fails():
    with pytest.raises(SimError, match="no event"):
        calc_with(P='Input "R=",R\n').run("P", [])


def test_unused_events_fail():
    with pytest.raises(SimError, match="unused events"):
        calc_with(P="1→A\n").run("P", [Value(1)])


def test_end_without_block_fails():
    with pytest.raises(SimError, match="End"):
        calc_with(P="1→A\nEnd\n").run("P")
