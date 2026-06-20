"use client";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
  AreaChart,
  Area,
  BarChart,
  Bar,
  Cell,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { formatCurrency } from "@/lib/utils";
import type { BacktestResult } from "@/types/backtest";

export function BacktestResults({ result }: { result: BacktestResult }) {
  if (!result.success) {
    return (
      <Card className="border-red-200 bg-red-50 dark:border-red-900 dark:bg-red-950/30">
        <CardContent className="p-6 text-red-700 dark:text-red-400">
          {result.message || "Backtest failed"}
        </CardContent>
      </Card>
    );
  }

  const perf = result.performance;
  const metrics = [
    { label: "Total Return", value: `${perf.total_return}%`, color: "text-indigo-600" },
    { label: "CAGR", value: `${perf.cagr}%`, color: "text-emerald-600" },
    { label: "Sharpe", value: perf.sharpe_ratio, color: "text-blue-600" },
    { label: "Sortino", value: perf.sortino_ratio, color: "text-blue-500" },
    { label: "Max Drawdown", value: `${perf.max_drawdown}%`, color: "text-red-600" },
    { label: "Volatility", value: `${perf.volatility}%`, color: "text-amber-600" },
    { label: "Calmar", value: perf.calmar_ratio, color: "text-purple-600" },
    { label: "Final Value", value: formatCurrency(perf.final_value), color: "text-slate-800 dark:text-slate-200" },
  ];
  if (perf.benchmark_cagr !== undefined) {
    metrics.push({ label: "Benchmark CAGR", value: `${perf.benchmark_cagr}%`, color: "text-slate-600" });
  }
  if (perf.alpha !== undefined) {
    metrics.push({ label: "Alpha", value: `${perf.alpha}%`, color: "text-emerald-600" });
  }
  if (perf.beta !== undefined) {
    metrics.push({ label: "Beta", value: String(perf.beta), color: "text-slate-600" });
  }

  const equityData = result.equity_curve.map((p) => ({
    date: p.date,
    portfolio: p.value,
    benchmark: result.benchmark_curve.find((b) => b.date === p.date)?.value,
  }));

  const heatmapColors = (v: number) =>
    v > 5 ? "#10b981" : v > 0 ? "#86efac" : v > -5 ? "#fca5a5" : "#ef4444";

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
        {metrics.map((m) => (
          <Card key={m.label}>
            <CardContent className="p-4">
              <p className="text-xs text-slate-500">{m.label}</p>
              <p className={`mt-1 text-xl font-bold ${m.color}`}>{m.value}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Equity Curve</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={320}>
            <LineChart data={equityData}>
              <CartesianGrid strokeDasharray="3 3" className="stroke-slate-200 dark:stroke-slate-700" />
              <XAxis dataKey="date" tick={{ fontSize: 11 }} tickFormatter={(d) => d.slice(0, 7)} />
              <YAxis tick={{ fontSize: 11 }} tickFormatter={(v) => `₹${(v / 1e5).toFixed(0)}L`} />
              <Tooltip formatter={(v) => [`₹${Number(v).toLocaleString()}`, ""]} />
              <Legend />
              <Line type="monotone" dataKey="portfolio" stroke="#4f46e5" strokeWidth={2} dot={false} name="Portfolio" />
              {result.benchmark_curve.length > 0 && (
                <Line type="monotone" dataKey="benchmark" stroke="#94a3b8" strokeWidth={1.5} dot={false} strokeDasharray="5 5" name="Nifty 50" />
              )}
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Drawdown</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={220}>
              <AreaChart data={result.drawdown}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" tickFormatter={(d) => d.slice(0, 7)} />
                <YAxis tickFormatter={(v) => `${v}%`} />
                <Tooltip formatter={(v) => [`${Number(v).toFixed(2)}%`, "Drawdown"]} />
                <Area type="monotone" dataKey="value" stroke="#ef4444" fill="#fecaca" />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Monthly Returns</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={result.monthly_returns?.slice(-24) ?? []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" tick={{ fontSize: 10 }} />
                <YAxis tickFormatter={(v) => `${v}%`} />
                <Tooltip formatter={(v) => [`${Number(v).toFixed(2)}%`, "Return"]} />
                <Bar dataKey="return">
                  {(result.monthly_returns?.slice(-24) ?? []).map((entry, i) => (
                    <Cell key={i} fill={heatmapColors(entry.return)} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="text-emerald-700">Top Winners</CardTitle>
          </CardHeader>
          <CardContent>
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left text-slate-500">
                  <th className="pb-2">Symbol</th>
                  <th className="pb-2">Return</th>
                  <th className="pb-2">Periods</th>
                </tr>
              </thead>
              <tbody>
                {result.top_winners.map((w) => (
                  <tr key={w.symbol} className="border-b border-slate-100 dark:border-slate-800">
                    <td className="py-2 font-medium">{w.symbol}</td>
                    <td className="py-2 text-emerald-600">{w.avg_return}%</td>
                    <td className="py-2">{w.periods}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-red-700">Top Losers</CardTitle>
          </CardHeader>
          <CardContent>
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left text-slate-500">
                  <th className="pb-2">Symbol</th>
                  <th className="pb-2">Return</th>
                  <th className="pb-2">Periods</th>
                </tr>
              </thead>
              <tbody>
                {result.top_losers.map((l) => (
                  <tr key={l.symbol} className="border-b border-slate-100 dark:border-slate-800">
                    <td className="py-2 font-medium">{l.symbol}</td>
                    <td className="py-2 text-red-600">{l.avg_return}%</td>
                    <td className="py-2">{l.periods}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Rebalance History</CardTitle>
        </CardHeader>
        <CardContent className="max-h-80 overflow-y-auto">
          {result.portfolio_logs.map((log) => (
            <div key={log.date} className="mb-4 border-b border-slate-100 pb-3 dark:border-slate-800">
              <p className="font-medium">
                {log.date} — {formatCurrency(log.portfolio_value)}
              </p>
              <div className="mt-2 flex flex-wrap gap-1.5">
                {log.holdings.map((h) => (
                  <span key={h.symbol} className="rounded-full bg-slate-100 px-2 py-0.5 text-xs dark:bg-slate-800">
                    {h.symbol} ({h.weight}%)
                  </span>
                ))}
              </div>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}
