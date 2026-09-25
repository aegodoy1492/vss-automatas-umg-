import { useEffect, useRef } from "react";
import cytoscape, { type Core, type ElementDefinition } from "cytoscape";
import type { AutomatonDef, StepOut } from "../types";

function buildElements(a: AutomatonDef): ElementDefinition[] {
  const nodes: ElementDefinition[] = a.states.map((s) => ({
    data: { id: s, label: s, start: s === a.start, accepting: a.accepting.includes(s) },
  }));
  const seen = new Map<string, Set<string>>();
  const edges: ElementDefinition[] = [];
  a.transitions.forEach((t, i) => {
    const key = `${t.from}->${t.to}`;
    const label = t.symbol ?? "ε";
    const set = seen.get(key) ?? new Set<string>();
    if (set.has(label)) return;
    set.add(label);
    seen.set(key, set);
    edges.push({ data: { id: `e${i}`, source: t.from, target: t.to, label, pair: key } });
  });
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
    if (step.active_states.length === 0) {
      // sin estados activos: no hay nada que marcar como activo
    }
    step.edges.forEach((e) => {
      cy.edges(`[pair = "${e.source}->${e.target}"]`).addClass("used");
    });
  }, [step]);

  if (!automaton) return <div className="graph-empty">Selecciona un preset para ver el grafo.</div>;
  return <div className="graph-canvas" ref={ref} />;
}
