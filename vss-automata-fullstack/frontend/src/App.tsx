import { useEffect, useMemo, useRef, useState } from "react";
import { buildKeywordsPreset, getPresets, simulate } from "./api";
import type { Preset, SimulationResponse } from "./types";
import PresetPicker from "./components/PresetPicker";
import ParamsPanel from "./components/ParamsPanel";
import ResultSummary from "./components/ResultSummary";
import GraphView from "./components/GraphView";
import StackView from "./components/StackView";
import TraceControls from "./components/TraceControls";

export default function App() {
  const [presets, setPresets] = useState<Preset[]>([]);
  const [selectedId, setSelectedId] = useState("");
  const [preset, setPreset] = useState<Preset | null>(null);
  const [input, setInput] = useState("");
  const [normalize, setNormalize] = useState(false);
  const [keywordsInput, setKeywordsInput] = useState("iva, factura, nit, contribuyente");
  const [keywordsBusy, setKeywordsBusy] = useState(false);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<SimulationResponse | null>(null);
  const [stepIndex, setStepIndex] = useState(0);
  const [playing, setPlaying] = useState(false);
  const timer = useRef<number | null>(null);

  useEffect(() => {
    getPresets()
      .then((list) => {
        setPresets(list);
        if (list.length) {
          setSelectedId(list[0].id);
          setPreset(list[0]);
          setInput(list[0].sample_valid);
        }
      })
      .catch((e) => setError(String(e.message ?? e)));
  }, []);

  function selectPreset(id: string) {
    const p = presets.find((x) => x.id === id);
    if (!p) return;
    setSelectedId(id);
    setPreset(p);
    setInput(p.sample_valid);
    setResult(null);
    setStepIndex(0);
    setPlaying(false);
  }

  async function rebuildKeywords() {
    setKeywordsBusy(true);
    setError(null);
    try {
      const words = keywordsInput.split(",").map((w) => w.trim()).filter(Boolean);
      const p = await buildKeywordsPreset(words, normalize);
      setPreset(p);
      setPresets((prev) => prev.map((x) => (x.id === "keywords" ? p : x)));
      setResult(null);
      setStepIndex(0);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setKeywordsBusy(false);
    }
  }

  async function run() {
    if (!preset) return;
    setRunning(true);
    setError(null);
    setResult(null);
    setPlaying(false);
    try {
      const r = await simulate({
        num_nodes: preset.num_nodes,
        alphabet: preset.alphabet,
        string: input,
        method: preset.method,
        automaton: preset.automaton,
        normalize,
      });
      setResult(r);
      setStepIndex(0);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setRunning(false);
    }
  }

  useEffect(() => {
    if (!playing || !result) return;
    timer.current = window.setInterval(() => {
      setStepIndex((i) => {
        if (i >= result.steps.length - 1) {
          setPlaying(false);
          return i;
        }
        return i + 1;
      });
    }, 700);
    return () => { if (timer.current) window.clearInterval(timer.current); };
  }, [playing, result]);

  const currentStep = useMemo(
    () => (result ? result.steps[stepIndex] ?? null : null),
    [result, stepIndex]
  );

  return (
    <div className="app">
      <header className="app-header">
        <div>
          <div className="brand"><span>VSS</span> · Plataforma de Autómatas y Lenguajes Formales</div>
          <div className="subtitle">UMG · Autómatas &amp; Lenguajes Formales</div>
        </div>
        {presets.length > 0 && (
          <PresetPicker presets={presets} selectedId={selectedId} onSelect={selectPreset} />
        )}
      </header>

      <div className="app-body">
        <div className="panel panel-left">
          {preset && (
            <>
              <ParamsPanel
                preset={preset}
                keywordsInput={keywordsInput}
                onKeywordsInput={setKeywordsInput}
                onRebuildKeywords={rebuildKeywords}
                keywordsBusy={keywordsBusy}
                input={input}
                onInputChange={setInput}
                normalize={normalize}
                onNormalizeChange={setNormalize}
                onRun={run}
                running={running}
                error={error}
              />
              {result && <ResultSummary result={result} />}
            </>
          )}
        </div>

        <div className="panel panel-center">
          <GraphView automaton={preset?.automaton ?? null} step={currentStep} />
        </div>

        <div className="panel panel-right">
          <StackView step={currentStep} />
        </div>
      </div>

      {result && (
        <TraceControls
          steps={result.steps}
          index={stepIndex}
          onIndexChange={(i) => { setStepIndex(i); setPlaying(false); }}
          playing={playing}
          onTogglePlay={() => setPlaying((p) => !p)}
        />
      )}
    </div>
  );
}
