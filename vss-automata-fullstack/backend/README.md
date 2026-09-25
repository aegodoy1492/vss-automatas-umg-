# VSS · Backend Autómatas (FastAPI)

```
pip install -r requirements.txt
pytest -q
uvicorn app.main:app --reload      # http://localhost:8000/docs
```

| Endpoint | Uso |
|---|---|
| `GET /api/presets` | NIT, CUI, palabras clave, XML FEL, aⁿbⁿ (con los 4 parámetros precargados) |
| `POST /api/presets/keywords` | Construye el AFND para una lista de palabras clave |
| `POST /api/simulate` | `num_nodes`, `alphabet`, `string`, `method` (`afd`/`afnd`/`pda`) + `automaton` → traza paso a paso |
