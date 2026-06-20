import { type BacktestRequest, type BacktestResult } from "@/types/backtest";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const TIMEOUT_MS = 120_000;

async function fetchWithTimeout(url: string, options: RequestInit = {}): Promise<Response> {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), TIMEOUT_MS);
  try {
    return await fetch(url, { ...options, signal: controller.signal });
  } finally {
    clearTimeout(id);
  }
}

export async function runBacktest(config: BacktestRequest): Promise<BacktestResult> {
  const res = await fetchWithTimeout(`${API_BASE}/api/backtest/run`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(config),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || "Backtest failed");
  }
  return res.json();
}

export async function getPrebuiltStrategies() {
  const res = await fetchWithTimeout(`${API_BASE}/api/backtest/strategies`);
  if (!res.ok) throw new Error("Failed to fetch strategies");
  return res.json();
}

export async function runPrebuiltStrategy(id: string): Promise<BacktestResult> {
  const res = await fetchWithTimeout(`${API_BASE}/api/backtest/strategies/${id}/run`, {
    method: "POST",
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getAvailableMetrics(): Promise<string[]> {
  const res = await fetchWithTimeout(`${API_BASE}/api/stocks/metrics`);
  if (!res.ok) return [];
  const data = await res.json();
  return data.metrics || [];
}

export async function getStocks() {
  const res = await fetchWithTimeout(`${API_BASE}/api/stocks/`);
  if (!res.ok) return [];
  return res.json();
}

export async function checkHealth(): Promise<{
  status: string;
  database: string;
  data_source: string;
  use_database: boolean;
}> {
  const res = await fetchWithTimeout(`${API_BASE}/api/data/health`);
  return res.json();
}

export async function exportResults(data: BacktestResult): Promise<Blob> {
  const res = await fetchWithTimeout(`${API_BASE}/api/backtest/export`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Export failed");
  return res.blob();
}

export async function exportResultsCsv(data: BacktestResult): Promise<Blob> {
  const res = await fetchWithTimeout(`${API_BASE}/api/backtest/export/csv`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("CSV export failed");
  return res.blob();
}

export async function compareStrategies(configs: BacktestRequest[]) {
  const res = await fetchWithTimeout(`${API_BASE}/api/backtest/compare`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(configs),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
