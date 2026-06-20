"use client";

import { useEffect, useState } from "react";
import { AppShell } from "@/components/layout/app-shell";
import BacktestConfig from "@/components/BacktestConfig";
import { useBacktest } from "@/context/backtest-context";
import { checkHealth, getAvailableMetrics, runBacktest } from "@/lib/api";
import { toast } from "sonner";

export default function BuilderPage() {
  const { config, setConfig, setResult, loading, setLoading } = useBacktest();
  const [metrics, setMetrics] = useState<string[]>([]);
  const [dataSource, setDataSource] = useState("demo");

  useEffect(() => {
    getAvailableMetrics().then(setMetrics);
    checkHealth().then((h) => setDataSource(h.data_source));
  }, []);

  const handleRun = async () => {
    setLoading(true);
    try {
      const res = await runBacktest(config);
      setResult(res);
      if (res.success) toast.success("Backtest saved — view in Results");
      else toast.error(res.message || "Failed");
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <AppShell dataSource={dataSource}>
      <h2 className="mb-6 text-2xl font-bold">Strategy Builder</h2>
      <BacktestConfig config={config} onChange={setConfig} metrics={metrics} onRun={handleRun} loading={loading} />
    </AppShell>
  );
}
