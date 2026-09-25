from __future__ import annotations

from typing import Iterable

from .common import ANY, AutomatonError, Edge, Match, Result, Step


class NFA:
    """Simulación por conjuntos de estados activos. Soporta comodín '*' en δ."""

    def __init__(self, states: Iterable[str], alphabet: Iterable[str], start: str,
                 accepting: Iterable[str], transitions: Iterable[tuple[str, str, str]],
                 accept_labels: dict[str, str] | None = None):
        self.states = frozenset(states)
        self.alphabet = frozenset(alphabet)
        self.start = start
        self.accepting = frozenset(accepting)
        self.labels = accept_labels or {}
        if start not in self.states:
            raise AutomatonError(f"Estado inicial '{start}' no pertenece a Q")
        extra = self.accepting - self.states
        if extra:
            raise AutomatonError(f"Estados de aceptación fuera de Q: {sorted(extra)}")
        self.delta: dict[tuple[str, str], set[str]] = {}
        self.has_wildcard = False
        for src, sym, dst in transitions:
            if src not in self.states or dst not in self.states:
                raise AutomatonError(f"Transición con estado desconocido: δ({src},{sym})∋{dst}")
            if sym == ANY:
                self.has_wildcard = True
            elif sym not in self.alphabet:
                raise AutomatonError(f"Símbolo '{sym}' de δ({src},{sym}) no pertenece a Σ")
            self.delta.setdefault((src, sym), set()).add(dst)

    def _step(self, active: set[str], a: str) -> tuple[set[str], list[Edge]]:
        nxt: set[str] = set()
        edges: list[Edge] = []
        for q in sorted(active):
            for key in ((q, a), (q, ANY)):
                for p in sorted(self.delta.get(key, ())):
                    nxt.add(p)
                    edges.append(Edge(q, p, a))
        return nxt, edges

    def run(self, w: str, accept_mode: str = "end") -> Result:
        """accept_mode='end': ∃ estado final tras consumir w. 'any': ∃ coincidencia en cualquier posición."""
        active = {self.start}
        steps = [Step(0, None, sorted(active), note="Estado inicial")]
        matches: list[Match] = []

        def collect(i: int) -> None:
            for q in sorted(active & self.accepting):
                lab = self.labels.get(q)
                matches.append(Match(lab or q, (i - len(lab) + 1) if lab else None, i))

        collect(0)
        for i, a in enumerate(w, 1):
            if not self.has_wildcard and a not in self.alphabet:
                return Result("afnd", False, f"El símbolo {a!r} (posición {i}) no pertenece a Σ",
                              steps, matches, sorted(active))
            active, edges = self._step(active, a)
            if not active:
                steps.append(Step(i, a, [], note="Conjunto de estados activos vacío → rechazo"))
                return Result("afnd", False, f"Sin estados activos tras {a!r} (posición {i})",
                              steps, matches, [])
            steps.append(Step(i, a, sorted(active), edges, note=f"Activos: {{{', '.join(sorted(active))}}}"))
            collect(i)
        if accept_mode == "any":
            ok = bool(matches)
            reason = f"{len(matches)} coincidencia(s) encontrada(s)" if ok else "Sin coincidencias"
        else:
            ok = bool(active & self.accepting)
            reason = ("Algún estado activo ∈ F al terminar la cadena" if ok
                      else "Ningún estado activo ∈ F al terminar la cadena")
        return Result("afnd", ok, reason, steps, matches, sorted(active))
