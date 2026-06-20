"use client";

import { useEffect, useState } from "react";
import { toast } from "sonner";
import { AppShell } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { checkHealth } from "@/lib/api";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function DataPage() {
  const [health, setHealth] = useState<Record<string, unknown>>({});
  const [syncing, setSyncing] = useState(false);

  const load = () => checkHealth().then(setHealth);

  useEffect(() => {
    load();
  }, []);

  const syncData = async () => {
    setSyncing(true);
    toast.info("Fetching real data from Yahoo Finance — this may take 20-40 minutes...");
    try {
      const res = await fetch(`${API}/api/data/sync`, { method: "POST" });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Sync failed");
      toast.success("Data sync complete!");
      load();
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Sync failed");
    } finally {
      setSyncing(false);
    }
  };

  const stats = (health.stats as Record<string, number>) || {};
  const isReal = health.data_source === "postgresql";

  return (
    <AppShell dataSource={String(health.data_source || "demo")}>
      <h2 className="mb-6 text-2xl font-bold">Data Management</h2>

      <div className="mb-6 grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader><CardTitle>Data Source</CardTitle></CardHeader>
          <CardContent>
            <Badge variant={isReal ? "success" : "demo"} className="mb-2">
              {isReal ? "Yahoo Finance → PostgreSQL" : "Demo (run sync)"}
            </Badge>
            <p className="text-sm text-slate-500">Status: {String(health.status)}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>Stocks</CardTitle></CardHeader>
          <CardContent className="text-3xl font-bold">{stats.stocks ?? 0}</CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>Price Records</CardTitle></CardHeader>
          <CardContent className="text-3xl font-bold">{stats.prices ?? 0}</CardContent>
        </Card>
      </div>

      <Card className="mb-6">
        <CardHeader><CardTitle>Sync Real Data (Yahoo Finance API)</CardTitle></CardHeader>
        <CardContent className="space-y-4">
          <p className="text-sm text-slate-500">
            Fetches OHLCV prices, P&L, balance sheets, cash flows, and ratios for 110+ NSE stocks.
            Data is stored in PostgreSQL before any backtest runs.
          </p>
          <Button onClick={syncData} disabled={syncing}>
            {syncing ? "Syncing..." : "Sync Yahoo Finance Data"}
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>Database Tables</CardTitle></CardHeader>
        <CardContent className="grid grid-cols-2 gap-2 text-sm md:grid-cols-4">
          <div>Metrics: {stats.metrics ?? 0}</div>
          <div>Income Stmt: {stats.income_statements ?? 0}</div>
          <div>Companies: {stats.stocks ?? 0}</div>
          <div>Prices: {stats.prices ?? 0}</div>
        </CardContent>
      </Card>
    </AppShell>
  );
}
