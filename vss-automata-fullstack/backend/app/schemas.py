from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class TransitionIn(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    from_: str = Field(alias="from")
    to: str
    symbol: str | None = None  # None = ε (solo AP)
    pop: str | None = None  # solo AP
    push: list[str] = Field(default_factory=list)  # solo AP; push[0] = nuevo tope


class AutomatonDef(BaseModel):
    kind: Literal["generic", "xml_tags"] = "generic"
    states: list[str] = Field(min_length=1, max_length=200)
    start: str
    accepting: list[str] = Field(default_factory=list)
    transitions: list[TransitionIn] = Field(default_factory=list, max_length=5000)
    stack_alphabet: list[str] = Field(default_factory=list)
    initial_stack: str = "Z"
    accept_by: Literal["final_state", "empty_stack"] = "final_state"
    accept_mode: Literal["end", "any"] = "end"
    accept_labels: dict[str, str] = Field(default_factory=dict)


class SimulationRequest(BaseModel):
    num_nodes: int = Field(ge=1, le=200, description="¿Número de nodos? |Q|")
    alphabet: list[str] = Field(description="¿Alfabeto a utilizar? Σ")
    string: str = Field(max_length=200_000, description="¿Cadena a analizar? w")
    method: Literal["afd", "afnd", "pda"] = Field(description="¿Método de solución?")
    automaton: AutomatonDef
    normalize: bool = Field(False, description="Minúsculas y sin acentos sobre w")


class KeywordsRequest(BaseModel):
    keywords: list[str] = Field(min_length=1, max_length=50)
    normalize: bool = True


class EdgeOut(BaseModel):
    source: str
    target: str
    label: str


class StepOut(BaseModel):
    index: int
    symbol: str | None
    active_states: list[str]
    edges: list[EdgeOut]
    stack: list[str] | None
    note: str


class MatchOut(BaseModel):
    pattern: str
    start: int | None
    end: int


class SimulationResponse(BaseModel):
    method: str
    accepted: bool
    reason: str
    steps: list[StepOut]
    matches: list[MatchOut]
    final_states: list[str]
    final_stack: list[str] | None
    error_position: int | None
