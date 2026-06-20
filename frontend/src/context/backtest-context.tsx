"use client";

import { createContext, useContext, useState, type ReactNode } from "react";
import type { BacktestRequest, BacktestResult } from "@/types/backtest";

interface BacktestContextValue {
  config: BacktestRequest;
  setConfig: (config: BacktestRequest) => void;
  result: BacktestResult | null;
  setResult: (result: BacktestResult | null) => void;
  loading: boolean;
  setLoading: (loading: boolean) => void;
}

const DEFAULT_CONFIG: BacktestRequest = {
  start_date: "2018-01-01",
  end_date: "2024-12-31",
  initial_capital: 1_000_000,
  portfolio_size: 20,
  rebalance_frequency: "quarterly",
  position_sizing: "equal",
  sizing_metric: "roce",
  filters: [
    { metric: "market_cap_cr", operator: "between", value: [1000, 50000] },
    { metric: "roce", operator: ">", value: 15 },
  ],
  ranking_rules: [
    { metric: "roe", direction: "desc", weight: 0.5 },
    { metric: "pe_ratio", direction: "asc", weight: 0.5 },
  ],
  include_benchmark: true,
};

const BacktestContext = createContext<BacktestContextValue | null>(null);

export function BacktestProvider({ children }: { children: ReactNode }) {
  const [config, setConfig] = useState<BacktestRequest>(DEFAULT_CONFIG);
  const [result, setResult] = useState<BacktestResult | null>(null);
  const [loading, setLoading] = useState(false);

  return (
    <BacktestContext.Provider value={{ config, setConfig, result, setResult, loading, setLoading }}>
      {children}
    </BacktestContext.Provider>
  );
}

export function useBacktest() {
  const ctx = useContext(BacktestContext);
  if (!ctx) throw new Error("useBacktest must be used within BacktestProvider");
  return ctx;
}
