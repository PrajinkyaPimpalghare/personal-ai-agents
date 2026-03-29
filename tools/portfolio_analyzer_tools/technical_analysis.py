"""
Technical Analysis Module - Calculate technical indicators for stock analysis

Implements 6 core technical indicators:
1. RSI (Relative Strength Index) - Momentum & overbought/oversold
2. MACD (Moving Average Convergence Divergence) - Trend & momentum
3. Bollinger Bands - Volatility & mean reversion
4. ATR (Average True Range) - Volatility measurement
5. EMA (Exponential Moving Average) - Trend identification (20/50/200)
6. Support & Resistance - Key price levels

These calculations are deterministic and designed for fast computation with 2-year historical data.
"""

from typing import List, Tuple, Dict, Optional
from collections import deque


def calculate_rsi(closes: List[float], period: int = 14) -> float:
    """
    Calculate Relative Strength Index (14-period default).
    
    Formula: RSI = 100 - (100 / (1 + RS)) where RS = Avg Gain / Avg Loss
    
    Args:
        closes: List of closing prices (oldest first)
        period: RSI period (default 14)
    
    Returns:
        RSI value (0-100)
    
    Interpretation:
        > 70: Overbought (potential pullback)
        50-70: Strong uptrend
        40-60: Neutral
        30-50: Bearish weakness
        < 30: Oversold (potential bounce)
    
    Example:
        >>> closes = [100, 102, 101, 103, 105, ...]  # 50+ candles
        >>> calculate_rsi(closes)
        65.3
    """
    if len(closes) < period + 1:
        return 50.0  # Neutral if insufficient data
    
    gains = []
    losses = []
    
    for i in range(1, len(closes)):
        change = closes[i] - closes[i - 1]
        if change > 0:
            gains.append(change)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(change))
    
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    
    if avg_loss == 0:
        return 100.0 if avg_gain > 0 else 50.0
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return round(rsi, 2)


def calculate_macd(closes: List[float], fast: int = 12, slow: int = 26, signal_period: int = 9) -> Tuple[float, float, float]:
    """
    Calculate MACD (Moving Average Convergence Divergence).
    
    Formula:
    - MACD = EMA(12) - EMA(26)
    - Signal Line = EMA(9) of MACD
    - Histogram = MACD - Signal Line
    
    Args:
        closes: List of closing prices (oldest first)
        fast: Fast EMA period (default 12)
        slow: Slow EMA period (default 26)
        signal_period: Signal line EMA period (default 9)
    
    Returns:
        Tuple of (MACD, Signal Line, Histogram)
    
    Interpretation:
        MACD > Signal: Bullish (uptrend momentum)
        MACD < Signal: Bearish (downtrend momentum)
        Positive Histogram: Bullish momentum
        Negative Histogram: Bearish momentum
        Crossing: Signal line crossover = trading signal
    
    Example:
        >>> closes = [100, 102, 101, ..., 105]  # 50+ candles
        >>> macd, signal, histogram = calculate_macd(closes)
        >>> print(f"MACD: {macd}, Signal: {signal}, Histogram: {histogram}")
    """
    if len(closes) < slow + signal_period:
        return 0.0, 0.0, 0.0  # Insufficient data
    
    ema_fast = calculate_ema(closes, fast)
    ema_slow = calculate_ema(closes, slow)
    macd = round(ema_fast - ema_slow, 4)
    
    # Calculate MACD EMA for signal line
    # Need historical MACD values for proper calculation
    macd_values = []
    for i in range(slow - 1, len(closes)):
        subset = closes[i - slow + 1:i + 1]
        ema_f = calculate_ema(subset, fast)
        ema_s = calculate_ema(subset, slow)
        macd_values.append(ema_f - ema_s)
    
    if len(macd_values) < signal_period:
        signal = macd
        histogram = 0.0
    else:
        signal = round(calculate_ema(macd_values, signal_period), 4)
        histogram = round(macd - signal, 4)
    
    return macd, signal, histogram


def calculate_ema(closes: List[float], period: int) -> float:
    """
    Calculate Exponential Moving Average.
    
    Formula: EMA = Price(t) × Multiplier + EMA(t-1) × (1 - Multiplier)
    where Multiplier = 2 / (Period + 1)
    
    Args:
        closes: List of closing prices (oldest first)
        period: EMA period (e.g., 20, 50, 200)
    
    Returns:
        EMA value (latest)
    
    Example:
        >>> ema_20 = calculate_ema(closes, 20)
        >>> ema_50 = calculate_ema(closes, 50)
        >>> ema_200 = calculate_ema(closes, 200)
    """
    if len(closes) < period:
        return sum(closes) / len(closes)  # Return SMA if insufficient data
    
    multiplier = 2 / (period + 1)
    ema = sum(closes[:period]) / period  # Initial SMA
    
    for price in closes[period:]:
        ema = price * multiplier + ema * (1 - multiplier)
    
    return round(ema, 2)


