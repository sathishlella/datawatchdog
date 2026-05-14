import { useState } from "react";
import { schedules as api } from "../api";
import type { Dataset, Schedule } from "../types";

interface Props {
  dataset: Dataset;
  schedules: Schedule[];
  onSchedulesChange: (s: Schedule[]) => void;
}

const CRON_PRESETS = [
  { label: "Every hour", value: "0 * * * *" },
  { label: "Every 6 hours", value: "0 */6 * * *" },
  { label: "Daily at 8am", value: "0 8 * * *" },
  { label: "Weekly Monday 9am", value: "0 9 * * 1" },
];

export function SchedulePanel({ dataset, schedules, onSchedulesChange }: Props) {
  const [email, setEmail] = useState("");
  const [cron, setCron] = useState("0 8 * * *");
  const [threshold, setThreshold] = useState("80");

  const sel: React.CSSProperties = {
    background: "#1a0a1a", border: "1px solid #4a1340", borderRadius: 8,
    color: "#e0d0e8", padding: "8px 12px", fontSize: "0.82rem",
  };

  const addSchedule = async () => {
    if (!email) return alert("Enter an email address");
    const sched = await api.create({
      dataset_id: dataset.id, cron_expression: cron,
      alert_email: email, alert_threshold: Number(threshold),
    });
    onSchedulesChange([...schedules, sched]);
  };

  const removeSchedule = async (id: number) => {
    await api.delete(id);
    onSchedulesChange(schedules.filter((s) => s.id !== id));
  };

  return (
    <div>
      <div style={{ fontWeight: 700, color: "#f9a8d4", marginBottom: 16 }}>
        Schedules for: <span style={{ color: "#fdf2f8" }}>{dataset.name}</span>
      </div>

      <div style={{ background: "#0f060f", border: "1px solid #4a134066",
        borderRadius: 12, padding: 20, marginBottom: 20,
        display: "flex", gap: 12, flexWrap: "wrap", alignItems: "flex-end" }}>
        <div>
          <div style={{ fontSize: "0.65rem", color: "#94a3b8", marginBottom: 4 }}>SCHEDULE</div>
          <select style={sel} value={cron} onChange={(e) => setCron(e.target.value)}>
            {CRON_PRESETS.map((p) => <option key={p.value} value={p.value}>{p.label}</option>)}
          </select>
        </div>
        <div>
          <div style={{ fontSize: "0.65rem", color: "#94a3b8", marginBottom: 4 }}>ALERT EMAIL</div>
          <input style={{ ...sel, width: 220 }} type="email" value={email}
            onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" />
        </div>
        <div>
          <div style={{ fontSize: "0.65rem", color: "#94a3b8", marginBottom: 4 }}>THRESHOLD</div>
          <input style={{ ...sel, width: 80 }} type="number" value={threshold}
            onChange={(e) => setThreshold(e.target.value)} />
        </div>
        <button onClick={addSchedule}
          style={{ padding: "8px 18px", background: "#be185d", border: "none",
            borderRadius: 8, color: "#fdf2f8", fontWeight: 700, cursor: "pointer" }}>
          + Add Schedule
        </button>
      </div>

      {schedules.map((s) => (
        <div key={s.id} style={{ background: "#0f060f", border: "1px solid #4a134066",
          borderRadius: 8, padding: "12px 16px", marginBottom: 8,
          display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div>
            <span style={{ color: "#f9a8d4", fontWeight: 700 }}>{s.cron_expression}</span>
            <span style={{ color: "#64748b", fontSize: "0.78rem", marginLeft: 12 }}>
              → {s.alert_email} · threshold: {s.alert_threshold}
            </span>
          </div>
          <button onClick={() => removeSchedule(s.id)}
            style={{ background: "transparent", border: "none", color: "#f87171",
              cursor: "pointer" }}>✕</button>
        </div>
      ))}
    </div>
  );
}
