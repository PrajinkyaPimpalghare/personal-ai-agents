"""
Intraday Trading Setups - Professional intraday strategies

Four main setups:
1. Opening Range Breakout (ORB) - Breakout in first 15 minutes
2. Pivot Breakout - Trade around pivot points
3. Momentum Reversal - RSI/Stochastic overbought/oversold
4. Support/Resistance - Bounce trades at key levels
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class TradingSetup:
    """Single intraday trading setup"""
    setup_type: str                  # ORB, Pivot, Momentum, S-R
    stock: str
    entry_price: float
    stop_loss: float
    target_price: float
    entry_condition: str             # Description of entry condition
    confidence: int                  # 1-10 confidence level
    risk_reward_ratio: float         # R:R
    setup_time: str                  # When setup appeared
    liquidity: str                   # EXCELLENT / GOOD / FAIR
    notes: str                       # Additional notes
    

class OpeningRangeBreakout:
    """ORB Setup - Trade breakout of first 15-min range"""
    
    @staticmethod
    def identify_setup(levels: 'IntradayLevel', candles_15min: List[Dict], 
                      indicators: Dict) -> Optional[TradingSetup]:
        """
        Identify ORB setup
        
        Entry: Break above/below opening range with volume
        Stop: Inside opening range
        Target: Risk-reward 1:1.5 minimum
        """
        if not levels or not candles_15min:
            return None
        
        current_price = levels.current_price
        orb_high = levels.open_range_high
        orb_low = levels.open_range_low
        
        if orb_high == 0 or orb_low == 0:
            return None
        
        # Check for breakout above
        if current_price > orb_high:
            entry_price = orb_high + 0.05  # Entry just above ORB high
            stop_loss = orb_low
            risk = entry_price - stop_loss
            target = entry_price + (risk * 1.5)
            
            confidence = 8 if indicators.get("volume_is_bullish") else 6
            
            return TradingSetup(
                setup_type="ORB",
                stock=levels.stock,
                entry_price=round(entry_price, 2),
                stop_loss=round(stop_loss, 2),
                target_price=round(target, 2),
                entry_condition=f"Break above ORB high {orb_high:.2f}",
                confidence=confidence,
                risk_reward_ratio=1.5,
                setup_time=levels.current_time or "",
                liquidity="EXCELLENT",
                notes="Opening range breakout with volume confirmation"
            )
        
        # Check for breakdown below
        elif current_price < orb_low:
            entry_price = orb_low - 0.05  # Entry just below ORB low
            stop_loss = orb_high
            risk = stop_loss - entry_price
            target = entry_price - (risk * 1.5)
            
            confidence = 8 if indicators.get("volume_is_bullish") else 6
            
            return TradingSetup(
                setup_type="ORB",
                stock=levels.stock,
                entry_price=round(entry_price, 2),
                stop_loss=round(stop_loss, 2),
                target_price=round(target, 2),
                entry_condition=f"Break below ORB low {orb_low:.2f}",
                confidence=confidence,
                risk_reward_ratio=1.5,
                setup_time=levels.current_time or "",
                liquidity="EXCELLENT",
                notes="Opening range breakdown with volume confirmation"
            )
        
        return None


class PivotBreakout:
    """Pivot Point Trading Setup"""
    
    @staticmethod
    def identify_setup(levels: 'IntradayLevel', indicators: Dict) -> Optional[TradingSetup]:
        """
        Identify pivot breakout setup
        
        Entry: Breakout of R1/S1
        Stop: Pivot level or previous
        Target: R2 or S2
        """
        if not levels:
            return None
        
        current_price = levels.current_price
        
        # Check R1 breakout
        if current_price > levels.r1 and not (current_price > levels.r2):
            entry_price = levels.r1 + 0.05
            stop_loss = levels.pivot
            target = levels.r2
            
            confidence = 7 if indicators.get("rsi_signal") == "BULLISH_MOMENTUM" else 5
            
            return TradingSetup(
                setup_type="Pivot",
                stock=levels.stock,
                entry_price=round(entry_price, 2),
                stop_loss=round(stop_loss, 2),
                target_price=round(target, 2),
                entry_condition=f"Break above R1 {levels.r1:.2f}",
                confidence=confidence,
                risk_reward_ratio=2.0,
                setup_time=levels.current_time or "",
                liquidity="GOOD",
                notes="Pivot R1 breakout trade"
            )
        
        # Check S1 breakdown
        if current_price < levels.s1 and not (current_price < levels.s2):
            entry_price = levels.s1 - 0.05
            stop_loss = levels.pivot
            target = levels.s2
            
            confidence = 7 if indicators.get("rsi_signal") == "BEARISH_MOMENTUM" else 5
            
            return TradingSetup(
                setup_type="Pivot",
                stock=levels.stock,
                entry_price=round(entry_price, 2),
                stop_loss=round(stop_loss, 2),
                target_price=round(target, 2),
                entry_condition=f"Break below S1 {levels.s1:.2f}",
                confidence=confidence,
                risk_reward_ratio=2.0,
                setup_time=levels.current_time or "",
                liquidity="GOOD",
                notes="Pivot S1 breakdown trade"
            )
        
        # Check bounce from pivot
        if abs(current_price - levels.pivot) < (levels.r1 - levels.pivot) * 0.3:
            if indicators.get("rsi_signal") == "OVERSOLD":
                entry_price = levels.pivot
                stop_loss = levels.s1
                target = levels.r1
                
                return TradingSetup(
                    setup_type="Pivot",
                    stock=levels.stock,
                    entry_price=round(entry_price, 2),
                    stop_loss=round(stop_loss, 2),
                    target_price=round(target, 2),
                    entry_condition=f"Bounce from Pivot {levels.pivot:.2f} with RSI oversold",
                    confidence=8,
                    risk_reward_ratio=1.5,
                    setup_time=levels.current_time or "",
                    liquidity="GOOD",
                    notes="Pivot bounce trade when oversold"
                )
        
        return None


class MomentumReversal:
    """Momentum-based reversal setup"""
    
    @staticmethod
    def identify_setup(levels: 'IntradayLevel', indicators: Dict, pivot_level: float) -> Optional[TradingSetup]:
        """
        Identify momentum reversal setup
        
        Entry: RSI / Stochastic extremely overbought/oversold
        Stop: Opposite extreme
        Target: Back to pivot or midpoint
        """
        if not indicators:
            return None
        
        current_price = levels.current_price if levels else 0
        rsi = indicators.get("rsi", 50)
        stoch_k = indicators.get("stoch_k", 50)
        
        # Oversold reversal (Buy signal)
        if rsi < 25 and stoch_k < 20:
            entry_price = current_price
            stop_loss = current_price - 50  # Rough stop
            target = pivot_level  # Back to pivot
            
            if stop_loss < target:
                risk = entry_price - stop_loss
                rr = (target - entry_price) / risk if risk > 0 else 1.0
                
                return TradingSetup(
                    setup_type="Momentum",
                    stock=levels.stock if levels else "UNKNOWN",
                    entry_price=round(entry_price, 2),
                    stop_loss=round(stop_loss, 2),
                    target_price=round(target, 2),
                    entry_condition=f"Extreme oversold: RSI {rsi:.0f}, Stochastic {stoch_k:.0f}",
                    confidence=8,
                    risk_reward_ratio=rr,
                    setup_time=levels.current_time if levels else "",
                    liquidity="GOOD",
                    notes="Momentum reversal from oversold condition"
                )
        
        # Overbought reversal (Sell signal)
        if rsi > 75 and stoch_k > 80:
            entry_price = current_price
            stop_loss = current_price + 50  # Rough stop
            target = pivot_level  # Back to pivot
            
            if entry_price > target:
                risk = stop_loss - entry_price
                rr = (entry_price - target) / risk if risk > 0 else 1.0
                
                return TradingSetup(
                    setup_type="Momentum",
                    stock=levels.stock if levels else "UNKNOWN",
                    entry_price=round(entry_price, 2),
                    stop_loss=round(stop_loss, 2),
                    target_price=round(target, 2),
                    entry_condition=f"Extreme overbought: RSI {rsi:.0f}, Stochastic {stoch_k:.0f}",
                    confidence=8,
                    risk_reward_ratio=rr,
                    setup_time=levels.current_time if levels else "",
                    liquidity="GOOD",
                    notes="Momentum reversal from overbought condition"
                )
        
        return None


class SupportResistanceBreak:
    """Support/Resistance bounce trade"""
    
    @staticmethod
    def identify_setup(levels: 'IntradayLevel', support_levels: List[float], 
                      resistance_levels: List[float], indicators: Dict) -> Optional[TradingSetup]:
        """
        Identify S/R bounce setup
        
        Entry: Bounce from support or breakdown from resistance
        Stop: Break of support/resistance
        Target: Next level
        """
        if not levels or not support_levels or not resistance_levels:
            return None
        
        current_price = levels.current_price
        tolerance = 0.3  # 0.3% tolerance for "at" support/resistance
        
        # Bounce from support
        if support_levels:
            nearest_support = min(support_levels)
            if abs(current_price - nearest_support) < (current_price * tolerance / 100):
                stop_loss = nearest_support - 20
                if resistance_levels:
                    target = max([r for r in resistance_levels if r > current_price], default=current_price + 50)
                else:
                    target = current_price + 50
                
                risk = current_price - stop_loss
                rr = (target - current_price) / risk if risk > 0 else 1.0
                
                confidence = 6 if indicators.get("volume_is_bullish") else 5
                
                return TradingSetup(
                    setup_type="S-R",
                    stock=levels.stock,
                    entry_price=round(current_price, 2),
                    stop_loss=round(stop_loss, 2),
                    target_price=round(target, 2),
                    entry_condition=f"Bounce from Support {nearest_support:.2f}",
                    confidence=confidence,
                    risk_reward_ratio=rr,
                    setup_time=levels.current_time or "",
                    liquidity="FAIR",
                    notes="Support bounce trade"
                )
        
        # Breakdown from resistance
        if resistance_levels:
            nearest_resistance = max(resistance_levels)
            if abs(current_price - nearest_resistance) < (current_price * tolerance / 100):
                stop_loss = nearest_resistance + 20
                if support_levels:
                    target = min([s for s in support_levels if s < current_price], default=current_price - 50)
                else:
                    target = current_price - 50
                
                if current_price > target:
                    risk = stop_loss - current_price
                    rr = (current_price - target) / risk if risk > 0 else 1.0
                    
                    confidence = 6 if indicators.get("volume_is_bullish") else 5
                    
                    return TradingSetup(
                        setup_type="S-R",
                        stock=levels.stock,
                        entry_price=round(current_price, 2),
                        stop_loss=round(stop_loss, 2),
                        target_price=round(target, 2),
                        entry_condition=f"Breakdown from Resistance {nearest_resistance:.2f}",
                        confidence=confidence,
                        risk_reward_ratio=rr,
                        setup_time=levels.current_time or "",
                        liquidity="FAIR",
                        notes="Resistance breakdown trade"
                    )
        
        return None


class IntradaySetupFinder:
    """Find all available intraday trading setups"""
    
    def __init__(self):
        self.orb = OpeningRangeBreakout()
        self.pivot = PivotBreakout()
        self.momentum = MomentumReversal()
        self.sr = SupportResistanceBreak()
    
    def find_all_setups(self, levels: 'IntradayLevel', candles_15min: List[Dict], 
                       support_levels: List[float], resistance_levels: List[float],
                       indicators: Dict) -> List[TradingSetup]:
        """Find all available trading setups"""
        setups = []
        
        # Try ORB
        orb_setup = OpeningRangeBreakout.identify_setup(levels, candles_15min, indicators)
        if orb_setup:
            setups.append(orb_setup)
        
        # Try Pivot
        pivot_setup = PivotBreakout.identify_setup(levels, indicators)
        if pivot_setup:
            setups.append(pivot_setup)
        
        # Try Momentum Reversal
        momentum_setup = MomentumReversal.identify_setup(levels, indicators, levels.pivot if levels else 0)
        if momentum_setup:
            setups.append(momentum_setup)
        
        # Try S/R
        sr_setup = SupportResistanceBreak.identify_setup(levels, support_levels, resistance_levels, indicators)
        if sr_setup:
            setups.append(sr_setup)
        
        # Sort by confidence
        setups.sort(key=lambda x: x.confidence, reverse=True)
        
        return setups
    
    def to_dict(self, setup: TradingSetup) -> Dict:
        """Convert setup to dictionary"""
        return {
            "setup_type": setup.setup_type,
            "stock": setup.stock,
            "entry_price": setup.entry_price,
            "stop_loss": setup.stop_loss,
            "target_price": setup.target_price,
            "entry_condition": setup.entry_condition,
            "confidence": setup.confidence,
            "risk_reward_ratio": round(setup.risk_reward_ratio, 2),
            "setup_time": setup.setup_time,
            "liquidity": setup.liquidity,
            "notes": setup.notes,
            "potential_profit": round((setup.target_price - setup.entry_price) * 100, 2)  # For 100 shares
        }