def calculate_bollinger_bands(
    closes: List[float],
    sma_period: int = 20,
    std_dev_multiplier: float = 2
) -> Tuple[float, float, float]:
    """
    Calculate Bollinger Bands (20-period SMA, 2 std dev default).
    
    Components:
    - Middle Band = SMA(20)
    - Upper Band = SMA(20) + (2 × StdDev)
    - Lower Band = SMA(20) - (2 × StdDev)
    
    Args:
        closes: List of closing prices (oldest first)
        sma_period: Moving average period (default 20)
        std_dev_multiplier: Standard deviation multiplier (default 2)
    
    Returns:
        Tuple of (Upper Band, Middle Band, Lower Band)
    
    Interpretation:
        Price at Upper: Overbought (potential pullback)
        Price at Lower: Oversold (potential bounce)
        Band Squeeze: Low volatility, breakout coming
        Band Expansion: High volatility, trend accelerating
    
    Example:
        >>> closes = [100, 102, 101, ...]  # 30+ candles
        >>> upper, middle, lower = calculate_bollinger_bands(closes)
    """
    if len(closes) < sma_period:
        return 0.0, 0.0, 0.0
    
    # Calculate SMA (middle band)
    sma = sum(closes[-sma_period:]) / sma_period
    middle_band = round(sma, 2)
    
    # Calculate standard deviation
    variance = sum((x - sma) ** 2 for x in closes[-sma_period:]) / sma_period
    std_dev = variance ** 0.5
    
    upper_band = round(sma + (std_dev_multiplier * std_dev), 2)
    lower_band = round(sma - (std_dev_multiplier * std_dev), 2)
    
    return upper_band, middle_band, lower_band


def calculate_atr(
    highs: List[float],
    lows: List[float],
    closes: List[float],
    period: int = 14
) -> float:
    """
    Calculate Average True Range (volatility indicator).
    
    True Range = max(High - Low, |High - Close(prev)|, |Low - Close(prev)|)
    ATR = Average of True Ranges
    
    Args:
        highs: List of high prices (oldest first)
        lows: List of low prices (oldest first)
        closes: List of close prices (oldest first)
        period: ATR period (default 14)
    
    Returns:
        ATR value (never negative)
    
    Interpretation:
        High ATR (> 3% of price): High volatility
        Low ATR (< 1% of price): Low volatility
        Rising ATR: Volatility increasing, trend accelerating
        Falling ATR: Volatility decreasing, trend weakening
    
    Use for:
        - Position sizing: Reduce size if high ATR
        - Stop loss: Entry - (ATR × multiplier)
        - Dynamic stops: Follow ATR movements
    
    Example:
        >>> atr = calculate_atr(highs, lows, closes)
        >>> atr_pct = (atr / closes[-1]) * 100  # ATR as % of price
    """
    if len(closes) < period:
        return 0.0
    
    true_ranges = []
    
    for i in range(1, len(closes)):
        high_low = highs[i] - lows[i]
        high_close = abs(highs[i] - closes[i - 1])
        low_close = abs(lows[i] - closes[i - 1])
        tr = max(high_low, high_close, low_close)
        true_ranges.append(tr)
    
    atr = sum(true_ranges[-period:]) / period
    return round(atr, 2)


def find_support_resistance(
    prices: List[float],
    lookback_period: int = 100,
    num_levels: int = 3
) -> Tuple[List[float], List[float]]:
    """
    Find support and resistance levels from historical price data.
    
    Uses swing highs and lows to identify key price levels.
    
    Args:
        prices: List of closing prices (oldest first)
        lookback_period: Period to search for levels (default 100 candles)
        num_levels: Number of levels to return (default top 3)
    
    Returns:
        Tuple of (Support Levels, Resistance Levels) sorted ascending
    
    Interpretation:
        Support: Price level where buying pressure emerges (bounce point)
        Resistance: Price level where selling pressure emerges (barrier)
        Strong Level: Tested multiple times without breaking
        Broken Level: May not hold again
    
    Use for:
        - Entry points: Buy at support
        - Exit points: Sell at resistance
        - Stop loss: Below support
        - Profit targets: Near resistance
    
    Example:
        >>> supports, resistances = find_support_resistance(prices)
        >>> print(f"S1: {supports[0]}, R1: {resistances[0]}")
    """
    if len(prices) < lookback_period:
        lookback_period = len(prices)
    
    recent_prices = prices[-lookback_period:]
    
    # Find local highs (resistance)
    resistances = []
    for i in range(1, len(recent_prices) - 1):
        if recent_prices[i] > recent_prices[i - 1] and recent_prices[i] > recent_prices[i + 1]:
            resistances.append(recent_prices[i])
    
    # Find local lows (support)
    supports = []
    for i in range(1, len(recent_prices) - 1):
        if recent_prices[i] < recent_prices[i - 1] and recent_prices[i] < recent_prices[i + 1]:
            supports.append(recent_prices[i])
    
    # Get unique levels and sort
    resistances = sorted(list(set(resistances)), reverse=True)[:num_levels]
    supports = sorted(list(set(supports)))[:num_levels]
    
    return supports, resistances


