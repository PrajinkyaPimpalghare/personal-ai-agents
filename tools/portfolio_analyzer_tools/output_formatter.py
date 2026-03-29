"""
Output Formatter Module - Standardized analysis output templates

Generates consistent, professional output formats that reduce token usage
by pre-formatting the analysis for the agent to enhance with narrative.

Templates:
- Portfolio overview table
- Individual stock analysis headers
- Technical verdict section
- Scoring breakdown
- Risk assessment template
- Bull/Bear debate template
"""

from typing import Dict, List, Any


def format_portfolio_overview(holdings: List[Dict]) -> str:
    """
    Format portfolio overview as professional table.
    
    Args:
        holdings: List of holding dicts with:
            - symbol, quantity, avg_price, last_price, pnl, day_change
    
    Returns:
        Formatted table string
    """
    lines = []
    lines.append("=" * 120)
    lines.append(f"{'STOCK':<12} {'QTY':<6} {'AVG COST':<12} {'CURRENT':<12} {'GAIN/LOSS':<15} {'%RET':<8} {'DAY CHG':<10}")
    lines.append("-" * 120)
    
    total_invested = 0
    total_current = 0
    total_gain = 0
    
    for h in holdings:
        symbol = h.get('symbol', 'N/A')[:12]
        qty = h.get('quantity', 0)
        avg_price = h.get('avg_price', 0)
        last_price = h.get('last_price', 0)
        pnl = h.get('pnl', 0)
        day_change = h.get('day_change', 0)
        
        invested = avg_price * qty
        current = last_price * qty
        pct_ret = ((current - invested) / invested * 100) if invested > 0 else 0
        
        pnl_color = "+" if pnl >= 0 else "-"
        lines.append(
            f"{symbol:<12} {qty:<6} ₹{avg_price:<11.2f} ₹{last_price:<11.2f} "
            f"{pnl_color}₹{abs(pnl):<14.0f} {pct_ret:>6.1f}% {day_change:>8.2f}%"
        )
        
        total_invested += invested
        total_current += current
        total_gain += pnl
    
    lines.append("-" * 120)
    total_pct = ((total_current - total_invested) / total_invested * 100) if total_invested > 0 else 0
    lines.append(
        f"{'TOTAL':<12} {'-':<6} ₹{total_invested:<11.0f} ₹{total_current:<11.0f} "
        f"+₹{total_gain:<14.0f} {total_pct:>6.1f}%"
    )
    lines.append("=" * 120)
    
    return "\n".join(lines)


def format_technical_verdict(indicators: Dict[str, Any]) -> str:
    """Format technical analysis verdict."""
    lines = []
    lines.append("\n## Technical Analysis (3-6 Month Outlook)")
    lines.append("-" * 80)
    
    lines.append(f"Current Trend: {indicators.get('trend', 'N/A')}")
    lines.append(f"EMA Status: {indicators.get('ema_status', 'N/A')}")
    lines.append(f"RSI (14): {indicators.get('rsi', 'N/A')} → {indicators.get('rsi_interpretation', 'N/A')}")
    lines.append(f"MACD: {indicators.get('macd', 'N/A')} vs Signal {indicators.get('signal', 'N/A')}")
    lines.append(f"Bollinger Bands: Price at {indicators.get('bb_position', 'N/A')}")
    lines.append(f"ATR: {indicators.get('atr', 'N/A')} ({indicators.get('atr_pct', 'N/A')}% volatility)")
    
    lines.append(f"\nResistance Levels: {indicators.get('resistance', 'N/A')}")
    lines.append(f"Support Levels: {indicators.get('support', 'N/A')}")
    
    lines.append(f"\nTechnical Signal: **{indicators.get('signal_verdict', 'HOLD')}**")
    lines.append(f"Entry Setup: {indicators.get('entry_setup', 'N/A')}")
    lines.append(f"Target: {indicators.get('target', 'N/A')}")
    
    return "\n".join(lines)


def format_scoring_breakdown(scores: Dict[str, float]) -> str:
    """Format weighted scoring breakdown."""
    lines = []
    lines.append("\n## Weighted Score & Verdict")
    lines.append("-" * 80)
    lines.append(f"Fundamental Score: {scores.get('fundamental', 5.0)}/10 (30% weight)")
    lines.append(f"Technical Score: {scores.get('technical', 5.0)}/10 (25% weight)")
    lines.append(f"Sentiment Score: {scores.get('sentiment', 5.0)}/10 (15% weight)")
    lines.append(f"Macro Score: {scores.get('macro', 5.0)}/10 (15% weight)")
    lines.append(f"Debate Score: {scores.get('debate', 5.0)}/10 (15% weight)")
    
    total_score = scores.get('total', 5.0)
    verdict = scores.get('verdict', 'HOLD')
    confidence = scores.get('confidence', 'MEDIUM')
    
    lines.append(f"\n**TOTAL SCORE: {total_score}/10**")
    lines.append(f"**Verdict: {verdict}**")
    lines.append(f"**Confidence: {confidence}**")
    
    return "\n".join(lines)


