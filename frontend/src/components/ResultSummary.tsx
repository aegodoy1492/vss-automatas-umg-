import type { SimulationResponse } from "../types";

export default function ResultSummary({ result }: { result: SimulationResponse }) {
  return (
    <div className={"result " + (result.accepted ? "accepted" : "rejected")}>
      <div className="verdict">{result.accepted ? "Cadena aceptada" : "Cadena rechazada"}</div>
      <div className="reason">{result.reason}</div>

      {result.matches.length > 0 && (
        <div className="matches-list">
          {result.matches.map((m, i) => (
            <div className="match-row" key={i}>
              <span>{m.pattern}</span>
              <span>{m.start ? `${m.start}–${m.end}` : `pos. ${m.end}`}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
