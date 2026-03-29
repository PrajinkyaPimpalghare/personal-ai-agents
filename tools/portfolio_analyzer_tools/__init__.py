"""
Portfolio Analyzer Tools - Comprehensive Python toolkit for stock analysis

This package provides efficient, deterministic calculations for portfolio analysis,
reducing token usage while maintaining analysis quality.

Modules:
- metrics: Financial metrics calculation (P/E, ROE, returns, etc.)
- technical_analysis: Technical indicators (RSI, MACD, Bollinger, ATR, EMA)
- scoring: Weighted scoring system (0-10 scale with 5 factors)
- risk_management: Position sizing, stop loss, portfolio heat
- data_cache: Smart caching for MCP calls and historical data
- output_formatter: Standardized analysis output templates
- portfolio_analyzer: Main orchestration class

Usage:
    from portfolio_analyzer_tools import PortfolioAnalyzer
    
    analyzer = PortfolioAnalyzer()
    analysis = analyzer.analyze_portfolio(holdings_data)
"""

from .metrics import (
    absolute_return,
    percentage_return,
    cagr,
    pe_ratio,
    pb_ratio,
    peg_ratio,
    dividend_yield,
    profit_margin,
    roe,
    roic,
    days_held,
    annualized_return,
)

from .technical_analysis import (
    calculate_rsi,
    calculate_macd,
    calculate_bollinger_bands,
    calculate_atr,
    calculate_ema,
    find_support_resistance,
    generate_technical_signal,
)

from .scoring import (
    calculate_fundamental_score,
    calculate_technical_score,
    calculate_sentiment_score,
    calculate_macro_score,
    calculate_debate_score,
    calculate_total_score_and_verdict,
)

from .risk_management import (
    calculate_position_size,
    calculate_atr_based_stop_loss,
    calculate_profit_targets,
    calculate_risk_reward_ratio,
    portfolio_heat_calculation,
    calculate_drawdown_from_peak,
    validate_position_sizing,
)

from .portfolio_analyzer import PortfolioAnalyzer

__version__ = "1.0.0"
__all__ = [
    "PortfolioAnalyzer",
    # Metrics
    "absolute_return",
    "percentage_return",
    "cagr",
    "pe_ratio",
    "pb_ratio",
    "peg_ratio",
    "dividend_yield",
    "profit_margin",
    "roe",
    "roic",
    "days_held",
    "annualized_return",
    # Technical
    "calculate_rsi",
    "calculate_macd",
    "calculate_bollinger_bands",
    "calculate_atr",
    "calculate_ema",
    "find_support_resistance",
    "generate_technical_signal",
    # Scoring
    "calculate_fundamental_score",
    "calculate_technical_score",
    "calculate_sentiment_score",
    "calculate_macro_score",
    "calculate_debate_score",
    "calculate_total_score_and_verdict",
    # Risk Management
    "calculate_position_size",
    "calculate_atr_based_stop_loss",
    "calculate_profit_targets",
    "calculate_risk_reward_ratio",
    "portfolio_heat_calculation",
    "calculate_drawdown_from_peak",
    "validate_position_sizing",
]
