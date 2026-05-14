import { useState } from "react";
import { rules as api } from "../api";
import type { Dataset, Rule } from "../types";

interface Props {
  dataset: Dataset;
  rules: Rule[];
  onRulesChange: (rules: Rule[]) => void;
}

const RULE_TYPES = ["null", "duplicate", "range", "format", "referential"] as const;

export function RuleBuilder({ dataset, rules, onRulesChange }: Props) {
  const [column, setColumn] = useState(dataset.columns[0] || "");
  const [ruleType, setRuleType] = useState<typeof RULE_TYPES[number]>("null");
  const [threshold, setThreshold] = useState("5");
  const [pattern, setPattern] = useState("");
  const [minVal, setMinVal] = useState("0");
  const [maxVal, setMaxVal] = useState("1000");
  const [allowed, setAllowed] = useState("");

  const sel: React.CSSProperties = {
    background: "#1a0a1a", border: "1px solid #4a1340", borderRadius: 8,
    color: "#e0d0e8", padding: "8px 12px", fontSize: "0.82rem",
  };

  const buildConfig = () => {
    if (ruleType === "null" || ruleType === "duplicate") return { threshold: Number(threshold) };
    if (ruleType === "range") return { min: Number(minVal), max: Number(maxVal) };
    if (ruleType === "format") return { pattern };
    if (ruleType === "referential") return { allowed: allowed.split(",").map((s) => s.trim()) };
    return {};
  };

  const addRule = async () => {
    const rule = await api.create(dataset.id, {
      column_name: column, rule_type: ruleType,
      rule_config: buildConfig(), weight: 1.0,
    });
    onRulesChange([...rules, rule]);
  };

  const removeRule = async (id: number) => {
    await api.delete(id);
    onRulesChange(rules.filter((r) => r.id !== id));
  };

  return (
    <div>
      <div style={{ fontWeight: 700, color: "#f9a8d4", marginBottom: 16 }}>
        Rules for: <span style={{ color: "#fdf2f8" }}>{dataset.name}</span>
      </div>

      <div style={{ background: "#0f060f", border: "1px solid #4a134066",
        borderRadius: 12, padding: 20, marginBottom: 20,
        display: "flex", gap: 12, flexWrap: "wrap", alignItems: "flex-end" }}>
        <div>
          <div style={{ fontSize: "0.65rem", color: "#94a3b8", marginBottom: 4 }}>COLUMN</div>
          <select style={sel} value={column} onChange={(e) => setColumn(e.target.value)}>
            {dataset.columns.map((c) => <option key={c} value={c}>{c}</option>)}
          </select>
        </div>
        <div>
          <div style={{ fontSize: "0.65rem", color: "#94a3b8", marginBottom: 4 }}>CHECK TYPE</div>
          <select style={sel} value={ruleType}
            onChange={(e) => setRuleType(e.target.value as typeof RULE_TYPES[number])}>
            {RULE_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
          </select>
        </div>
        {(ruleType === "null" || ruleType === "duplicate") && (
          <div>
            <div style={{ fontSize: "0.65rem", color: "#94a3b8", marginBottom: 4 }}>THRESHOLD %</div>
            <input style={sel} type="number" value={threshold}
              onChange={(e) => setThreshold(e.target.value)} />
          </div>
        )}
        {ruleType === "range" && (
          <>
            <div>
              <div style={{ fontSize: "0.65rem", color: "#94a3b8", marginBottom: 4 }}>MIN</div>
              <input style={sel} type="number" value={minVal}
                onChange={(e) => setMinVal(e.target.value)} />
            </div>
            <div>
              <div style={{ fontSize: "0.65rem", color: "#94a3b8", marginBottom: 4 }}>MAX</div>
              <input style={sel} type="number" value={maxVal}
                onChange={(e) => setMaxVal(e.target.value)} />
            </div>
          </>
        )}
        {ruleType === "format" && (
          <div>
            <div style={{ fontSize: "0.65rem", color: "#94a3b8", marginBottom: 4 }}>REGEX PATTERN</div>
            <input style={{ ...sel, width: 200 }} value={pattern}
              onChange={(e) => setPattern(e.target.value)}
              placeholder="^\d{4}-\d{2}-\d{2}$" />
          </div>
        )}
        {ruleType === "referential" && (
          <div>
            <div style={{ fontSize: "0.65rem", color: "#94a3b8", marginBottom: 4 }}>
              ALLOWED VALUES (comma-sep)
            </div>
            <input style={{ ...sel, width: 220 }} value={allowed}
              onChange={(e) => setAllowed(e.target.value)} placeholder="Male,Female,Non-binary" />
          </div>
        )}
        <button onClick={addRule}
          style={{ padding: "8px 18px", background: "#be185d", border: "none",
            borderRadius: 8, color: "#fdf2f8", fontWeight: 700, cursor: "pointer" }}>
          + Add Rule
        </button>
      </div>

      {rules.length > 0 ? (
        <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          {rules.map((r) => (
            <div key={r.id} style={{ background: "#0f060f", border: "1px solid #4a134066",
              borderRadius: 8, padding: "12px 16px",
              display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <div>
                <span style={{ color: "#f9a8d4", fontWeight: 700, fontSize: "0.85rem" }}>
                  {r.column_name}
                </span>
                <span style={{ color: "#7c2d6b", fontSize: "0.75rem", marginLeft: 8,
                  background: "#2a0f2a", padding: "2px 8px", borderRadius: 4 }}>
                  {r.rule_type}
                </span>
                <span style={{ color: "#64748b", fontSize: "0.72rem", marginLeft: 10 }}>
                  {JSON.stringify(r.rule_config)}
                </span>
              </div>
              <button onClick={() => removeRule(r.id)}
                style={{ background: "transparent", border: "none", color: "#f87171",
                  cursor: "pointer", fontSize: "0.8rem" }}>
                ✕ Remove
              </button>
            </div>
          ))}
        </div>
      ) : (
        <div style={{ textAlign: "center", padding: 32, color: "#64748b" }}>
          No rules yet. Add your first quality check above.
        </div>
      )}
    </div>
  );
}
