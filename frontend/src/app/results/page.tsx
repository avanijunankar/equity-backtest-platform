"use client";

import { useEffect, useState } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { BacktestResults } from "@/components/backtest-results";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/badge";
import { useBacktest } from "@/context/backtest-context";
import { checkHealth } from "@/lib/api";

export default function ResultsPage() {
  const { result, loading } = useBacktest();
  const [dataSource, setDataSource] = useState("demo");

  useEffect(() => {
    checkHealth().then((h) => setDataSource(h.data_source));
  }, []);

  return (
    <AppShell dataSource={dataSource}>
      <h2 className="mb-6 text-2xl font-bold">Backtest Results</h2>
      {loading ? (
        <div className="space-y-4">
          <Skeleton className="h-24 w-full" />
          <Skeleton className="h-80 w-full" />
        </div>
      ) : result ? (
        <BacktestResults result={result} />
      ) : (
        <Card className="flex h-48 items-center justify-center">
          <CardContent className="text-slate-400">No results yet — run a backtest from Dashboard</CardContent>
        </Card>
      )}
    </AppShell>
  );
}
