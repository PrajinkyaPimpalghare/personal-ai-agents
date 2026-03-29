"""
Risk Management Module - Position sizing, stop loss, and portfolio risk control

Implements professional risk management framework:
- ATR-based position sizing (tied to volatility)
- Dynamic stop loss calculation
- Profit target generation (1:2, 1:3, 1:4 ratios)
- Risk-reward ratio enforcement
- Portfolio heat tracking (concentration risk)
- Drawdown monitoring and limits
- Position validation and warnings

All calculations are deterministic and based on proven risk management principles.
"""

from typing import List, Dict, Tuple, Optional


def calculate_position_size(
    account_size: float,
    risk_per_trade_pct: float = 2.0,
    entry_price: float = None,
    stop_loss_price: float = None,
    stop_loss_distance: float = None,
    atr: float = None,
    volatility_multiplier: float = 1.0,
    max_position_pct: float = 15.0  # Max % of account per position
) -> Dict[str, float]:
    """
    Calculate position size based on ATR volatility and account risk.
    
    Formula: Position Size = (Account Risk %) / Stop Loss Distance
    where Stop Loss Distance = Entry - (ATR × Multiplier)
    
    Args:
        account_size: Total account value (₹)
        risk_per_trade_pct: Max risk per trade as % of account (default 2%)
        entry_price: Entry price (₹)
        stop_loss_price: Stop loss price (₹)
        stop_loss_distance: If provided, use directly instead of calculating
        atr: Average True Range
        volatility_multiplier: Multiplier for stop distance (1.0 to 2.0)
        max_position_pct: Max position as % of account (caps position size)
    
    Returns:
        Dict with:
        - quantity: Number of shares
        - position_value: Total position value (₹)
        - position_pct: Position as % of account
        - max_loss: Maximum loss if stopped (₹)
        - risk_per_share: Risk per share (₹)
    
    Example:
        >>> sizing = calculate_position_size(
        ...     account_size=1000000,
        ...     entry_price=3850,
        ...     atr=95,
        ...     volatility_multiplier=1.5
        ... )
        >>> print(f"Buy {sizing['quantity']} shares")  # e.g., "Buy 260 shares"
    """
    max_loss = (account_size * risk_per_trade_pct) / 100
    
    # Calculate stop loss distance
    if stop_loss_distance is None:
        if entry_price is None or atr is None:
            return {
                "quantity": 0,
                "position_value": 0,
                "position_pct": 0,
                "max_loss": max_loss,
                "error": "Insufficient data for calculation"
            }
        
        if stop_loss_price is not None:
            stop_loss_distance = entry_price - stop_loss_price
        else:
            stop_loss_distance = atr * volatility_multiplier
    
    if stop_loss_distance <= 0:
        return {
            "quantity": 0,
            "position_value": 0,
            "position_pct": 0,
            "max_loss": max_loss,
            "error": "Invalid stop loss distance"
        }
    
    # Calculate quantity based on max loss
    quantity = int(max_loss / stop_loss_distance)
    
    position_value = quantity * entry_price
    position_pct = (position_value / account_size) * 100
    
    # Apply max position cap
    if position_pct > max_position_pct:
        quantity = int((account_size * max_position_pct) / (entry_price * 100))
        position_value = quantity * entry_price
        position_pct = (position_value / account_size) * 100
    
    return {
        "quantity": quantity,
        "position_value": round(position_value, 2),
        "position_pct": round(position_pct, 2),
        "max_loss": round(max_loss, 2),
        "risk_per_share": round(stop_loss_distance, 2),
        "stop_loss_price": round(entry_price - stop_loss_distance, 2)
    }


