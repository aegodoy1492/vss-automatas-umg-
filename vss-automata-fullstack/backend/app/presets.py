from __future__ import annotations

from .engines import AutomatonError, normalize_text

DIGITS = list("0123456789")


def _t(src, dst, sym=None, **kw):
    return {"from": src, "to": dst, "symbol": sym, **kw}


def nit_preset() -> dict:
    """NIT: dígitos+ '-' (dígito | K)."""
    tr = [_t("q0", "q1", d) for d in DIGITS] + [_t("q1", "q1", d) for d in DIGITS]
    tr += [_t("q1", "q2", "-")] + [_t("q2", "q3", s) for s in DIGITS + ["K"]]
    return {
        "id": "nit", "name": "NIT (SAT)", "method": "afd",
        "description": "Sintaxis del NIT: uno o más dígitos, guion y dígito verificador (0-9 o K).",
        "num_nodes": 4, "alphabet": DIGITS + ["-", "K"],
        "sample_valid": "1234567-K", "sample_invalid": "1234567K",
        "automaton": {"kind": "generic", "states": ["q0", "q1", "q2", "q3"], "start": "q0",
                      "accepting": ["q3"], "transitions": tr},
    }


def cui_preset() -> dict:
    """CUI (RENAP): 8 dígitos de registro + verificador + departamento 01-22 + municipio (2 dígitos)."""
    states = [f"q{i}" for i in range(10)] + ["D0", "D1", "D2", "P", "M", "F"]
    tr = [_t(f"q{i}", f"q{i + 1}", d) for i in range(9) for d in DIGITS]
    tr += [_t("q9", "D0", "0"), _t("q9", "D1", "1"), _t("q9", "D2", "2")]
    tr += [_t("D0", "P", d) for d in DIGITS[1:]]
    tr += [_t("D1", "P", d) for d in DIGITS]
    tr += [_t("D2", "P", d) for d in "012"]
    tr += [_t("P", "M", d) for d in DIGITS] + [_t("M", "F", d) for d in DIGITS]
    return {
        "id": "cui", "name": "CUI (RENAP/DPI)", "method": "afd",
        "description": "13 dígitos: 8 de registro, 1 verificador, departamento 01-22 y municipio.",
        "num_nodes": len(states), "alphabet": DIGITS,
        "sample_valid": "1924118530114", "sample_invalid": "1924118530014",
        "automaton": {"kind": "generic", "states": states, "start": "q0",
                      "accepting": ["F"], "transitions": tr},
    }


def keywords_preset(keywords: list[str], normalize: bool = True) -> dict:
    """AFND de búsqueda: q0 se repite con cualquier símbolo y ramifica un camino por palabra clave."""
    words = []
    for k in keywords:
        k = normalize_text(k.strip()) if normalize else k.strip()
        if not k:
            raise AutomatonError("Palabra clave vacía")
        if "*" in k:
            raise AutomatonError("Las palabras clave no pueden contener '*'")
        if k not in words:
            words.append(k)
    states, tr, labels, accepting = ["q0"], [_t("q0", "q0", "*")], {}, []
    for n, k in enumerate(words, 1):
        prev = "q0"
        for j, ch in enumerate(k, 1):
            cur = f"k{n}_{j}"
            states.append(cur)
            tr.append(_t(prev, cur, ch))
            prev = cur
        accepting.append(prev)
        labels[prev] = k
    return {
        "id": "keywords", "name": "Búsqueda de palabras clave", "method": "afnd",
        "description": "Varios patrones en paralelo sobre un texto (AFND con comodín en q0).",
        "num_nodes": len(states), "alphabet": sorted({c for k in words for c in k}),
        "sample_valid": "la factura incluye el nit y el iva", "sample_invalid": "sin coincidencias aqui",
        "automaton": {"kind": "generic", "states": states, "start": "q0", "accepting": accepting,
                      "transitions": tr, "accept_mode": "any", "accept_labels": labels},
    }


FEL_VALID = """<?xml version="1.0" encoding="UTF-8"?>
<dte:GTDocumento xmlns:dte="http://www.sat.gob.gt/dte/fel/0.2.0" Version="0.1">
  <dte:SAT ClaseDocumento="dte">
    <dte:DTE ID="DatosCertificados">
      <dte:DatosEmision ID="DatosEmision">
        <dte:Emisor NITEmisor="1234567" NombreEmisor="Ventura"/>
        <dte:Receptor IDReceptor="CF"/>
      </dte:DatosEmision>
    </dte:DTE>
  </dte:SAT>
</dte:GTDocumento>"""
FEL_INVALID = FEL_VALID.replace("</dte:DTE>", "")


def fel_preset() -> dict:
    tr = [
        _t("q0", "q1", "<t>", push=["t"]), _t("q1", "q1", "<t>", push=["t"]),
        _t("q1", "q1", "</t>", pop="t"), _t("q1", "q2", "</t>", pop="t"),
        _t("q1", "q1", "<t/>"), _t("q0", "q2", "<t/>"),
    ]
    return {
        "id": "fel_xml", "name": "XML FEL (SAT)", "method": "pda",
        "description": "Balanceo de etiquetas del DTE: PUSH al abrir, POP al cerrar, una sola raíz.",
        "num_nodes": 3, "alphabet": ["<t>", "</t>", "<t/>"],
        "sample_valid": FEL_VALID, "sample_invalid": FEL_INVALID,
        "automaton": {"kind": "xml_tags", "states": ["q0", "q1", "q2"], "start": "q0",
                      "accepting": ["q2"], "transitions": tr},
    }


def anbn_preset() -> dict:
    """{aⁿbⁿ | n ≥ 1}: AP genérico de demostración."""
    tr = [
        _t("q0", "q0", "a", pop="Z", push=["A", "Z"]), _t("q0", "q0", "a", pop="A", push=["A", "A"]),
        _t("q0", "q1", "b", pop="A"), _t("q1", "q1", "b", pop="A"),
        _t("q1", "q2", None, pop="Z"),
    ]
    return {
        "id": "anbn", "name": "aⁿbⁿ (demostración)", "method": "pda",
        "description": "Apila una A por cada 'a' y desapila una por cada 'b'.",
        "num_nodes": 3, "alphabet": ["a", "b"], "sample_valid": "aaabbb", "sample_invalid": "aabbb",
        "automaton": {"kind": "generic", "states": ["q0", "q1", "q2"], "start": "q0",
                      "accepting": ["q2"], "transitions": tr, "stack_alphabet": ["A", "Z"],
                      "initial_stack": "Z"},
    }


def all_presets() -> list[dict]:
    return [nit_preset(), cui_preset(),
            keywords_preset(["iva", "factura", "nit", "contribuyente"]),
            fel_preset(), anbn_preset()]
