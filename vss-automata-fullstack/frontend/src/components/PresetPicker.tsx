import type { Preset } from "../types";

export default function PresetPicker({
  presets, selectedId, onSelect,
}: { presets: Preset[]; selectedId: string; onSelect: (id: string) => void }) {
  return (
    <select value={selectedId} onChange={(e) => onSelect(e.target.value)}>
      {presets.map((p) => (
        <option key={p.id} value={p.id}>{p.name}</option>
      ))}
    </select>
  );
}
