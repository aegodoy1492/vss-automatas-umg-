export type Method = "afd" | "afnd" | "pda";

export interface TransitionIn {
  from: string;
  to: string;
  symbol: string | null;
  pop?: string | null;
  push?: string[];
}

export interface AutomatonDef {
  kind: "generic" | "xml_tags";
  states: string[];
  start: string;
  accepting: string[];
  transitions: TransitionIn[];
  stack_alphabet: string[];
  initial_stack: string;
  accept_by: "final_state" | "empty_stack";
  accept_mode: "end" | "any";
  accept_labels: Record<string, string>;
}

export interface Preset {
  id: string;
  name: string;
  description: string;
  method: Method;
  num_nodes: number;
  alphabet: string[];
  sample_valid: string;
  sample_invalid: string;
  automaton: AutomatonDef;
}

export interface EdgeOut {
  source: string;
  target: string;
  label: string;
}

export interface StepOut {
  index: number;
  symbol: string | null;
  active_states: string[];
  edges: EdgeOut[];
  stack: string[] | null;
  note: string;
}

export interface MatchOut {
  pattern: string;
  start: number | null;
  end: number;
}

export interface SimulationResponse {
  method: Method;
  accepted: boolean;
  reason: string;
  steps: StepOut[];
  matches: MatchOut[];
  final_states: string[];
  final_stack: string[] | null;
  error_position: number | null;
}

export interface ApiError {
  detail: string;
}
