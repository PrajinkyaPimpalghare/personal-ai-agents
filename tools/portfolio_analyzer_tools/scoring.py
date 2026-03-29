"""
Scoring Module - Weighted scoring system for investment recommendations

Implements the comprehensive 5-factor scoring framework:
1. Fundamental Score (30% weight) - P/E, ROE, Revenue Growth, Debt, Margins
2. Technical Score (25% weight) - RSI, MACD, Bollinger Bands, Support/Resistance, Volume
3. Sentiment Score (15% weight) - Analyst ratings, social sentiment, institutional activity
4. Macro Score (15% weight) - Oil prices, Rupee, RBI stance, FII flows, GDP data
5. Debate Score (15% weight) - Bull vs. Bear debate result

Final Score: 0-10 scale
Verdict: STRONG BUY / BUY / HOLD / SELL / STRONG SELL
Confidence: VERY HIGH / HIGH / MEDIUM

All scoring is deterministic once input metrics are provided.
"""

from typing import Dict, Tuple, List


def calculate_fundamental_score(
    pe_ratio: float,
    roe: float,
    revenue_growth: float,
    debt_to_equity: float = None,
    margin_trend: str = "stable"  # "improving", "stable", "declining"
) -> float:
    """
    Calculate Fundamental Score (0-10 scale).
    
    Components evaluated:
    - P/E Ratio: Valuation (lower is often better)
    - ROE: Return on Equity (higher is better)
    - Revenue Growth: % YoY growth (higher is better)
    - Debt/Equity: Leverage (lower is better)
    - Margin Trend: Direction of profitability
    
    Args:
        pe_ratio: Price-to-Earnings ratio
        roe: Return on Equity (%)
        revenue_growth: Revenue growth % YoY
        debt_to_equity: Debt-to-Equity ratio (optional)
        margin_trend: "improving", "stable", or "declining"
    
    Returns:
        Fundamental score 0-10
    
    Interpretation:
        9-10: Revenue >20% YoY, ROE >20%, P/E below peers, debt <20% equity
        7-8: Revenue 10-20%, ROE 15-20%, P/E at peers, manageable debt
        5-6: Revenue 5-10%, ROE 10-15%, P/E slightly above peers
        3-4: Revenue flat, ROE <10%, P/E above peers, high debt
        0-2: Revenue declining, Negative ROE, P/E overvalued, debt crisis
    
    Example:
        >>> score = calculate_fundamental_score(
        ...     pe_ratio=20, roe=18, revenue_growth=12, 
        ...     debt_to_equity=0.5, margin_trend="improving"
        ... )
        >>> print(score)  # e.g., 7.5
    """
    score = 5.0  # Base score
    
    # P/E Ratio Scoring (typical peer average 18-22x)
    if pe_ratio < 12:
        score += 2.0  # Undervalued
    elif pe_ratio < 15:
        score += 1.5
    elif pe_ratio < 18:
        score += 1.0
    elif pe_ratio < 25:
        score += 0.0  # Fair valued
    else:
        score -= 1.0  # Overvalued
    
    # ROE Scoring
    if roe > 20:
        score += 2.0
    elif roe > 15:
        score += 1.5
    elif roe > 10:
        score += 1.0
    elif roe > 5:
        score += 0.0
    else:
        score -= 1.5
    
    # Revenue Growth Scoring
    if revenue_growth > 20:
        score += 2.0
    elif revenue_growth > 15:
        score += 1.5
    elif revenue_growth > 10:
        score += 1.0
    elif revenue_growth > 5:
        score += 0.5
    elif revenue_growth > 0:
        score += 0.0
    else:
        score -= 2.0  # Declining revenue
    
    # Debt/Equity Scoring
    if debt_to_equity is not None:
        if debt_to_equity < 0.3:
            score += 1.0
        elif debt_to_equity < 0.8:
            score += 0.5
        elif debt_to_equity < 1.5:
            score += 0.0
        else:
            score -= 1.0
    
    # Margin Trend
    if margin_trend == "improving":
        score += 0.5
    elif margin_trend == "declining":
        score -= 1.0
    
    return round(max(0, min(10, score)), 1)


