"use client";

import { Plus, Trash2 } from "lucide-react";
import type { BacktestRequest, FilterRule, RankingRule } from "@/types/backtest";

interface Props {
  config: BacktestRequest;
  onChange: (config: BacktestRequest) => void;
  metrics?: string[];
  onRun: () => void;
  loading: boolean;
}

const OPERATORS = [">", ">=", "<", "<=", "==", "!=", "between"] as const;

const DEFAULT_METRICS = [
  "market_cap_cr", "pe_ratio", "pb_ratio", "roe", "roce", "roa",
  "debt_to_equity", "current_ratio", "dividend_yield", "revenue_growth", "pat_margin", "pat",
];

export default function BacktestConfig({
  config,
  onChange,
  metrics = DEFAULT_METRICS,
  onRun,
  loading,
}: Props) {
  const update = (partial: Partial<BacktestRequest>) =>
    onChange({ ...config, ...partial });

  const addFilter = () => {
    update({
      filters: [
        ...config.filters,
        { metric: metrics[0] || "roce", operator: ">", value: 15 },
      ],
    });
  };

  const updateFilter = (index: number, filter: FilterRule) => {
    const filters = [...config.filters];
    filters[index] = filter;
    update({ filters });
  };

  const removeFilter = (index: number) => {
    update({ filters: config.filters.filter((_, i) => i !== index) });
  };

  const addRanking = () => {
    update({
      ranking_rules: [
        ...config.ranking_rules,
        { metric: metrics[0] || "roe", direction: "desc", weight: 1 },
      ],
    });
  };

  const updateRanking = (index: number, rule: RankingRule) => {
    const ranking_rules = [...config.ranking_rules];
    ranking_rules[index] = rule;
    update({ ranking_rules });
  };

  const removeRanking = (index: number) => {
    update({ ranking_rules: config.ranking_rules.filter((_, i) => i !== index) });
  };

  return (
    <div className="space-y-6">
      <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 className="mb-4 text-lg font-semibold text-slate-800">Backtest Parameters</h2>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
          <label className="block text-sm">
            <span className="text-slate-600">Start Date</span>
            <input
              type="date"
              value={config.start_date}
              onChange={(e) => update({ start_date: e.target.value })}
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-white"
            />
          </label>
          <label className="block text-sm">
            <span className="text-slate-600">End Date</span>
            <input
              type="date"
              value={config.end_date}
              onChange={(e) => update({ end_date: e.target.value })}
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-white"
            />
          </label>
          <label className="block text-sm">
            <span className="text-slate-600">Initial Capital (₹)</span>
            <input
              type="number"
              value={config.initial_capital}
              onChange={(e) => update({ initial_capital: Number(e.target.value) })}
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-white"
            />
          </label>
          <label className="block text-sm">
            <span className="text-slate-600">Portfolio Size</span>
            <input
              type="number"
              min={1}
              max={100}
              value={config.portfolio_size}
              onChange={(e) => update({ portfolio_size: Number(e.target.value) })}
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-white"
            />
          </label>
          <label className="block text-sm">
            <span className="text-slate-600">Rebalance Frequency</span>
            <select
              value={config.rebalance_frequency}
              onChange={(e) =>
                update({
                  rebalance_frequency: e.target.value as BacktestRequest["rebalance_frequency"],
                })
              }
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-white"
            >
              <option value="monthly">Monthly</option>
              <option value="quarterly">Quarterly</option>
              <option value="semiannual">Semiannual</option>
              <option value="yearly">Yearly</option>
              <option value="weekly">Weekly</option>
            </select>
          </label>
          <label className="block text-sm">
            <span className="text-slate-600">Position Sizing</span>
            <select
              value={config.position_sizing}
              onChange={(e) =>
                update({
                  position_sizing: e.target.value as BacktestRequest["position_sizing"],
                })
              }
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-white"
            >
              <option value="equal">Equal Weighted</option>
              <option value="market_cap">Market Cap Weighted</option>
              <option value="metric">Metric Weighted</option>
            </select>
          </label>
          {config.position_sizing === "metric" && (
            <label className="block text-sm">
              <span className="text-slate-600">Sizing Metric</span>
              <select
                value={config.sizing_metric || ""}
                onChange={(e) => update({ sizing_metric: e.target.value })}
                className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-white"
              >
                {metrics.map((m) => (
                  <option key={m} value={m}>
                    {m}
                  </option>
                ))}
              </select>
            </label>
          )}
          <label className="flex items-center gap-2 text-sm md:col-span-2">
            <input
              type="checkbox"
              checked={config.include_benchmark}
              onChange={(e) => update({ include_benchmark: e.target.checked })}
              className="rounded"
            />
            <span className="text-slate-600">Compare with Nifty 50 benchmark</span>
          </label>
        </div>
      </section>

      <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-slate-800">Filters (applied at start)</h2>
          <button
            onClick={addFilter}
            className="flex items-center gap-1 rounded-lg bg-slate-100 px-3 py-1.5 text-sm hover:bg-slate-200"
          >
            <Plus size={16} /> Add Filter
          </button>
        </div>
        {config.filters.length === 0 && (
          <p className="text-sm text-slate-500">No filters — entire universe will be used.</p>
        )}
        <div className="space-y-3">
          {config.filters.map((f, i) => (
            <div key={i} className="flex flex-wrap items-center gap-2">
              <select
                value={f.metric}
                onChange={(e) => updateFilter(i, { ...f, metric: e.target.value })}
                className="rounded-lg border border-slate-300 px-3 py-2 text-sm text-white"
              >
                {metrics.map((m) => (
                  <option key={m} value={m}>
                    {m}
                  </option>
                ))}
              </select>
              <select
                value={f.operator}
                onChange={(e) =>
                  updateFilter(i, {
                    ...f,
                    operator: e.target.value as FilterRule["operator"],
                  })
                }
                className="rounded-lg border border-slate-300 px-3 py-2 text-sm text-white"
              >
                {OPERATORS.map((op) => (
                  <option key={op} value={op}>
                    {op}
                  </option>
                ))}
              </select>
              {f.operator === "between" ? (
                <>
                  <input
                    type="number"
                    placeholder="Min"
                    value={Array.isArray(f.value) ? f.value[0] : 0}
                    onChange={(e) =>
                      updateFilter(i, {
                        ...f,
                        value: [Number(e.target.value), Array.isArray(f.value) ? f.value[1] : 0],
                      })
                    }
                    className="w-24 rounded-lg border border-slate-300 px-3 py-2 text-sm text-white"
                  />
                  <input
                    type="number"
                    placeholder="Max"
                    value={Array.isArray(f.value) ? f.value[1] : 0}
                    onChange={(e) =>
                      updateFilter(i, {
                        ...f,
                        value: [Array.isArray(f.value) ? f.value[0] : 0, Number(e.target.value)],
                      })
                    }
                    className="w-24 rounded-lg border border-slate-300 px-3 py-2 text-sm text-white"
                  />
                </>
              ) : (
                <input
                  type="number"
                  value={typeof f.value === "number" ? f.value : 0}
                  onChange={(e) => updateFilter(i, { ...f, value: Number(e.target.value) })}
                  className="w-28 rounded-lg border border-slate-300 px-3 py-2 text-sm text-white"
                />
              )}
              <button onClick={() => removeFilter(i)} className="text-red-500 hover:text-red-700">
                <Trash2 size={18} />
              </button>
            </div>
          ))}
        </div>
      </section>

      <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-slate-800">Ranking Rules</h2>
          <button
            onClick={addRanking}
            className="flex items-center gap-1 rounded-lg bg-slate-100 px-3 py-1.5 text-sm hover:bg-slate-200"
          >
            <Plus size={16} /> Add Rule
          </button>
        </div>
        <div className="space-y-3">
          {config.ranking_rules.map((r, i) => (
            <div key={i} className="flex flex-wrap items-center gap-2">
              <select
                value={r.metric}
                onChange={(e) => updateRanking(i, { ...r, metric: e.target.value })}
                className="rounded-lg border border-slate-300 px-3 py-2 text-sm text-white"
              >
                {metrics.map((m) => (
                  <option key={m} value={m}>
                    {m}
                  </option>
                ))}
              </select>
              <select
                value={r.direction}
                onChange={(e) =>
                  updateRanking(i, { ...r, direction: e.target.value as "asc" | "desc" })
                }
                className="rounded-lg border border-slate-300 px-3 py-2 text-sm text-white"
              >
                <option value="desc">Descending</option>
                <option value="asc">Ascending</option>
              </select>
              <input
                type="number"
                step={0.1}
                min={0}
                value={r.weight}
                onChange={(e) => updateRanking(i, { ...r, weight: Number(e.target.value) })}
                className="w-20 rounded-lg border border-slate-300 px-3 py-2 text-sm text-white"
                placeholder="Weight"
              />
              <button onClick={() => removeRanking(i)} className="text-red-500 hover:text-red-700">
                <Trash2 size={18} />
              </button>
            </div>
          ))}
        </div>
      </section>

      <button
        onClick={onRun}
        disabled={loading}
        className="w-full rounded-xl bg-indigo-600 py-3 font-semibold text-white hover:bg-indigo-700 disabled:opacity-50 md:w-auto md:px-12"
      >
        {loading ? "Running Backtest..." : "Run Backtest"}
      </button>
    </div>
  );
}
