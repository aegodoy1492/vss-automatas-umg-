import pytest

from app.engines import DFA, NFA, PDA, AutomatonError, PDATransition, run_xml
from app.presets import FEL_INVALID, FEL_VALID, anbn_preset, cui_preset, keywords_preset, nit_preset


def build_dfa(p):
    a = p["automaton"]
    return DFA(a["states"], p["alphabet"], a["start"], a["accepting"],
               [(t["from"], t["symbol"], t["to"]) for t in a["transitions"]])


def build_nfa(p):
    a = p["automaton"]
    return NFA(a["states"], p["alphabet"] + ["*"], a["start"], a["accepting"],
               [(t["from"], t["symbol"], t["to"]) for t in a["transitions"]], a["accept_labels"])


def build_pda(p):
    a = p["automaton"]
    return PDA(a["states"], p["alphabet"], a["stack_alphabet"], a["start"], a["initial_stack"],
               a["accepting"], [PDATransition(t["from"], t["symbol"], t.get("pop"), t["to"],
                                              tuple(t.get("push", []))) for t in a["transitions"]])


@pytest.mark.parametrize("w,ok", [("1234567-K", True), ("5-0", True), ("1234567-8", True),
                                  ("1234567K", False), ("-5", False), ("12-", False),
                                  ("12-KK", False), ("", False), ("12a-3", False)])
def test_nit(w, ok):
    assert build_dfa(nit_preset()).run(w).accepted is ok


@pytest.mark.parametrize("w,ok", [("1924118530114", True), ("5486270650101", True),
                                  ("1924118532201", True), ("1924118530014", False),
                                  ("1924118532301", False), ("192411853011", False),
                                  ("19241185301145", False), ("19241185301a4", False)])
def test_cui(w, ok):
    assert build_dfa(cui_preset()).run(w).accepted is ok


def test_dfa_determinism_and_definition_errors():
    with pytest.raises(AutomatonError):
        DFA(["a", "b"], "x", "a", ["b"], [("a", "x", "a"), ("a", "x", "b")])
    with pytest.raises(AutomatonError):
        DFA(["a"], "x", "z", [], [])


def test_dfa_trace():
    r = build_dfa(nit_preset()).run("1-K")
    assert [s.active_states for s in r.steps] == [["q0"], ["q1"], ["q2"], ["q3"]]
    assert r.steps[1].edges[0].source == "q0"


def test_nfa_keywords():
    p = keywords_preset(["iva", "factura", "nit"])
    text = "la factura incluye el nit y el iva"
    r = build_nfa(p).run(text, "any")
    found = {(m.pattern, m.start, m.end) for m in r.matches}
    for word in ("factura", "nit", "iva"):
        s = text.index(word) + 1
        assert (word, s, s + len(word) - 1) in found
    assert r.accepted and len(r.matches) == 3
    assert not build_nfa(p).run("nada relevante", "any").accepted


def test_nfa_overlap_and_normalize():
    p = keywords_preset(["aba", "bab"])
    r = build_nfa(p).run("ababa", "any")
    assert len(r.matches) == 3
    assert keywords_preset(["ARTÍCULO"])["automaton"]["accept_labels"]
    assert list(keywords_preset(["ARTÍCULO"])["automaton"]["accept_labels"].values()) == ["articulo"]


def test_nfa_end_mode_nondeterminism():
    # (a|b)*ab
    n = NFA(["p", "q", "r"], "ab", "p", ["r"],
            [("p", "a", "p"), ("p", "b", "p"), ("p", "a", "q"), ("q", "b", "r")])
    assert n.run("bbab").accepted and not n.run("bba").accepted
    assert n.run("ab").steps[1].active_states == ["p", "q"]


@pytest.mark.parametrize("w,ok", [("ab", True), ("aaabbb", True), ("aab", False), ("abb", False),
                                  ("ba", False), ("", False)])
def test_pda_anbn(w, ok):
    assert build_pda(anbn_preset()).run(w).accepted is ok


def test_pda_trace_stack():
    r = build_pda(anbn_preset()).run("aabb")
    assert r.steps[2].stack == ["Z", "A", "A"]
    assert r.final_stack == []  # Z consumida en la transición final


def test_pda_empty_stack_mode_and_epsilon_loop_is_bounded():
    p = PDA(["q"], "a", ["A"], "q", "Z", [], [PDATransition("q", None, None, "q", ("A",))], "empty_stack")
    r = p.run("a", max_configs=200, max_stack=50)
    assert not r.accepted and "truncada" in r.reason


def test_xml_valid():
    r = run_xml(FEL_VALID)
    assert r.accepted and r.final_stack == ["Z"] and r.final_states == ["q2"]
    assert max(len(s.stack) for s in r.steps) == 5  # Z + 4 niveles de anidamiento


@pytest.mark.parametrize("doc,frag", [
    (FEL_INVALID, "Se esperaba </dte:DTE>"),
    ("<a><b></a></b>", "Se esperaba </b>"),
    ("<a><b></b>", "sin cerrar"),
    ("<a></a><b></b>", "Múltiples"),
    ("</a>", "sin apertura"),
    ("hola <a></a>", "fuera del elemento raíz"),
    ("<a></a> x", "fuera del elemento raíz"),
    ("<a><b</a>", "mal formada"),
    ("", "raíz"),
    ("<!-- solo comentario -->", "raíz"),
])
def test_xml_invalid(doc, frag):
    r = run_xml(doc)
    assert not r.accepted and frag in r.reason


def test_xml_misc_valid():
    assert run_xml("<a/>").accepted
    assert run_xml("<?xml version='1.0'?><!-- c --><a x='1'>t<b/><![CDATA[<z>]]></a>\n").accepted
