import type { AlertRecord } from "../types";

interface Props { alerts: AlertRecord[]; }

export function AlertHistory({ alerts }: Props) {
  if (alerts.length === 0) return (
    <div style={{ textAlign: "center", padding: 60, color: "#64748b" }}>
      No alerts sent yet.
    </div>
  );

  return (
    <div>
      {alerts.map((a) => (
        <div key={a.id} style={{ background: "#0f060f", border: "1px solid #4a134066",
          borderRadius: 8, padding: "14px 18px", marginBottom: 8,
          display: "flex", gap: 16, alignItems: "center" }}>
          <div style={{ fontSize: "1.4rem", fontWeight: 900,
            color: a.score < 60 ? "#f87171" : "#f9a8d4" }}>
            {a.score.toFixed(1)}
          </div>
          <div>
            <div style={{ fontSize: "0.8rem", color: "#e0d0e8" }}>
              Score below threshold of {a.threshold} · sent to {a.email}
            </div>
            <div style={{ fontSize: "0.7rem", color: "#64748b", marginTop: 2 }}>
              {new Date(a.sent_at).toLocaleString()}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
