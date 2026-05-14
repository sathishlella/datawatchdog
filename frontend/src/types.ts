export interface Dataset {
  id: number;
  name: string;
  columns: string[];
  row_count: number;
  created_at: string;
}

export interface Rule {
  id: number;
  dataset_id: number;
  column_name: string;
  rule_type: "null" | "duplicate" | "range" | "format" | "referential";
  rule_config: Record<string, unknown>;
  weight: number;
}

export interface Issue {
  column: string;
  rule_type: string;
  message: string;
}

export interface Report {
  id: number;
  dataset_id: number;
  score: number;
  issues: Issue[];
  run_at: string;
}

export interface Schedule {
  id: number;
  dataset_id: number;
  cron_expression: string;
  alert_email: string;
  alert_threshold: number;
  is_active: boolean;
}

export interface AlertRecord {
  id: number;
  dataset_id: number;
  score: number;
  threshold: number;
  email: string;
  sent_at: string;
}
