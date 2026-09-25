from __future__ import annotations

from typing import Iterable

from .common import AutomatonError, Edge, Result, Step


class DFA:
    """M = (Q, Σ, δ, q0, F). Transición faltante = estado sumidero implícito."""

    def __init__(self, states: Iterable[str], alphabet: Iterable[str], start: str,
                 accepting: Iterable[str], transitions: Iterable[tuple[str, str, str]]):
        self.states = frozenset(states)
        self.alphabet = frozenset(alphabet)
        self.start = start
        self.accepting = frozenset(accepting)
        if start not in self.states:
            raise AutomatonError(f"Estado inicial '{start}' no pertenece a Q")
        extra = self.accepting - self.states
        if extra:
            raise AutomatonError(f"Estados de aceptación fuera de Q: {sorted(extra)}")
        self.delta: dict[tuple[str, str], str] = {}
        for src, sym, dst in transitions:
            if src not in self.states or dst not in self.states:
                raise AutomatonError(f"Transición con estado desconocido: δ({src},{sym})={dst}")
            if sym not in self.alphabet:
                raise AutomatonError(f"Símbolo '{sym}' de δ({src},{sym}) no pertenece a Σ")
            if self.delta.get((src, sym), dst) != dst:
                raise AutomatonError(f"No determinista: δ({src},{sym}) tiene más de un destino")
            self.delta[(src, sym)] = dst

    def run(self, w: str) -> Result:
        q = self.start
        steps = [Step(0, None, [q], note="Estado inicial")]
        for i, a in enumerate(w, 1):
            if a not in self.alphabet:
                return Result("afd", False, f"El símbolo {a!r} (posición {i}) no pertenece a Σ",
                              steps, final_states=[q])
            nxt = self.delta.get((q, a))
            if nxt is None:
                steps.append(Step(i, a, [q], note=f"δ({q},{a}) no definida → sumidero"))
                return Result("afd", False, f"Sin transición desde {q} con {a!r} (posición {i})",
                              steps, final_states=[q])
            steps.append(Step(i, a, [nxt], [Edge(q, nxt, a)], note=f"δ({q},{a}) = {nxt}"))
            q = nxt
        ok = q in self.accepting
        reason = (f"Cadena consumida completa; {q} ∈ F" if ok
                  else f"Cadena consumida completa; {q} ∉ F")
        return Result("afd", ok, reason, steps, final_states=[q])
