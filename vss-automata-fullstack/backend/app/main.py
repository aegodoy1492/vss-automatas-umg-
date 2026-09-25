from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .engines import AutomatonError
from .presets import all_presets, keywords_preset
from .schemas import KeywordsRequest, SimulationRequest, SimulationResponse
from .service import simulate, to_dict

app = FastAPI(title="VSS · Plataforma de Autómatas y Lenguajes Formales", version="0.1.0")
app.add_middleware(CORSMiddleware,
                   allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
                   allow_methods=["*"], allow_headers=["*"])


@app.exception_handler(AutomatonError)
async def _automaton_error(_, exc: AutomatonError):
    return JSONResponse(status_code=422, content={"detail": str(exc)})


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/presets")
def presets():
    return all_presets()


@app.post("/api/presets/keywords")
def build_keywords(req: KeywordsRequest):
    return keywords_preset(req.keywords, req.normalize)


@app.post("/api/simulate", response_model=SimulationResponse)
def run(req: SimulationRequest):
    return to_dict(simulate(req))
