import type { StepOut } from "../types";

export default function StackView({ step }: { step: StepOut | null }) {
  const stack = step?.stack ?? null;
  return (
    <>
      <div className="stack-title">Pila (Autómata de Pila)</div>
      {!stack ? (
        <div className="stack-empty">No aplica para este método.</div>
      ) : stack.length === 0 ? (
        <div className="stack-empty">Pila vacía.</div>
      ) : (
        <div className="stack-col">
          {stack.map((s, i) => (
            <div key={i} className={"stack-tile" + (i === stack.length - 1 ? " top" : "")}>
              {s}
            </div>
          ))}
        </div>
      )}
    </>
  );
}
