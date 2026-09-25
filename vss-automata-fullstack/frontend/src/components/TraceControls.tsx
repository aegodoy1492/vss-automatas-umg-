import type { StepOut } from "../types";

export default function TraceControls({
  steps, index, onIndexChange, playing, onTogglePlay,
}: {
  steps: StepOut[];
  index: number;
  onIndexChange: (i: number) => void;
  playing: boolean;
  onTogglePlay: () => void;
}) {
  const step = steps[index];
  const atStart = index <= 0;
  const atEnd = index >= steps.length - 1;

  return (
    <div className="trace-bar">
      <button onClick={() => onIndexChange(0)} disabled={atStart} title="Ir al inicio">⏮</button>
      <button onClick={() => onIndexChange(index - 1)} disabled={atStart} title="Paso anterior">◀</button>
      <button onClick={onTogglePlay} disabled={steps.length < 2} title={playing ? "Pausar" : "Reproducir"}>
        {playing ? "⏸" : "▶"}
      </button>
      <button onClick={() => onIndexChange(index + 1)} disabled={atEnd} title="Paso siguiente">▶</button>
      <button onClick={() => onIndexChange(steps.length - 1)} disabled={atEnd} title="Ir al final">⏭</button>

      <input
        type="range"
        min={0}
        max={Math.max(steps.length - 1, 0)}
        value={index}
        onChange={(e) => onIndexChange(Number(e.target.value))}
      />

      <span className="step-info">paso {index}/{steps.length - 1}{step?.symbol ? ` · símbolo '${step.symbol}'` : ""}</span>
      <span className="spacer" />
      <span className="step-note">{step?.note ?? ""}</span>
    </div>
  );
}
