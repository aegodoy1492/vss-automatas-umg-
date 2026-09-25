import type { Method, Preset } from "../types";

const METHOD_LABEL: Record<Method, string> = { afd: "AFD", afnd: "AFND", pda: "AP" };

export default function ParamsPanel({
  preset, keywordsInput, onKeywordsInput, onRebuildKeywords, keywordsBusy,
  input, onInputChange, normalize, onNormalizeChange, onRun, running, error,
}: {
  preset: Preset;
  keywordsInput: string;
  onKeywordsInput: (v: string) => void;
  onRebuildKeywords: () => void;
  keywordsBusy: boolean;
  input: string;
  onInputChange: (v: string) => void;
  normalize: boolean;
  onNormalizeChange: (v: boolean) => void;
  onRun: () => void;
  running: boolean;
  error: string | null;
}) {
  return (
    <>
      <div className="field">
        <label>¿Número de nodos? — |Q|</label>
        <div className="hint">{preset.num_nodes} estados</div>
      </div>

      <div className="field">
        <label>¿Alfabeto a utilizar? — Σ</label>
        <div className="chips">
          {preset.alphabet.slice(0, 24).map((s, i) => (
            <span className="chip" key={i}>{s === " " ? "␣" : s}</span>
          ))}
          {preset.alphabet.length > 24 && <span className="chip">+{preset.alphabet.length - 24}</span>}
        </div>
      </div>

      <div className="field">
        <label>¿Método de solución?</label>
        <div className="method-row">
          {(["afd", "afnd", "pda"] as Method[]).map((m) => (
            <span key={m} className={"method-pill" + (preset.method === m ? " active" : "")}>
              {METHOD_LABEL[m]}
            </span>
          ))}
        </div>
      </div>

      {preset.id === "keywords" && (
        <div className="field">
          <label>Palabras clave (separadas por coma)</label>
          <textarea
            value={keywordsInput}
            onChange={(e) => onKeywordsInput(e.target.value)}
            rows={2}
          />
          <button className="ghost" style={{ marginTop: 6 }} onClick={onRebuildKeywords} disabled={keywordsBusy}>
            {keywordsBusy ? "Actualizando…" : "Reconstruir AFND"}
          </button>
        </div>
      )}

      <div className="field">
        <label>¿Cadena a analizar? — w</label>
        <textarea
          value={input}
          onChange={(e) => onInputChange(e.target.value)}
          rows={preset.id === "fel_xml" ? 10 : 3}
        />
      </div>

      <div className="field">
        <label style={{ display: "flex", alignItems: "center", gap: 6, cursor: "pointer" }}>
          <input type="checkbox" checked={normalize} onChange={(e) => onNormalizeChange(e.target.checked)} />
          Normalizar (minúsculas, sin acentos)
        </label>
      </div>

      <button className="primary" onClick={onRun} disabled={running}>
        {running ? "Ejecutando…" : "Ejecutar"}
      </button>

      {error && <div className="error-banner">{error}</div>}
    </>
  );
}
