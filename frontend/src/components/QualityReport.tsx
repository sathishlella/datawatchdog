import type { Report } from "../types";

interface Props { report: Report | null; }

export function QualityReport({ report }: Props) {
  if (!report) return (
    <div style={{ textAlign: "center", padding: 60, color: "#64748b" }}>
      No report yet — select a dataset, add rules, then click "Run Check".
    </div>
  );

  const score = Number(report.score);
  const color = score >= 80 ? "#6ee7b7" : score >= 60 ? "#f9a8d4" : "#f87171";

  return (
    <div>
      <div style={{ display: "flex", gap: 20, marginBottom: 24, flexWrap: "wrap" }}>
        <div style={{ background: "#0f060f", border: `2px solid ${color}55`,
          borderRadius: 16, padding: "24px 32px", textAlign: "center" }}>
          <div style={{ fontSize: "3.5rem", fontWeight: 900, color, lineHeight: 1 }}>
            {score.toFixed(1)}
          </div>
          <div style={{ fontSize: "0.7rem", color: "#64748b", textTransform: "uppercase",
            letterSpacing: "0.1em", marginTop: 6 }}>Quality Score</div>
        </div>
        <div style={{ flex: 1, background: "#0f060f", border: "1px solid #4a134066",
          borderRadius: 16, padding: "20px 24px", minWidth: 200 }}>
          <div style={{ fontSize: "0.75rem", color: "#94a3b8", fontWeight: 700,
            textTransform: "uppercase", marginBottom: 8 }}>
            Last Run: {new Date(report.run_at).toLocaleString()}
          </div>
          <div style={{ fontSize: "0.85rem", color: "#e0d0e8" }}>
            {report.issues.length === 0 ? (
              <span style={{ color: "#6ee7b7" }}>✓ All quality checks passed</span>
            ) : (
              <span style={{ color: "#f9a8d4" }}>
                {report.issues.length} issue(s) found
              </span>
            )}
          </div>
        </div>
      </div>

      {report.issues.length > 0 && (
        <div style={{ background: "#0f060f", border: "1px solid #4a134066",
          borderRadius: 16, overflow: "hidden" }}>
          <div style={{ padding: "12px 18px", borderBottom: "1px solid #2a0f2a",
            fontSize: "0.75rem", color: "#f9a8d4", fontWeight: 700,
            textTransform: "uppercase", letterSpacing: "0.08em" }}>
            Issues
          </div>
          {report.issues.map((issue, i) => (
            <div key={i} style={{ padding: "12px 18px", borderBottom: "1px solid #1a0a1a",
              display: "flex", gap: 12 }}>
              <span style={{ background: "#2a0f2a", color: "#f9a8d4",
                padding: "2px 8px", borderRadius: 4, fontSize: "0.7rem",
                fontWeight: 700, whiteSpace: "nowrap" }}>
                {issue.column}
              </span>
              <span style={{ color: "#94a3b8", fontSize: "0.8rem" }}>{issue.message}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