def calculate_technical_score(
    rsi: float,
    macd_histogram: float,
    bollinger_position: str = "middle",  # "upper", "middle", "lower"
    support_resistance_status: str = "holding",  # "breaking_up", "holding", "breaking_down"
    volume_confirmation: bool = True,
    trend_ema: str = "uptrend"  # "uptrend", "neutral", "downtrend"
) -> float:
    """
    Calculate Technical Score (0-10 scale).
    
    Components:
    - RSI: Momentum (50-70 bullish, <30 oversold)
    - MACD: Trend confirmation (positive histogram bullish)
    - Bollinger Bands: Volatility and mean reversion
    - Support/Resistance: Price action and strength
    - Volume: Confirmation of moves
    - Trend (EMA): Long-term direction
    
    Args:
        rsi: RSI value (0-100)
        macd_histogram: MACD histogram value
        bollinger_position: Position relative to bands
        support_resistance_status: Current price action
        volume_confirmation: True if volume confirms move
        trend_ema: Direction of EMA(20/50/200)
    
    Returns:
        Technical score 0-10
    
    Example:
        >>> score = calculate_technical_score(
        ...     rsi=65, macd_histogram=0.5,
        ...     bollinger_position="middle",
        ...     support_resistance_status="breaking_up",
        ...     volume_confirmation=True,
        ...     trend_ema="uptrend"
        ... )
        >>> print(score)  # e.g., 7.8
    """
    score = 5.0  # Base
    
    # RSI Scoring
    if rsi > 70:
        score -= 1.0  # Overbought risk
    elif rsi > 50:
        score += 1.5  # Bullish momentum
    elif rsi > 40:
        score += 0.5  # Mild bullish
    elif rsi < 30:
        score += 1.0  # Oversold bounce potential
    elif rsi < 40:
        score -= 1.0  # Bearish weakness
    
    # MACD Scoring
    if macd_histogram > 0.5:
        score += 2.0  # Strong bullish
    elif macd_histogram > 0:
        score += 1.0  # Mild bullish
    elif macd_histogram < -0.5:
        score -= 2.0  # Strong bearish
    elif macd_histogram < 0:
        score -= 1.0  # Mild bearish
    
    # Bollinger Bands Scoring
    if bollinger_position == "upper":
        score -= 0.5  # Overbought
    elif bollinger_position == "lower":
        score += 1.0  # Oversold, bounce potential
    elif bollinger_position == "middle":
        score += 0.0  # Neutral
    
    # Support/Resistance Scoring
    if support_resistance_status == "breaking_up":
        score += 1.5  # Positive breakout
    elif support_resistance_status == "holding":
        score += 0.0  # Neutral
    elif support_resistance_status == "breaking_down":
        score -= 1.5  # Negative breakdown
    
    # Volume Confirmation
    if volume_confirmation:
        score += 0.5
    else:
        score -= 0.5
    
    # Trend (EMA alignment)
    if trend_ema == "uptrend":
        score += 1.5
    elif trend_ema == "downtrend":
        score -= 1.5
    # neutral adds 0
    
    return round(max(0, min(10, score)), 1)


def calculate_sentiment_score(
    analyst_upgrades_downgrades_net: int = 0,  # +2 for upgrade, -2 for downgrade
    retail_sentiment: str = "neutral",  # "bullish", "neutral", "bearish"
    institutional_activity: str = "neutral",  # "buying", "neutral", "selling"
    news_tone: str = "neutral",  # "very_positive", "positive", "neutral", "negative", "very_negative"
    insider_activity: str = "neutral"  # "buying", "neutral", "selling"
) -> float:
    """
    Calculate Sentiment Score (0-10 scale).
    
    Components:
    - Analyst upgrades/downgrades: Expert consensus
    - Retail sentiment: Social media & forums
    - Institutional activity: Big money positioning
    - News tone: Recent company/sector news
    - Insider activity: Management buying/selling
    
    Args:
        analyst_upgrades_downgrades_net: Net score (+2 per upgrade, -2 per downgrade)
        retail_sentiment: "bullish" / "neutral" / "bearish"
        institutional_activity: "buying" / "neutral" / "selling"
        news_tone: "very_positive" / "positive" / "neutral" / "negative" / "very_negative"
        insider_activity: "buying" / "neutral" / "selling"
    
    Returns:
        Sentiment score 0-10
    
    Example:
        >>> score = calculate_sentiment_score(
        ...     analyst_upgrades_downgrades_net=4,  # 2 upgrades
        ...     retail_sentiment="bullish",
        ...     institutional_activity="buying",
        ...     news_tone="positive"
        ... )
        >>> print(score)  # e.g., 7.5
    """
    score = 5.0  # Base
    
    # Analyst Sentiment
    score += max(-1.0, min(1.0, analyst_upgrades_downgrades_net / 4))
    
    # Retail Sentiment
    if retail_sentiment == "bullish":
        score += 1.5
    elif retail_sentiment == "bearish":
        score -= 1.5
    
    # Institutional Activity
    if institutional_activity == "buying":
        score += 1.5
    elif institutional_activity == "selling":
        score -= 1.5
    
    # News Tone
    if news_tone == "very_positive":
        score += 2.0
    elif news_tone == "positive":
        score += 1.0
    elif news_tone == "negative":
        score -= 1.0
    elif news_tone == "very_negative":
        score -= 2.0
    
    # Insider Activity
    if insider_activity == "buying":
        score += 1.0
    elif insider_activity == "selling":
        score -= 1.0
    
    return round(max(0, min(10, score)), 1)