def calculate_atr_based_stop_loss(
    entry_price: float,
    atr: float,
    multiplier: float = 1.5
) -> float:
    """
    Calculate ATR-based stop loss price.
    
    Formula: Stop Loss = Entry Price - (ATR × Multiplier)
    
    Args:
        entry_price: Entry price (₹)
        atr: Average True Range
        multiplier: ATR multiplier
            - 1.0 = Tight stop (aggressive, higher exit probability)
            - 1.5 = Standard stop (balanced)
            - 2.0 = Conservative stop (looser, lower exit probability)
    
    Returns:
        Stop loss price (₹)
    
    Example:
        >>> stop = calculate_atr_based_stop_loss(
        ...     entry_price=3850,
        ...     atr=95,
        ...     multiplier=1.5
        ... )
        >>> print(f"Stop Loss: ₹{stop}")  # "Stop Loss: ₹3707.5"
    """
    stop_loss = entry_price - (atr * multiplier)
    return round(max(0, stop_loss), 2)


def calculate_profit_targets(
    entry_price: float,
    stop_loss_price: float,
    target_ratios: List[float] = None,
    include_breakeven: bool = True
) -> Dict[str, float]:
    """
    Calculate profit targets based on risk-reward ratios.
    
    Formula: Target = Entry + ((Entry - Stop) × Ratio)
    
    Args:
        entry_price: Entry price (₹)
        stop_loss_price: Stop loss price (₹)
        target_ratios: Risk-reward ratios (default: [2, 3, 4] for 1:2, 1:3, 1:4)
        include_breakeven: Include breakeven level
    
    Returns:
        Dict with:
        - t1: First target (1:2 ratio)
        - t2: Second target (1:3 ratio)
        - t3: Third target (1:4 ratio)
        - breakeven: Entry price
        - recommended_exit_strategy: Exit plan with % positions
    
    Example:
        >>> targets = calculate_profit_targets(
        ...     entry_price=3850,
        ...     stop_loss_price=3600
        ... )
        >>> print(f"Targets: {targets['t1']}, {targets['t2']}, {targets['t3']}")
    """
    if target_ratios is None:
        target_ratios = [2, 3, 4]
    
    risk_distance = entry_price - stop_loss_price
    
    targets = {"breakeven": entry_price}
    
    for i, ratio in enumerate(target_ratios, 1):
        target_price = entry_price + (risk_distance * ratio)
        targets[f"t{i}"] = round(target_price, 2)
    
    # Recommended exit strategy
    targets["exit_strategy"] = {
        "t1": "Sell 30% (lock in profit)",
        "t2": "Sell 50% (lock in bigger profit)",
        "t3": "Let remaining 20% run (max upside)",
    }
    
    return targets


def calculate_risk_reward_ratio(
    entry_price: float,
    target_price: float,
    stop_loss_price: float
) -> float:
    """
    Calculate risk-reward ratio for a trade.
    
    Formula: R/R = Potential Gain / Potential Loss
    
    Args:
        entry_price: Entry price (₹)
        target_price: Profit target (₹)
        stop_loss_price: Stop loss (₹)
    
    Returns:
        Risk-reward ratio (2.0 = 1:2 ratio)
    
    Rules:
        - Minimum 1:2 ratio (0.5 risk:reward)
        - Ideal 1:3 ratio (~0.33)
        - Avoid ratios < 1:1 (lose more than you can gain)
    
    Example:
        >>> ratio = calculate_risk_reward_ratio(3850, 4100, 3600)
        >>> print(f"R/R Ratio: 1:{ratio}")  # "R/R Ratio: 1:2.0"
    """
    risk = entry_price - stop_loss_price
    reward = target_price - entry_price
    
    if risk == 0:
        return 0.0
    
    ratio = reward / risk
    return round(ratio, 2)


