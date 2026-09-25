import type { Preset, SimulationResponse, AutomatonDef, Method } from "./types";

const BASE = "http://localhost:8000";

async function unwrap<T>(res: Response): Promise<T> {
  const data = await res.json();
  if (!res.ok) throw new Error((data as { detail?: string }).detail ?? "Error desconocido");
  return data as T;
}

export function getPresets(): Promise<Preset[]> {
  return fetch(`${BASE}/api/presets`).then(unwrap<Preset[]>);
}

export function buildKeywordsPreset(keywords: string[], normalize: boolean): Promise<Preset> {
  return fetch(`${BASE}/api/presets/keywords`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ keywords, normalize }),
  }).then(unwrap<Preset>);
}

export interface SimulateArgs {
  num_nodes: number;
  alphabet: string[];
  string: string;
  method: Method;
  automaton: AutomatonDef;
  normalize: boolean;
}

export function simulate(args: SimulateArgs): Promise<SimulationResponse> {
  return fetch(`${BASE}/api/simulate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(args),
  }).then(unwrap<SimulationResponse>);
}
