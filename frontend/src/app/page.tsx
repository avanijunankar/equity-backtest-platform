"use client";

import { useEffect, useState } from "react";
import { toast } from "sonner";
import { Play, Download } from "lucide-react";
import { AppShell } from "@/components/layout/app-shell";
import BacktestConfig from "@/components/BacktestConfig";
import { BacktestResults } from "@/components/backtest-results";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/badge";
import { useBacktest } from "@/context/backtest-context";
import {
  checkHealth,
  exportResults,
  exportResultsCsv,
  getPrebuiltStrategies,
  runBacktest,
  runPrebuiltStrategy,
} from "@/lib/api";
import type { PrebuiltStrategy } from "@/types/backtest";

export default function DashboardPage() {
  const { config, setConfig, result, setResult, loading, setLoading } = useBacktest();
  const [strategies, setStrategies] = useState<PrebuiltStrategy[]>([]);
  const [dataSource, setDataSource] = useState("demo");

  useEffect(() => {
    getPrebuiltStrategies().then(setStrategies).catch(console.error);
    checkHealth().then((h) => setDataSource(h.data_source || "demo"));
  }, []);

  const handleRun = async () => {
    setLoading(true);
    setResult(null);
    try {
      const res = await runBacktest(config);
      setResult(res);
      if (res.success) toast.success(`Backtest complete — CAGR ${res.performance.cagr}%`);
      else toast.error(res.message || "Backtest failed");
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Backtest failed");
    } finally {
      setLoading(false);
    }
  };

  const handlePrebuilt = async (id: string) => {
    setLoading(true);
    setResult(null);
    try {
      const res = await runPrebuiltStrategy(id);
      setResult(res);
      const s = strategies.find((x) => x.id === id);
      if (s) setConfig(s.config);
      if (res.success) toast.success(`Strategy complete — CAGR ${res.performance.cagr}%`);
      else toast.error(res.message || "Strategy failed");
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Strategy failed");
    } finally {
      setLoading(false);
    }
  };

  const handleExportCsv = async () => {
    if (!result) return;
    try {
      const blob = await exportResultsCsv(result);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "backtest_results.csv";
      a.click();
      URL.revokeObjectURL(url);
      toast.success("Exported to CSV");
    } catch {
      toast.error("CSV export failed");
    }
  };

  const handleExport = async () => {
    if (!result) return;
    try {
      const blob = await exportResults(result);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "backtest_results.xlsx";
      a.click();
      URL.revokeObjectURL(url);
      toast.success("Exported to Excel");
    } catch {
      toast.error("Export failed");
    }
  };

  return (
    <AppShell dataSource={dataSource}>
      <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 dark:text-white">Dashboard</h2>
          <p className="text-sm text-slate-500">Configure and run fundamental equity strategies</p>
        </div>
        {result?.success && (
          <div className="flex gap-2">
            <Button variant="secondary" onClick={handleExport}>
              <Download className="h-4 w-4" /> Excel
            </Button>
            <Button variant="outline" onClick={handleExportCsv}>
              <Download className="h-4 w-4" /> CSV
            </Button>
          </div>
        )}
      </div>

      {strategies.length > 0 && (
        <div className="mb-6 grid gap-4 md:grid-cols-3">
          {strategies.map((s) => (
            <Card key={s.id}>
              <CardHeader>
                <CardTitle>{s.name}</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="mb-4 text-sm text-slate-500">{s.description}</p>
                <Button size="sm" disabled={loading} onClick={() => handlePrebuilt(s.id)}>
                  <Play className="h-3 w-3" /> Run Strategy
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <div className="grid gap-6 xl:grid-cols-2">
        <BacktestConfig config={config} onChange={setConfig} onRun={handleRun} loading={loading} />
        <div>
          {loading ? (
            <div className="space-y-4">
              <Skeleton className="h-32 w-full" />
              <Skeleton className="h-64 w-full" />
              <Skeleton className="h-48 w-full" />
            </div>
          ) : result ? (
            <BacktestResults result={result} />
          ) : (
            <Card className="flex h-64 items-center justify-center">
              <CardContent className="text-center text-slate-400">
                Run a backtest or prebuilt strategy to see results
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </AppShell>
  );
}
