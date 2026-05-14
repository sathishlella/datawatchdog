import { useRef } from "react";
import { datasets as api } from "../api";
import type { Dataset } from "../types";

interface Props {
  datasets: Dataset[];
  onUploaded: (d: Dataset) => void;
  onSelect: (d: Dataset) => void;
}

export function DatasetUpload({ datasets, onUploaded, onSelect }: Props) {
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFile = async (file: File) => {
    const dataset = await api.upload(file);
    onUploaded(dataset);
  };

  return (
    <div>
      <div
        onClick={() => inputRef.current?.click()}
        onDragOver={(e) => e.preventDefault()}
        onDrop={(e) => { e.preventDefault(); const f = e.dataTransfer.files[0]; if (f) handleFile(f); }}
        style={{ background: "#0f060f", border: "2px dashed #4a1340", borderRadius: 16,
          padding: 40, textAlign: "center", cursor: "pointer", marginBottom: 24 }}>
        <div style={{ fontSize: "2rem", marginBottom: 8 }}>📂</div>
        <div style={{ color: "#f9a8d4", fontWeight: 700 }}>Drop CSV here or click to upload</div>
        <div style={{ color: "#64748b", fontSize: "0.8rem", marginTop: 4 }}>
          Accepts .csv files — columns auto-detected
        </div>
        <input ref={inputRef} type="file" accept=".csv" style={{ display: "none" }}
          onChange={(e) => { const f = e.target.files?.[0]; if (f) handleFile(f); }} />
      </div>

      {datasets.length > 0 && (
        <div>
          <div style={{ fontSize: "0.75rem", color: "#94a3b8", fontWeight: 700,
            textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 12 }}>
            Existing Datasets
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {datasets.map((d) => (
              <div key={d.id} onClick={() => onSelect(d)}
                style={{ background: "#0f060f", border: "1px solid #4a134066",
                  borderRadius: 10, padding: "14px 18px", cursor: "pointer",
                  display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <div>
                  <div style={{ fontWeight: 700, color: "#f9a8d4" }}>{d.name}</div>
                  <div style={{ fontSize: "0.75rem", color: "#64748b", marginTop: 2 }}>
                    {d.row_count} rows · {d.columns.length} columns
                  </div>
                </div>
                <div style={{ fontSize: "0.72rem", color: "#be185d",
                  fontWeight: 700, textTransform: "uppercase" }}>
                  Select →
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