def portfolio_heat_calculation(
    positions: List[Dict],
    account_size: float = None
) -> Dict[str, float]:
    """
    Calculate total portfolio risk (heat) and concentration levels.
    
    Args:
        positions: List of position dicts with:
            - symbol: Stock ticker
            - quantity: Shares held
            - entry_price: Entry price
            - current_price: Current price
            - stop_loss: Stop loss price
            - sector: Sector classification
        account_size: Total account value (optional, auto-calc if not provided)
    
    Returns:
        Dict with:
        - total_portfolio_value: Sum of all position values
        - total_portfolio_risk: Amount at risk if all stops hit
        - total_portfolio_risk_pct: As % of portfolio
        - sector_concentration: Dict with each sector's risk %
        - position_concentration: Dict with each position's risk %
        - warnings: List of concentration warnings
    
    Example:
        >>> positions = [
        ...     {"symbol": "TCS", "quantity": 50, "entry_price": 3850,
        ...      "current_price": 3900, "stop_loss": 3600, "sector": "IT"},
        ...     {"symbol": "INFOSYS", "quantity": 30, "entry_price": 1500,
        ...      "current_price": 1820, "stop_loss": 1400, "sector": "IT"}
        ... ]
        >>> heat = portfolio_heat_calculation(positions, account_size=1000000)
        >>> print(f"Total Risk: {heat['total_portfolio_risk_pct']}%")
    """
    if not positions:
        return {"error": "No positions provided"}
    
    total_portfolio_value = 0
    total_risk_rupees = 0
    sector_risk = {}
    position_risks = {}
    
    # Calculate totals
    for pos in positions:
        position_value = pos["quantity"] * pos["current_price"]
        risk_per_position = pos["quantity"] * (pos["current_price"] - pos["stop_loss"])
        
        total_portfolio_value += position_value
        total_risk_rupees += risk_per_position
        
        position_risks[pos["symbol"]] = risk_per_position
        
        sector = pos.get("sector", "Other")
        if sector not in sector_risk:
            sector_risk[sector] = 0
        sector_risk[sector] += risk_per_position
    
    if account_size is None:
        account_size = total_portfolio_value
    
    total_risk_pct = (total_risk_rupees / account_size) * 100
    
    # Calculate concentration percentages
    position_concentration = {}
    sector_concentration = {}
    
    for symbol, risk in position_risks.items():
        position_concentration[symbol] = round((risk / total_portfolio_value) * 100, 2) \
            if total_portfolio_value > 0 else 0
    
    for sector, risk in sector_risk.items():
        sector_concentration[sector] = round((risk / total_portfolio_value) * 100, 2) \
            if total_portfolio_value > 0 else 0
    
    # Generate warnings
    warnings = []
    if total_risk_pct > 6:
        warnings.append(f"⚠️ Portfolio risk {total_risk_pct:.1f}% > 6% threshold. REDUCE positions.")
    if total_risk_pct > 10:
        warnings.append(f"🔴 CRITICAL: Portfolio risk {total_risk_pct:.1f}%. EXIT 50% of portfolio immediately.")
    
    for sector, pct in sector_concentration.items():
        if pct > 20:
            warnings.append(f"⚠️ Sector concentration: {sector} {pct:.1f}% > 20% limit")
    
    for symbol, pct in position_concentration.items():
        if pct > 15:
            warnings.append(f"⚠️ Position concentration: {symbol} {pct:.1f}% > 15% limit")
    
    return {
        "total_portfolio_value": round(total_portfolio_value, 2),
        "total_portfolio_risk": round(total_risk_rupees, 2),
        "total_portfolio_risk_pct": round(total_risk_pct, 2),
        "position_concentration": position_concentration,
        "sector_concentration": sector_concentration,
        "warnings": warnings,
        "status": "HEALTHY" if total_risk_pct < 5 else "CAUTION" if total_risk_pct < 8 else "ALERT"
    }


