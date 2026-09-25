from __future__ import annotations

from dataclasses import asdict

from .engines import (ANY, DFA, NFA, PDA, AutomatonError, PDATransition, Result, normalize_text,
                      run_xml)
from .schemas import SimulationRequest


def simulate(req: SimulationRequest) -> Result:
    a = req.automaton
    if len(set(a.states)) != len(a.states):
        raise AutomatonError("Hay nombres de estado repetidos")
    if len(a.states) != req.num_nodes:
        raise AutomatonError(f"|Q| = {req.num_nodes} pero el autómata define {len(a.states)} estados")
    w = normalize_text(req.string) if req.normalize else req.string

    if a.kind == "xml_tags":
        if req.method != "pda":
            raise AutomatonError("El modo xml_tags solo aplica al Autómata de Pila")
        return run_xml(req.string)  # el XML nunca se normaliza

    sigma = set(req.alphabet)
    if any(len(s) != 1 for s in sigma):
        raise AutomatonError("Cada símbolo de Σ debe ser un único carácter")

    if req.method in ("afd", "afnd"):
        tr = []
        for t in a.transitions:
            if t.symbol is None:
                raise AutomatonError("Las transiciones ε no están soportadas en AFD/AFND")
            tr.append((t.from_, t.symbol, t.to))
        if req.method == "afd":
            return DFA(a.states, sigma, a.start, a.accepting, tr).run(w)
        return NFA(a.states, sigma, a.start, a.accepting, tr, a.accept_labels).run(w, a.accept_mode)

    ptr = [PDATransition(t.from_, t.symbol, t.pop, t.to, tuple(t.push)) for t in a.transitions]
    return PDA(a.states, sigma, a.stack_alphabet, a.start, a.initial_stack, a.accepting,
               ptr, a.accept_by).run(w)


def to_dict(r: Result) -> dict:
    return asdict(r)
