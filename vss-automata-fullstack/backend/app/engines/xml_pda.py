from __future__ import annotations

import re

from .common import Edge, Result, Step

_NAME = r"[A-Za-z_][\w.\-]*(?::[A-Za-z_][\w.\-]*)?"
_ATTR = rf"\s+{_NAME}\s*=\s*(?:\"[^\"<]*\"|'[^'<]*')"
TOKEN_RE = re.compile(
    r"(?P<comment><!--.*?-->)"
    r"|(?P<cdata><!\[CDATA\[.*?\]\]>)"
    r"|(?P<pi><\?.*?\?>)"
    r"|(?P<doctype><!DOCTYPE[^>]*>)"
    rf"|(?P<close></(?P<cname>{_NAME})\s*>)"
    rf"|(?P<open><(?P<oname>{_NAME})(?:{_ATTR})*\s*(?P<selfclose>/)?>)"
    r"|(?P<text>[^<]+)",
    re.DOTALL,
)
_KINDS = ("comment", "cdata", "pi", "doctype", "close", "open", "text")


def run_xml(text: str) -> Result:
    """AP sobre etiquetas XML. q0: antes de la raíz · q1: dentro · q2: raíz cerrada (aceptación)."""
    stack: list[str] = []
    steps = [Step(0, None, ["q0"], stack=["Z"], note="Inicio del documento")]
    pos = 0
    root_seen = root_closed = False

    def state() -> str:
        return "q0" if not root_seen else ("q2" if root_closed else "q1")

    def fail(msg: str, at: int) -> Result:
        steps.append(Step(len(steps), None, [state()], stack=["Z", *stack], note=msg))
        return Result("pda", False, msg, steps, final_states=[state()],
                      final_stack=["Z", *stack], error_position=at)

    def add(tok: str, src: str, dst: str, label: str, note: str) -> None:
        tok = tok if len(tok) <= 80 else tok[:77] + "..."
        steps.append(Step(len(steps), tok, [dst], [Edge(src, dst, label)], ["Z", *stack], note))

    while pos < len(text):
        m = TOKEN_RE.match(text, pos)
        if not m:
            return fail(f"Token inválido o etiqueta mal formada en posición {pos}", pos)
        kind = next(k for k in _KINDS if m.group(k) is not None)
        raw = m.group(0)
        outside = (not root_seen) or root_closed
        if kind in ("text", "cdata") and outside and (kind == "cdata" or raw.strip()):
            return fail(f"Contenido fuera del elemento raíz en posición {pos}", pos)
        if kind == "open":
            name, selfclose = m.group("oname"), m.group("selfclose") is not None
            if root_closed:
                return fail(f"Múltiples elementos raíz: <{name}> en posición {pos}", pos)
            if selfclose:
                if not root_seen:
                    root_seen = root_closed = True
                    add(raw, "q0", "q2", f"<{name}/>", "Raíz vacía: sin cambios en la pila")
                else:
                    add(raw, "q1", "q1", f"<{name}/>", "Elemento vacío: sin cambios en la pila")
            else:
                src = "q1" if root_seen else "q0"
                root_seen = True
                stack.append(name)
                add(raw, src, "q1", f"<{name}>", f"PUSH {name}")
        elif kind == "close":
            name = m.group("cname")
            if not stack:
                return fail(f"Cierre </{name}> sin apertura en posición {pos}", pos)
            if stack[-1] != name:
                return fail(f"Se esperaba </{stack[-1]}> y se encontró </{name}> en posición {pos}", pos)
            stack.pop()
            if not stack:
                root_closed = True
            add(raw, "q1", state(), f"</{name}>", f"POP {name}")
        pos = m.end()

    if stack:
        return fail(f"Etiquetas sin cerrar: {' > '.join(stack)}", len(text))
    if not root_seen:
        return fail("El documento no contiene elemento raíz", len(text))
    return Result("pda", True, "Etiquetas balanceadas; pila vacía y raíz cerrada",
                  steps, final_states=["q2"], final_stack=["Z"])