def calculate_drawdown_from_peak(
    portfolio_peak_value: float,
    current_portfolio_value: float
) -> Dict[str, object]:
    """
    Calculate portfolio drawdown from recent peak.
    
    Formula: Drawdown % = (Current - Peak) / Peak × 100
    
    Args:
        portfolio_peak_value: Recent peak portfolio value (₹)
        current_portfolio_value: Current portfolio value (₹)
    
    Returns:
        Dict with:
        - drawdown_pct: Drawdown as percentage
        - amount_lost: Amount lost in rupees
        - action: Trading action based on drawdown level
    
    Trading Rules:
        -5%: Pause new positions
        -10%: Exit 50% of positions
        -15%: Stop all trading, review strategy
    
    Example:
        >>> dd = calculate_drawdown_from_peak(1000000, 950000)
        >>> print(f"Drawdown: {dd['drawdown_pct']}%")  # "-5.0%"
    """
    if portfolio_peak_value == 0:
        return {"error": "Invalid peak value"}
    
    drawdown_pct = ((current_portfolio_value - portfolio_peak_value) / portfolio_peak_value) * 100
    amount_lost = portfolio_peak_value - current_portfolio_value
    
    if drawdown_pct > -5:
        action = "✅ NORMAL - Continue trading normally"
    elif drawdown_pct > -10:
        action = "⚠️ CAUTION - Pause new positions, only hold existing"
    elif drawdown_pct > -15:
        action = "🔴 ALERT - Exit 50% of portfolio, lock in some capital"
    else:
        action = "⛔ CRITICAL - STOP ALL TRADING. Review strategy. Portfolio damage control mode."
    
    return {
        "drawdown_pct": round(drawdown_pct, 2),
        "amount_lost": round(amount_lost, 2),
        "peak_value": portfolio_peak_value,
        "current_value": current_portfolio_value,
        "action": action,
        "trading_status": "🟢 ACTIVE" if drawdown_pct > -5 else "🟡 CAUTION" if drawdown_pct > -10 else "🔴 STOP"
    }


def validate_position_sizing(
    positions: List[Dict],
    account_size: float,
    max_sector_concentration: float = 0.20,
    max_single_stock: float = 0.15,
    max_portfolio_risk_pct: float = 6.0
) -> Dict[str, List[str]]:
    """
    Validate portfolio against risk management constraints.
    
    Args:
        positions: List of position dicts
        account_size: Total account value
        max_sector_concentration: Max sector risk (default 20%)
        max_single_stock: Max single stock risk (default 15%)
        max_portfolio_risk_pct: Max total portfolio risk (default 6%)
    
    Returns:
        Dict with:
        - violations: List of constraint violations
        - recommendations: List of corrective actions
        - validation_status: PASS / WARNING / FAIL
    
    Example:
        >>> validation = validate_position_sizing(
        ...     positions=positions,
        ...     account_size=1000000
        ... )
        >>> print(validation['validation_status'])
    """
    violations = []
    recommendations = []
    
    # Calculate metrics
    heat = portfolio_heat_calculation(positions, account_size)
    
    if "error" in heat:
        return {"error": heat["error"]}
    
    # Check portfolio risk
    if heat["total_portfolio_risk_pct"] > max_portfolio_risk_pct:
        violations.append(f"Portfolio risk {heat['total_portfolio_risk_pct']}% > {max_portfolio_risk_pct}% limit")
        recommendations.append("Reduce position sizes or exit smaller positions")
    
    # Check sector concentration
    for sector, risk_pct in heat["sector_concentration"].items():
        if risk_pct > max_sector_concentration * 100:
            violations.append(f"Sector {sector} risk {risk_pct}% > {max_sector_concentration * 100}% limit")
            recommendations.append(f"Reduce {sector} positions")
    
    # Check individual positions
    for symbol, risk_pct in heat["position_concentration"].items():
        if risk_pct > max_single_stock * 100:
            violations.append(f"{symbol} risk {risk_pct}% > {max_single_stock * 100}% limit")
            recommendations.append(f"Reduce {symbol} position size")
    
    if violations:
        status = "FAIL"
    elif heat["total_portfolio_risk_pct"] > max_portfolio_risk_pct * 0.8:
        status = "WARNING"
        recommendations.append("Approaching risk limits - monitor closely")
    else:
        status = "PASS"
    
    return {
        "validation_status": status,
        "violations": violations,
        "recommendations": recommendations,
        "portfolio_metrics": {
            "total_risk_pct": heat["total_portfolio_risk_pct"],
            "position_concentration": heat["position_concentration"],
            "sector_concentration": heat["sector_concentration"],
        }
    }
