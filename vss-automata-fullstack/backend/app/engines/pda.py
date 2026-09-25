from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Iterable

from .common import AutomatonError, Edge, Result, Step


@dataclass(frozen=True)
class PDATransition:
    """δ(src, symbol, pop) = (dst, push). None = ε. push[0] queda como nuevo tope."""
    src: str
    symbol: str | None
    pop: str | None
    dst: str
    push: tuple[str, ...] = ()

    def label(self) -> str:
        return f"{self.symbol or 'ε'},{self.pop or 'ε'}/{''.join(self.push) or 'ε'}"


class PDA:
    """Autómata de pila no determinista; explora configuraciones (q, i, pila) por BFS."""

    def __init__(self, states: Iterable[str], alphabet: Iterable[str], stack_alphabet: Iterable[str],
                 start: str, initial_stack: str, accepting: Iterable[str],
                 transitions: Iterable[PDATransition], accept_by: str = "final_state"):
        self.states = frozenset(states)
        self.alphabet = frozenset(alphabet)
        self.gamma = frozenset(stack_alphabet) | {initial_stack}
        self.start = start
        self.z0 = initial_stack
        self.accepting = frozenset(accepting)
        self.accept_by = accept_by
        if start not in self.states:
            raise AutomatonError(f"Estado inicial '{start}' no pertenece a Q")
        extra = self.accepting - self.states
        if extra:
            raise AutomatonError(f"Estados de aceptación fuera de Q: {sorted(extra)}")
        if accept_by not in ("final_state", "empty_stack"):
            raise AutomatonError("accept_by debe ser 'final_state' o 'empty_stack'")
        self.by_state: dict[str, list[PDATransition]] = {}
        for t in transitions:
            if t.src not in self.states or t.dst not in self.states:
                raise AutomatonError(f"Transición con estado desconocido: {t.src}→{t.dst}")
            if t.symbol is not None and t.symbol not in self.alphabet:
                raise AutomatonError(f"Símbolo '{t.symbol}' no pertenece a Σ")
            if t.pop is not None and t.pop not in self.gamma:
                raise AutomatonError(f"Símbolo de pila '{t.pop}' no pertenece a Γ")
            bad = [s for s in t.push if s not in self.gamma]
            if bad:
                raise AutomatonError(f"Símbolos de pila fuera de Γ en push: {bad}")
            self.by_state.setdefault(t.src, []).append(t)

    def _accepts(self, q: str, stack: tuple[str, ...]) -> bool:
        return q in self.accepting if self.accept_by == "final_state" else not stack

    def run(self, w: str, max_configs: int = 50_000, max_stack: int = 2_000) -> Result:
        for i, a in enumerate(w, 1):
            if a not in self.alphabet:
                return Result("pda", False, f"El símbolo {a!r} (posición {i}) no pertenece a Σ",
                              [self._initial_step()], final_states=[self.start], final_stack=[self.z0])
        n = len(w)
        init = (self.start, 0, (self.z0,))
        parent: dict = {init: None}
        queue = deque([init])
        best, truncated = init, False
        while queue:
            cfg = queue.popleft()
            q, i, stk = cfg
            if i == n and self._accepts(q, stk):
                return self._build(cfg, parent, True, "Cómputo aceptante encontrado")
            if i > best[1]:
                best = cfg
            for t in self.by_state.get(q, ()):
                if t.symbol is not None and (i >= n or w[i] != t.symbol):
                    continue
                if t.pop is not None:
                    if not stk or stk[-1] != t.pop:
                        continue
                    base = stk[:-1]
                else:
                    base = stk
                nstk = base + tuple(reversed(t.push))
                if len(nstk) > max_stack:
                    truncated = True
                    continue
                child = (t.dst, i + (t.symbol is not None), nstk)
                if child in parent:
                    continue
                if len(parent) >= max_configs:
                    truncated = True
                    continue
                parent[child] = (cfg, t)
                queue.append(child)
        q, i, stk = best
        reason = (f"Ningún cómputo acepta w; el más avanzado consumió {i}/{n} símbolos "
                  f"y quedó en {q} con pila {list(stk)}")
        if truncated:
            reason += " (exploración truncada por límite de configuraciones)"
        return self._build(best, parent, False, reason)

    def _initial_step(self) -> Step:
        return Step(0, None, [self.start], stack=[self.z0], note="Configuración inicial")

    def _build(self, cfg, parent, ok: bool, reason: str) -> Result:
        path = []
        c = cfg
        while parent[c] is not None:
            prev, t = parent[c]
            path.append((c, t))
            c = prev
        path.reverse()
        steps = [self._initial_step()]
        for k, (c, t) in enumerate(path, 1):
            steps.append(Step(k, t.symbol, [c[0]], [Edge(t.src, t.dst, t.label())], list(c[2]),
                              f"δ({t.src},{t.symbol or 'ε'},{t.pop or 'ε'}) → ({t.dst},{''.join(t.push) or 'ε'})"))
        return Result("pda", ok, reason, steps, final_states=[cfg[0]], final_stack=list(cfg[2]))
