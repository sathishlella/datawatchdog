import { useEffect, useState } from "react";
import { datasets as dsApi, rules as rulesApi, reports, alerts, schedules as schedApi } from "../api";
import type { AlertRecord, Dataset, Report, Rule, Schedule } from "../types";
import { AlertHistory } from "./AlertHistory";
import { DatasetUpload } from "./DatasetUpload";
import { QualityReport } from "./QualityReport";
import { RuleBuilder } from "./RuleBuilder";
import { SchedulePanel } from "./SchedulePanel";

type Tab = "datasets" | "rules" | "report" | "schedules" | "alerts";

const TABS: { id: Tab; label: string }[] = [
  { id: "datasets", label: "Datasets" },
  { id: "rules", label: "Rules" },
  { id: "report", label: "Report" },
  { id: "schedules", label: "Schedules" },
  { id: "alerts", label: "Alert History" },
];

export function Dashboard() {
  const [tab, setTab] = useState<Tab>("datasets");
  const [datasetList, setDatasetList] = useState<Dataset[]>([]);
  const [selectedDataset, setSelectedDataset] = useState<Dataset | null>(null);
  const [ruleList, setRuleList] = useState<Rule[]>([]);
  const [latestReport, setLatestReport] = useState<Report | null>(null);
  const [alertList, setAlertList] = useState<AlertRecord[]>([]);
  const [scheduleList, setScheduleList] = useState<Schedule[]>([]);
  const [running, setRunning] = useState(false);

  useEffect(() => {
    dsApi.list().then(setDatasetList);
    alerts.list().then(setAlertList);
  }, []);

  const handleSelect = async (d: Dataset) => {
    setSelectedDataset(d);
    setLatestReport(null);
    const [r, s] = await Promise.all([
      rulesApi.list(d.id),
      schedApi.list(d.id),
    ]);
    setRuleList(r);
    setScheduleList(s);
    setTab("rules");
  };

  const handleUploaded = (d: Dataset) => {
    setDatasetList((prev) => [...prev, d]);
    handleSelect(d);
  };

  const runCheck = async () => {
    if (!selectedDataset) return;
    setRunning(true);
    try {
      const rep = await reports.run(selectedDataset.id);
      setLatestReport(rep);
      setTab("report");
    } finally {
      setRunning(false);
    }
  };

  const pill = (id: Tab): React.CSSProperties => ({
    padding: "8px 18px", borderRadius: 20, cursor: "pointer", fontSize: "0.82rem",
    fontWeight: 700, border: "none",
    background: tab === id ? "#be185d" : "transparent",
    color: tab === id ? "#fdf2f8" : "#94a3b8",
  });

  return (
    <div style={{ maxWidth: 900, margin: "0 auto", padding: "32px 16px" }}>
      <div style={{ marginBottom: 32 }}>
        <div style={{ fontSize: "1.8rem", fontWeight: 900, color: "#f9a8d4",
          letterSpacing: "-0.02em" }}>
          DataWatchdog
        </div>
        <div style={{ color: "#64748b", fontSize: "0.85rem", marginTop: 4 }}>
          Automated CSV quality monitoring &amp; alerting
        </div>
      </div>

      <div style={{ display: "flex", gap: 8, marginBottom: 24,
        background: "#0f060f", padding: 6, borderRadius: 24,
        border: "1px solid #4a134066", width: "fit-content" }}>
        {TABS.map((t) => (
          <button key={t.id} style={pill(t.id)} onClick={() => setTab(t.id)}>
            {t.label}
          </button>
        ))}
      </div>

      {selectedDataset && (
        <div style={{ display: "flex", alignItems: "center", gap: 16, marginBottom: 24 }}>
          <div style={{ color: "#64748b", fontSize: "0.8rem" }}>
            Active dataset:
            <span style={{ color: "#f9a8d4", fontWeight: 700, marginLeft: 6 }}>
              {selectedDataset.name}
            </span>
          </div>
          <button onClick={runCheck} disabled={running}
            style={{ padding: "8px 22px", background: running ? "#4a1340" : "#be185d",
              border: "none", borderRadius: 8, color: "#fdf2f8", fontWeight: 700,
              cursor: running ? "not-allowed" : "pointer", fontSize: "0.82rem" }}>
            {running ? "Running…" : "▶ Run Check"}
          </button>
        </div>
      )}

      {tab === "datasets" && (
        <DatasetUpload
          datasets={datasetList}
          onUploaded={handleUploaded}
          onSelect={handleSelect}
        />
      )}
      {tab === "rules" && selectedDataset && (
        <RuleBuilder
          dataset={selectedDataset}
          rules={ruleList}
          onRulesChange={setRuleList}
        />
      )}
      {tab === "rules" && !selectedDataset && (
        <div style={{ textAlign: "center", padding: 60, color: "#64748b" }}>
          Select a dataset first.
        </div>
      )}
      {tab === "report" && <QualityReport report={latestReport} />}
      {tab === "schedules" && selectedDataset && (
        <SchedulePanel
          dataset={selectedDataset}
          schedules={scheduleList}
          onSchedulesChange={setScheduleList}
        />
      )}
      {tab === "schedules" && !selectedDataset && (
        <div style={{ textAlign: "center", padding: 60, color: "#64748b" }}>
          Select a dataset first.
        </div>
      )}
      {tab === "alerts" && <AlertHistory alerts={alertList} />}
    </div>
  );
}
