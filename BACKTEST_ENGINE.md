# Backtest Engine

## Flow

1. **Initial filter** (start date only): Apply user filters to universe
2. **Rebalance dates**: Monthly / Quarterly / Semiannual / Yearly
3. **Point-in-time metrics**: Latest data ≤ rebalance date
4. **Composite ranking**: Weighted average of metric ranks
5. **Top N selection**: Portfolio size
6. **Position sizing**: Equal / Market Cap / Metric weight
7. **Execution**: Close price on rebalance date
8. **Daily MTM**: Mark-to-market between rebalances
9. **Compounding**: Full portfolio reinvested each rebalance

## No Look-Ahead Bias

- Filters use metrics where `as_of_date ≤ start_date`
- Rebalance ranking uses metrics where `as_of_date ≤ rebalance_date`
- Prices use `trade_date ≤ execution_date`

## Rebalance Frequencies

| User Value | Pandas Freq |
|------------|-------------|
| monthly | ME |
| quarterly | QE |
| semiannual | 6ME |
| yearly | YE |

## Performance Metrics

CAGR, Total Return, Sharpe, Sortino, Max Drawdown, Calmar, Volatility, Alpha, Beta (vs Nifty 50)

## Outputs

Equity curve, drawdown, rolling returns, monthly returns heatmap, portfolio logs, transactions, winners/losers