def calculate_macro_score(
    oil_price_wti: float = 100,
    rupee_level: float = 84,  # ₹/USD
    rbi_stance: str = "neutral",  # "aggressive_hike", "hiking", "neutral", "cutting"
    fii_flow_status: str = "neutral",  # "inflows", "neutral", "outflows"
    gdp_growth: float = 5.5,
    inflation_level: float = 5.5
) -> float:
    """
    Calculate Macro Score (0-10 scale) - Indian market specific.
    
    Components:
    - Oil Prices: Impact on inflation, costs, economic growth
    - Rupee Strength: Impact on exporters/importers, FII flows
    - RBI Stance: Monetary policy impact on growth and rates
    - FII Flows: Foreign liquidity for markets
    - GDP Growth: Economic health
    - Inflation: Cost pressures on companies
    
    Args:
        oil_price_wti: WTI oil price ($/barrel)
        rupee_level: Rupee level (₹/USD)
        rbi_stance: "aggressive_hike" / "hiking" / "neutral" / "cutting"
        fii_flow_status: "inflows" / "neutral" / "outflows"
        gdp_growth: Real GDP growth rate (%)
        inflation_level: Inflation rate (%)
    
    Returns:
        Macro score 0-10
    
    Interpretation:
        Oil $50-90 (benign)
        Rupee ₹82-83 (strong)
        RBI cutting (favorable)
        FII inflows (positive)
        GDP >6% (good)
        Inflation 3-5% (comfortable)
    
    Example:
        >>> score = calculate_macro_score(
        ...     oil_price_wti=95, rupee_level=83.5,
        ...     rbi_stance="neutral", fii_flow_status="inflows",
        ...     gdp_growth=6.2, inflation_level=4.5
        ... )
        >>> print(score)  # e.g., 7.8
    """
    score = 5.0  # Base
    
    # Oil Price Impact
    if oil_price_wti < 60:
        score += 1.5  # Very favorable
    elif oil_price_wti < 90:
        score += 1.0  # Favorable
    elif oil_price_wti < 120:
        score += 0.0  # Neutral
    elif oil_price_wti < 150:
        score -= 1.0  # Headwind
    else:
        score -= 2.0  # Major headwind (war premium)
    
    # Rupee Strength
    if rupee_level < 83:
        score += 1.0  # Strong rupee (good for importers, FII)
    elif rupee_level < 85:
        score += 0.5  # Moderate
    elif rupee_level < 87:
        score -= 0.5  # Weak
    else:
        score -= 1.5  # Very weak
    
    # RBI Stance
    if rbi_stance == "cutting":
        score += 1.5  # Supportive for growth
    elif rbi_stance == "neutral":
        score += 0.0
    elif rbi_stance == "hiking":
        score -= 1.0
    elif rbi_stance == "aggressive_hike":
        score -= 1.5
    
    # FII Flows
    if fii_flow_status == "inflows":
        score += 1.5
    elif fii_flow_status == "outflows":
        score -= 1.5
    
    # GDP Growth
    if gdp_growth > 6:
        score += 1.0
    elif gdp_growth > 4:
        score += 0.5
    elif gdp_growth < 2:
        score -= 1.5
    
    # Inflation
    if inflation_level > 6:
        score -= 1.0  # High inflation pressure
    elif inflation_level > 4:
        score -= 0.5
    elif inflation_level < 3:
        score += 0.5  # Well controlled
    
    return round(max(0, min(10, score)), 1)


