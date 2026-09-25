from fastapi.testclient import TestClient

from app.main import app

c = TestClient(app)


def payload(p, w, **kw):
    return {"num_nodes": p["num_nodes"], "alphabet": p["alphabet"], "string": w,
            "method": p["method"], "automaton": p["automaton"], **kw}


def presets():
    return {p["id"]: p for p in c.get("/api/presets").json()}


def test_presets_roundtrip_all():
    for p in presets().values():
        for w, ok in ((p["sample_valid"], True), (p["sample_invalid"], False)):
            r = c.post("/api/simulate", json=payload(p, w))
            assert r.status_code == 200, r.text
            assert r.json()["accepted"] is ok, (p["id"], w, r.json()["reason"])


def test_keywords_endpoint_and_normalize():
    p = c.post("/api/presets/keywords", json={"keywords": ["Artículo", "IVA"]}).json()
    r = c.post("/api/simulate", json=payload(p, "El ARTÍCULO 5 y el Iva", normalize=True)).json()
    assert r["accepted"] and {m["pattern"] for m in r["matches"]} == {"articulo", "iva"}


def test_validation_errors():
    p = presets()["nit"]
    bad = payload(p, "1-2"); bad["num_nodes"] = 5
    assert c.post("/api/simulate", json=bad).status_code == 422
    bad = payload(p, "1-2"); bad["method"] = "xxx"
    assert c.post("/api/simulate", json=bad).status_code == 422
    bad = payload(p, "1-2"); bad["alphabet"] = ["12"]
    assert c.post("/api/simulate", json=bad).status_code == 422
    nd = payload(p, "1-2"); nd["automaton"]["transitions"] = nd["automaton"]["transitions"] + [
        {"from": "q0", "to": "q3", "symbol": "0"}]
    assert "No determinista" in c.post("/api/simulate", json=nd).json()["detail"]
    assert c.post("/api/presets/keywords", json={"keywords": []}).status_code == 422


def test_afd_preset_run_as_afnd_is_valid():
    p = presets()["nit"]
    r = c.post("/api/simulate", json=payload(p, "12-3", method="afnd")).json()
    assert r["accepted"]
