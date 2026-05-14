import axios from "axios";
import type { Dataset, Rule, Report, Schedule, AlertRecord } from "./types";

const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";
const api = axios.create({ baseURL: BASE });

export const datasets = {
  list: (): Promise<Dataset[]> => api.get("/api/datasets/").then(r => r.data),
  upload: (file: File): Promise<Dataset> => {
    const fd = new FormData();
    fd.append("file", file);
    return api.post("/api/datasets/upload", fd).then(r => r.data);
  },
  delete: (id: number) => api.delete(`/api/datasets/${id}`),
};

export const rules = {
  list: (datasetId: number): Promise<Rule[]> =>
    api.get(`/api/datasets/${datasetId}/rules`).then(r => r.data),
  create: (datasetId: number, rule: Omit<Rule, "id" | "dataset_id">) =>
    api.post(`/api/datasets/${datasetId}/rules`, rule).then((r) => r.data as Rule),
  delete: (ruleId: number) => api.delete(`/api/datasets/rules/${ruleId}`),
};

export const reports = {
  run: (datasetId: number): Promise<Report> =>
    api.post(`/api/datasets/${datasetId}/run`).then(r => r.data),
  list: (datasetId: number): Promise<Report[]> =>
    api.get(`/api/datasets/${datasetId}/reports`).then(r => r.data),
};

export const alerts = {
  list: (): Promise<AlertRecord[]> =>
    api.get("/api/datasets/alerts").then(r => r.data),
};

export const schedules = {
  list: (): Promise<Schedule[]> => api.get("/api/schedules/").then(r => r.data),
  create: (body: Omit<Schedule, "id" | "is_active">) =>
    api.post("/api/schedules/", body).then(r => r.data as Schedule),
  delete: (id: number) => api.delete(`/api/schedules/${id}`),
};
