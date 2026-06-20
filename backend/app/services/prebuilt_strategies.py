"""Prebuilt strategy templates for quick backtesting."""

from app.schemas.backtest import BacktestRequest, FilterRule, RankingRule

PREBUILT_STRATEGIES = [
    {
        "id": "quality_momentum",
        "name": "Quality Momentum",
        "description": "High ROCE stocks with positive PAT, equal-weighted, quarterly rebalance",
        "config": BacktestRequest(
            start_date="2018-01-01",
            end_date="2024-12-31",
            portfolio_size=20,
            rebalance_frequency="quarterly",
            position_sizing="equal",
            filters=[
                FilterRule(metric="roce", operator=">", value=15),
                FilterRule(metric="market_cap_cr", operator="between", value=[1000, 50000]),
            ],
            ranking_rules=[
                RankingRule(metric="roe", direction="desc", weight=0.5),
                RankingRule(metric="pe_ratio", direction="asc", weight=0.5),
            ],
        ),
    },
    {
        "id": "value_investing",
        "name": "Value Investing",
        "description": "Low PE, high ROE large caps, market cap weighted",
        "config": BacktestRequest(
            start_date="2018-01-01",
            end_date="2024-12-31",
            portfolio_size=15,
            rebalance_frequency="yearly",
            position_sizing="market_cap",
            filters=[
                FilterRule(metric="pe_ratio", operator=">", value=0),
                FilterRule(metric="pe_ratio", operator="<", value=25),
                FilterRule(metric="market_cap_cr", operator=">", value=5000),
            ],
            ranking_rules=[
                RankingRule(metric="pe_ratio", direction="asc", weight=0.6),
                RankingRule(metric="roe", direction="desc", weight=0.4),
            ],
        ),
    },
    {
        "id": "small_cap_growth",
        "name": "Small Cap Growth",
        "description": "Mid-small cap stocks ranked by revenue growth, ROCE-weighted",
        "config": BacktestRequest(
            start_date="2019-01-01",
            end_date="2024-12-31",
            portfolio_size=25,
            rebalance_frequency="quarterly",
            position_sizing="metric",
            sizing_metric="roce",
            filters=[
                FilterRule(metric="market_cap_cr", operator="between", value=[500, 5000]),
                FilterRule(metric="revenue_growth", operator=">", value=0.1),
            ],
            ranking_rules=[
                RankingRule(metric="revenue_growth", direction="desc", weight=0.5),
                RankingRule(metric="roce", direction="desc", weight=0.5),
            ],
        ),
    },
]