def generate_technical_signal(
    rsi: float,
    macd_vs_signal: float,  # MACD - Signal (positive = bullish)
    price_vs_upperbb: float,  # Current - Upper BB (negative = below, not overbought)
    price_vs_lowerbb: float,  # Current - Lower BB (positive = above, not oversold)
    price_vs_ema200: float,  # Current - EMA200 (positive = above, uptrend)
    atr_as_pct: float = 2.5,  # ATR as % of price
) -> Dict[str, object]:
    """
    Generate technical trading signal (STRONG BUY to STRONG SELL).
    
    Combines all indicators into a unified technical verdict.
    
    Args:
        rsi: RSI value (0-100)
        macd_vs_signal: Difference between MACD and Signal (positive=bullish)
        price_vs_upperbb: Difference between price and upper Bollinger Band
        price_vs_lowerbb: Difference between price and lower Bollinger Band
        price_vs_ema200: Difference between price and EMA200
        atr_as_pct: ATR as percentage of current price
    
    Returns:
        Dict with:
        - signal: STRONG BUY / BUY / HOLD / SELL / STRONG SELL
        - confidence: 0-100 confidence level
        - reasons: List of bullish/bearish reasons
        - technical_score: 0-10 score
    
    Example:
        >>> signal_dict = generate_technical_signal(
        ...     rsi=65, macd_vs_signal=0.5, price_vs_upperbb=-20,
        ...     price_vs_lowerbb=50, price_vs_ema200=100
        ... )
        >>> print(signal_dict['signal'])  # e.g., "BUY"
    """
    bullish_points = 0
    bearish_points = 0
    reasons = []
    
    # RSI Analysis
    if rsi > 70:
        bearish_points += 1
        reasons.append("RSI Overbought (>70)")
    elif rsi > 50:
        bullish_points += 1
        reasons.append("RSI Bullish (50-70)")
    elif rsi < 30:
        bullish_points += 1
        reasons.append("RSI Oversold (<30)")
    elif rsi < 50:
        bearish_points += 1
        reasons.append("RSI Bearish (<50)")
    
    # MACD Analysis
    if macd_vs_signal > 0:
        bullish_points += 1.5
        reasons.append("MACD above Signal (bullish)")
    else:
        bearish_points += 1.5
        reasons.append("MACD below Signal (bearish)")
    
    # Bollinger Bands Analysis
    if price_vs_lowerbb < 0:
        bullish_points += 1
        reasons.append("Price at Lower BB (oversold)")
    elif price_vs_upperbb > 0:
        bearish_points += 1
        reasons.append("Price at Upper BB (overbought)")
    
    # EMA200 Analysis (Trend Confirmation)
    if price_vs_ema200 > 0:
        bullish_points += 1
        reasons.append("Price > EMA200 (long-term uptrend)")
    else:
        bearish_points += 1
        reasons.append("Price < EMA200 (long-term downtrend)")
    
    # ATR Analysis (Volatility Impact)
    if atr_as_pct > 4:
        # High volatility - reduce conviction
        bullish_points *= 0.8
        bearish_points *= 0.8
        reasons.append("High Volatility (reduce position size)")
    elif atr_as_pct < 1:
        reasons.append("Low Volatility (consolidation)")
    
    # Calculate signal
    net_points = bullish_points - bearish_points
    
    if net_points > 3:
        signal = "STRONG BUY"
        technical_score = 9
        confidence = 85
    elif net_points > 1.5:
        signal = "BUY"
        technical_score = 7
        confidence = 70
    elif net_points > -1.5:
        signal = "HOLD"
        technical_score = 5
        confidence = 60
    elif net_points > -3:
        signal = "SELL"
        technical_score = 3
        confidence = 70
    else:
        signal = "STRONG SELL"
        technical_score = 1
        confidence = 85
    
    return {
        "signal": signal,
        "technical_score": technical_score,
        "confidence": confidence,
        "bullish_points": round(bullish_points, 1),
        "bearish_points": round(bearish_points, 1),
        "reasons": reasons,
    }