def calculate_debate_score(
    bull_points_won: int,
    bear_points_won: int,
    bull_conviction: str = "medium",  # "very_high", "high", "medium", "low"
    bear_conviction: str = "medium"
) -> float:
    """
    Calculate Debate Score based on Bull vs. Bear debate outcome.
    
    The Bull and Bear advocates make their cases, and the Judge determines
    which side has the stronger arguments.
    
    Args:
        bull_points_won: Number of factors won by bull case (0-5)
        bear_points_won: Number of factors won by bear case (0-5)
        bull_conviction: Strength of bull conviction
        bear_conviction: Strength of bear conviction
    
    Returns:
        Debate score 0-10
    
    Scoring Logic:
        - Bull wins 5 factors: 9.5/10
        - Bull wins 4 factors: 7.5/10
        - Split 2-2 or 3-3: 5.0/10
        - Bear wins 4 factors: 2.5/10
        - Bear wins 5 factors: 0.5/10
    
    Example:
        >>> score = calculate_debate_score(
        ...     bull_points_won=4, bear_points_won=1,
        ...     bull_conviction="high", bear_conviction="low"
        ... )
        >>> print(score)  # e.g., 7.8
    """
    conviction_multiplier = {
        "very_high": 1.0,
        "high": 0.9,
        "medium": 0.75,
        "low": 0.6
    }
    
    # Base score from points
    net_points = bull_points_won - bear_points_won
    
    if net_points >= 4:
        base_score = 9.0
    elif net_points >= 3:
        base_score = 7.5
    elif net_points >= 1:
        base_score = 6.5
    elif net_points >= -1:
        base_score = 5.0
    elif net_points >= -3:
        base_score = 3.5
    elif net_points >= -4:
        base_score = 2.5
    else:
        base_score = 1.0
    
    # Apply conviction multipliers
    if bull_points_won > bear_points_won:
        multiplier = conviction_multiplier[bull_conviction]
    else:
        multiplier = conviction_multiplier[bear_conviction]
    
    final_score = base_score * multiplier
    return round(max(0, min(10, final_score)), 1)


def calculate_total_score_and_verdict(
    fundamental_score: float,
    technical_score: float,
    sentiment_score: float,
    macro_score: float,
    debate_score: float,
    weights: Dict[str, float] = None
) -> Tuple[float, str, str]:
    """
    Calculate total weighted score and generate verdict.
    
    Default weights:
    - Fundamental: 30%
    - Technical: 25%
    - Sentiment: 15%
    - Macro: 15%
    - Debate: 15%
    
    Args:
        fundamental_score: Fundamental score (0-10)
        technical_score: Technical score (0-10)
        sentiment_score: Sentiment score (0-10)
        macro_score: Macro score (0-10)
        debate_score: Debate score (0-10)
        weights: Optional custom weights dict
    
    Returns:
        Tuple of (Total Score, Verdict, Confidence)
        
        Verdicts:
        - 8.5-10.0: STRONG BUY (VERY HIGH confidence)
        - 7.0-8.4: BUY (HIGH confidence)
        - 5.5-6.9: HOLD (MEDIUM confidence)
        - 4.0-5.4: SELL (HIGH confidence)
        - 0.0-3.9: STRONG SELL (VERY HIGH confidence)
    
    Example:
        >>> total, verdict, confidence = calculate_total_score_and_verdict(
        ...     fundamental_score=7.5,
        ...     technical_score=7.0,
        ...     sentiment_score=7.5,
        ...     macro_score=8.0,
        ...     debate_score=7.5
        ... )
        >>> print(f"{verdict} ({confidence})")  # e.g., "BUY (HIGH)"
    """
    if weights is None:
        weights = {
            "fundamental": 0.30,
            "technical": 0.25,
            "sentiment": 0.15,
            "macro": 0.15,
            "debate": 0.15
        }
    
    total_score = (
        fundamental_score * weights["fundamental"] +
        technical_score * weights["technical"] +
        sentiment_score * weights["sentiment"] +
        macro_score * weights["macro"] +
        debate_score * weights["debate"]
    )
    
    total_score = round(total_score, 1)
    
    # Determine verdict
    if total_score >= 8.5:
        verdict = "STRONG BUY"
        confidence = "🔴 VERY HIGH (90%+)"
    elif total_score >= 7.0:
        verdict = "BUY"
        confidence = "🟠 HIGH (75-90%)"
    elif total_score >= 5.5:
        verdict = "HOLD"
        confidence = "🟡 MEDIUM (60-75%)"
    elif total_score >= 4.0:
        verdict = "SELL"
        confidence = "🟠 HIGH (75-90%)"
    else:
        verdict = "STRONG SELL"
        confidence = "🔴 VERY HIGH (90%+)"
    
    return total_score, verdict, confidence
