export interface FilterRule {
  metric: string;
  operator: ">" | ">=" | "<" | "<=" | "==" | "!=" | "between";
  value: number | number[];
}

export interface RankingRule {
  metric: string;
  direction: "asc" | "desc";
  weight: number;
}

export interface BacktestRequest {
  start_date: string;
  end_date: string;
  initial_capital: number;
  portfolio_size: number;
  rebalance_frequency: "monthly" | "quarterly" | "semiannual" | "yearly" | "weekly";
  position_sizing: "equal" | "market_cap" | "metric";
  sizing_metric?: string | null;
  filters: FilterRule[];
  ranking_rules: RankingRule[];
  include_benchmark: boolean;
}

export interface BacktestResult {
  success: boolean;
  message?: string;
  data_source?: string;
  performance: Record<string, number>;
  equity_curve: { date: string; value: number }[];
  drawdown: { date: string; value: number }[];
  rolling_returns: { date: string; value: number }[];
  monthly_returns: { month: string; return: number }[];
  benchmark_curve: { date: string; value: number }[];
  portfolio_logs: {
    date: string;
    portfolio_value: number;
    holdings: { symbol: string; weight: number; price: number; shares: number }[];
  }[];
  transactions: {
    date: string;
    symbol: string;
    action: string;
    shares: number;
    price: number;
    weight_pct: number;
  }[];
  top_winners: { symbol: string; avg_return: number; periods: number }[];
  top_losers: { symbol: string; avg_return: number; periods: number }[];
  config_summary: Record<string, unknown>;
}

export interface PrebuiltStrategy {
  id: string;
  name: string;
  description: string;
  config: BacktestRequest;
}
