"use client";

import { useEffect, useState } from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts";
import { toast } from "sonner";
import { AppShell } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useBacktest } from "@/context/backtest-context";
import { checkHealth, compareStrategies } from "@/lib/api";

export default function ComparePage() {
  const { config } = useBacktest();
  const [dataSource, setDataSource] = useState("demo");
  const [comparisons, setComparisons] = useState<
    { label: string; performance: Record<string, number>; equity_curve: { date: string; value: number }[] }[]
  >([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    checkHealth().then((h) => setDataSource(h.data_source));
  }, []);

  const runCompare = async () => {
    setLoading(true);
    try {
      const alt = {
        ...config,
        position_sizing: "market_cap" as const,
        rebalance_frequency: "yearly" as const,
      };
      const res = await compareStrategies([config, alt]);
      setComparisons(res.comparisons);
      toast.success("Comparison complete");
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Compare failed");
    } finally {
      setLoading(false);
    }
  };

  const chartData =
    comparisons[0]?.equity_curve.map((p, i) => ({
      date: p.date,
      strategy1: p.value,
      strategy2: comparisons[1]?.equity_curve[i]?.value,
    })) ?? [];

  return (
    <AppShell dataSource={dataSource}>
      <div className="mb-6 flex items-center justify-between">
        <h2 className="text-2xl font-bold">Strategy Comparison</h2>
        <Button onClick={runCompare} disabled={loading}>
          {loading ? "Comparing..." : "Compare Current vs Market-Cap Yearly"}
        </Button>
      </div>

      {comparisons.length >= 2 && (
        <>
          <div className="mb-6 grid gap-4 md:grid-cols-2">
            {comparisons.map((c) => (
              <Card key={c.label}>
                <CardHeader>
                  <CardTitle>{c.label}</CardTitle>
                </CardHeader>
                <CardContent className="grid grid-cols-2 gap-2 text-sm">
                  <div>CAGR: {c.performance.cagr}%</div>
                  <div>Sharpe: {c.performance.sharpe_ratio}</div>
                  <div>Max DD: {c.performance.max_drawdown}%</div>
                  <div>Volatility: {c.performance.volatility}%</div>
                </CardContent>
              </Card>
            ))}
          </div>
          <Card>
            <CardHeader>
              <CardTitle>Equity Curve Comparison</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={350}>
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" tickFormatter={(d) => d.slice(0, 7)} />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="strategy1" stroke="#4f46e5" dot={false} name="Strategy 1" />
                  <Line type="monotone" dataKey="strategy2" stroke="#10b981" dot={false} name="Strategy 2" />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </>
      )}
    </AppShell>
  );
}
