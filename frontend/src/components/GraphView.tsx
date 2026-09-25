import { useEffect, useRef } from "react";
import cytoscape, { type Core, type ElementDefinition } from "cytoscape";
import type { AutomatonDef, StepOut } from "../types";

const DIGITS = "0123456789".split("");

function compactLabel(symbols: string[]): string {
  const uniq = Array.from(new Set(symbols));
  if (uniq.length === 1) return uniq[0];
  const isDigitRun = (start: number, end: number) =>
    uniq.length === end - start + 1 && DIGITS.slice(start, end + 1).every((d) => uniq.includes(d));
  if (isDigitRun(0, 9)) return "0-9";
  for (let start = 0; start <= 9; start++) {
    for (let end = start + 1; end <= 9; end++) {
      if (isDigitRun(start, end)) return `${DIGITS[start]}-${DIGITS[end]}`;
    }
  }
  if (uniq.length <= 4) return uniq.join(",");
  return `${uniq.slice(0, 3).join(",")}… (${uniq.length})`;
}

function buildElements(a: AutomatonDef): ElementDefinition[] {
  const nodes: ElementDefinition[] = a.states.map((s) => ({
    data: { id: s, label: s, start: s === a.start, accepting: a.accepting.includes(s) },
  }));
  const grouped = new Map<string, { from: string; to: string; symbols: string[] }>();
  a.transitions.forEach((t) => {
    const key = `${t.from}->${t.to}`;
    const g = grouped.get(key) ?? { from: t.from, to: t.to, symbols: [] };
    g.symbols.push(t.symbol ?? "ε");
    grouped.set(key, g);
  });
  const edges: ElementDefinition[] = Array.from(grouped.entries()).map(([key, g], i) => ({
    data: { id: `e${i}`, source: g.from, target: g.to, label: compactLabel(g.symbols), pair: key },
  }));
  return [...nodes, ...edges];
}

const STYLE: cytoscape.StylesheetJson = [
  { selector: "node", style: {
    "background-color": "#ffffff", "border-width": 2, "border-color": "#1b2321",
    "label": "data(label)", "text-valign": "center", "text-halign": "center",
    "font-family": "IBM Plex Mono", "font-size": 12, "width": 42, "height": 42,
    "color": "#1b2321",
  } },
  { selector: "node[?start]", style: { "border-color": "#1e5c4f", "border-width": 3 } },
  { selector: "node[?accepting]", style: {
    "border-style": "double", "border-width": 8, "border-color": "#1e5c4f",
  } },
  { selector: "node.active", style: {
    "background-color": "#1e5c4f", "color": "#ffffff", "border-color": "#1e5c4f",
  } },
  { selector: "node.rejected", style: {
    "background-color": "#a6402f", "color": "#ffffff", "border-color": "#a6402f",
  } },
  { selector: "edge", style: {
    "curve-style": "bezier", "target-arrow-shape": "triangle",
    "line-color": "#d8dcd3", "target-arrow-color": "#d8dcd3", "width": 1.5,
    "label": "data(label)", "font-family": "IBM Plex Mono", "font-size": 10,
    "text-background-color": "#fafbf9", "text-background-opacity": 1, "text-background-padding": "2px",
    "color": "#4d5750",
  } },
  { selector: "edge.used", style: {
    "line-color": "#b5651d", "target-arrow-color": "#b5651d", "width": 3, "color": "#b5651d",
  } },
];

export default function GraphView({ automaton, step }: { automaton: AutomatonDef | null; step: StepOut | null }) {
  const ref = useRef<HTMLDivElement>(null);
  const cyRef = useRef<Core | null>(null);

  useEffect(() => {
    if (!ref.current || !automaton) return;
    const cy = cytoscape({
      container: ref.current,
      elements: buildElements(automaton),
      style: STYLE,
      layout: { name: "cose", animate: false, padding: 40 } as cytoscape.LayoutOptions,
    });
    cyRef.current = cy;
    return () => cy.destroy();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [automaton]);

  useEffect(() => {
    const cy = cyRef.current;
    if (!cy) return;
    cy.nodes().removeClass("active rejected");
    cy.edges().removeClass("used");
    if (!step) return;
    step.active_states.forEach((s) => cy.$id(s).addClass("active"));
    step.edges.forEach((e) => {
      cy.edges(`[pair = "${e.source}->${e.target}"]`).addClass("used");
    });
  }, [step]);

  if (!automaton) return <div className="graph-empty">Selecciona un preset para ver el grafo.</div>;
  return <div className="graph-canvas" ref={ref} />;
}