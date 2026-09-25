from __future__ import annotations

import unicodedata
from dataclasses import dataclass, field

ANY = "*"  # comodín: cualquier símbolo (solo AFND, para búsqueda de patrones)


class AutomatonError(ValueError):
    """Definición de autómata inválida."""


@dataclass
class Edge:
    source: str
    target: str
    label: str


@dataclass
class Step:
    index: int
    symbol: str | None
    active_states: list[str]
    edges: list[Edge] = field(default_factory=list)
    stack: list[str] | None = None  # base -> tope
    note: str = ""


@dataclass
class Match:
    pattern: str
    start: int | None  # 1-based
    end: int  # 1-based, inclusivo


@dataclass
class Result:
    method: str
    accepted: bool
    reason: str
    steps: list[Step]
    matches: list[Match] = field(default_factory=list)
    final_states: list[str] = field(default_factory=list)
    final_stack: list[str] | None = None
    error_position: int | None = None  # offset 0-based en la cadena (XML)


def normalize_text(s: str) -> str:
    """Minúsculas + sin acentos (conserva la longitud para textos en español)."""
    d = unicodedata.normalize("NFD", s.lower())
    return unicodedata.normalize("NFC", "".join(c for c in d if not unicodedata.combining(c)))