def format_risk_assessment(risk_data: Dict[str, Any]) -> str:
    """Format risk assessment section."""
    lines = []
    lines.append("\n## Risk Assessment")
    lines.append("-" * 80)
    
    lines.append(f"Entry: ₹{risk_data.get('entry', 'N/A')}")
    lines.append(f"Stop Loss: ₹{risk_data.get('stop_loss', 'N/A')} (ATR-based, {risk_data.get('atr_multiplier', 1.5)}x ATR)")
    lines.append(f"Risk per Share: ₹{risk_data.get('risk_per_share', 'N/A')}")
    
    lines.append(f"\nProfit Targets:")
    lines.append(f"  T1: ₹{risk_data.get('t1', 'N/A')} (1:2 ratio, Exit 30%)")
    lines.append(f"  T2: ₹{risk_data.get('t2', 'N/A')} (1:3 ratio, Exit 50%)")
    lines.append(f"  T3: ₹{risk_data.get('t3', 'N/A')} (1:4 ratio, Let run)")
    
    lines.append(f"\nPosition Sizing:")
    lines.append(f"  Quantity: {risk_data.get('quantity', 'N/A')} shares")
    lines.append(f"  Position Value: ₹{risk_data.get('position_value', 'N/A')}")
    lines.append(f"  Max Risk: ₹{risk_data.get('max_risk', 'N/A')}")
    
    return "\n".join(lines)


def format_bull_bear_template() -> str:
    """Return template for Bull vs. Bear debate section."""
    template = """
## Bull vs. Bear Debate

### 🟢 BULL ADVOCATE Case
[3-5 bullish arguments]
- Catalyst 1: [Event & Impact]
- Catalyst 2: [Event & Impact]
- Valuation: [Why attractive]
- Technical: [Strength signals]

**Bull Target**: ₹X (+Y%) in 6M | **Conviction**: HIGH/MEDIUM/LOW

### 🔴 BEAR ADVOCATE Case
[3-5 bearish arguments]
- Risk 1: [Event & Impact]
- Risk 2: [Event & Impact]
- Valuation: [Why overvalued]
- Technical: [Weakness signals]

**Bear Target**: ₹X (-Y%) in 3M | **Conviction**: HIGH/MEDIUM/LOW

### ⚖️ JUDGE Synthesis
**Debate Winner**: BULL/BEAR/TIE
**Judgment Confidence**: HIGH (80%+) / MEDIUM (60-80%) / LOW (<60%)
**Tiebreaker**: [What swung the decision]
**Biggest Tail Risk**: [What could flip verdict]
"""
    return template


def generate_analysis_report(
    stock_symbol: str,
    portfolio_data: Dict[str, Any],
    technical_data: Dict[str, Any],
    scores: Dict[str, float],
    risk_data: Dict[str, Any]
) -> str:
    """
    Generate complete pre-formatted analysis report.
    
    This combines all templates into single report that agent enhances.
    
    Args:
        stock_symbol: Stock ticker
        portfolio_data: Holding information
        technical_data: Technical indicators
        scores: Scoring breakdown
        risk_data: Risk management metrics
    
    Returns:
        Pre-formatted analysis report string
    """
    lines = []
    lines.append(f"\n{'=' * 80}")
    lines.append(f"{stock_symbol} - COMPREHENSIVE ANALYSIS")
    lines.append(f"{'=' * 80}\n")
    
    if portfolio_data:
        lines.append("### Portfolio Position")
        for key, value in portfolio_data.items():
            lines.append(f"- {key}: {value}")
        lines.append("")
    
    # Technical section
    if technical_data:
        lines.append(format_technical_verdict(technical_data))
        lines.append("")
    
    # Debate template
    lines.append(format_bull_bear_template())
    
    # Scoring section
    if scores:
        lines.append(format_scoring_breakdown(scores))
        lines.append("")
    
    # Risk section
    if risk_data:
        lines.append(format_risk_assessment(risk_data))
        lines.append("")
    
    return "\n".join(lines)
