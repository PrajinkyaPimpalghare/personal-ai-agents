"""
Intraday Technical Indicators

Fast indicators optimized for intraday (5-min to 30-min candles):
- RSI (Relative Strength Index) - 14 period
- Stochastic %K %D - (14,3,3) Fast
- ADX (Average Directional Index) - Trend strength
- Rate of Change (ROC) - Momentum
- MACD Fast - (5, 13, 5)
- Volume Rate of Change - Volume momentum
"""

from typing import List, Dict, Tuple
import statistics


class IntradayRSI:
    """RSI indicator for intraday trading"""
    
    @staticmethod
    def calculate(closes: List[float], period: int = 14) -> Tuple[List[float], float]:
        """
        Calculate RSI values
        
        Args:
            closes: List of close prices (oldest to newest)
            period: RSI period (default 14)
        
        Returns:
            (rsi_values, current_rsi)
        """
        if len(closes) < period:
            return [], 0
        
        rsi_values = []
        gains = 0
        losses = 0
        
        # Calculate initial gains and losses
        for i in range(1, period + 1):
            change = closes[i] - closes[i-1]
            if change > 0:
                gains += change
            else:
                losses += abs(change)
        
        avg_gain = gains / period
        avg_loss = losses / period
        
        # Calculate first RSI
        rs = avg_gain / avg_loss if avg_loss != 0 else 0
        rsi = 100 - (100 / (1 + rs)) if rs >= 0 else 0
        rsi_values.append(rsi)
        
        # Smooth RSI for remaining values
        for i in range(period + 1, len(closes)):
            change = closes[i] - closes[i-1]
            if change > 0:
                avg_gain = (avg_gain * (period - 1) + change) / period
                avg_loss = (avg_loss * (period - 1)) / period
            else:
                avg_gain = (avg_gain * (period - 1)) / period
                avg_loss = (avg_loss * (period - 1) + abs(change)) / period
            
            rs = avg_gain / avg_loss if avg_loss != 0 else 0
            rsi = 100 - (100 / (1 + rs)) if rs >= 0 else 0
            rsi_values.append(rsi)
        
        return rsi_values, rsi_values[-1] if rsi_values else 0
    
    @staticmethod
    def get_signal(rsi: float) -> str:
        """Get trading signal from RSI"""
        if rsi > 70:
            return "OVERBOUGHT"
        elif rsi < 30:
            return "OVERSOLD"
        elif rsi > 50:
            return "BULLISH_MOMENTUM"
        elif rsi < 50:
            return "BEARISH_MOMENTUM"
        else:
            return "NEUTRAL"


class IntradayStochastic:
    """Fast Stochastic Oscillator"""
    
    @staticmethod
    def calculate(highs: List[float], lows: List[float], closes: List[float], 
                 k_period: int = 14, d_period: int = 3, smooth: int = 3) -> Tuple[float, float]:
        """
        Calculate Stochastic %K and %D
        
        Returns:
            (%K, %D)
        """
        if len(closes) < k_period:
            return 0, 0
        
        # Calculate %K
        high_14 = max(highs[-k_period:])
        low_14 = min(lows[-k_period:])
        
        if high_14 == low_14:
            k = 50
        else:
            k = 100 * (closes[-1] - low_14) / (high_14 - low_14)
        
        # Calculate %D (3-period SMA of %K)
        # For simplicity, use current K as approximation
        d = k  # Would be calculated as SMA in full implementation
        
        return k, d
    
    @staticmethod
    def get_signal(k: float, d: float) -> str:
        """Get trading signal from Stochastic"""
        if k < 20 and d < 20:
            return "STRONG_OVERSOLD"
        elif k < 50 and k > d:
            return "BULLISH_CROSSOVER"
        elif k > 80 and d > 80:
            return "STRONG_OVERBOUGHT"
        elif k > 50 and k < d:
            return "BEARISH_CROSSOVER"
        else:
            return "NEUTRAL"


class IntradayADX:
    """Average Directional Index - Trend strength"""
    
    @staticmethod
    def calculate_di(highs: List[float], lows: List[float], closes: List[float], 
                    period: int = 14) -> Tuple[float, float, float]:
        """
        Calculate +DI, -DI, and ADX
        
        Returns:
            (+DI, -DI, ADX)
        """
        if len(closes) < period:
            return 0, 0, 0
        
        # Calculate Plus and Minus DI
        plus_di = 0
        minus_di = 0
        
        for i in range(1, len(closes)):
            up = highs[i] - highs[i-1]
            down = lows[i-1] - lows[i]
            
            if up > 0 and up > down:
                plus_di += up
            else:
                plus_di += 0
            
            if down > 0 and down > up:
                minus_di += down
            else:
                minus_di += 0
        
        # Calculate True Range
        tr_sum = 0
        for i in range(1, len(closes)):
            tr = max(
                highs[i] - lows[i],
                abs(highs[i] - closes[i-1]),
                abs(lows[i] - closes[i-1])
            )
            tr_sum += tr
        
        avg_tr = tr_sum / period if period > 0 else 1
        plus_di = (plus_di / period / avg_tr * 100) if avg_tr > 0 else 0
        minus_di = (minus_di / period / avg_tr * 100) if avg_tr > 0 else 0
        
        # ADX = average of DI difference
        di_diff = abs(plus_di - minus_di)
        adx = (plus_di + minus_di) / 2 if (plus_di + minus_di) > 0 else 0
        
        return plus_di, minus_di, adx
    
    @staticmethod
    def get_strength(adx: float) -> str:
        """Interpret ADX strength"""
        if adx > 40:
            return "VERY_STRONG_TREND"
        elif adx > 30:
            return "STRONG_TREND"
        elif adx > 20:
            return "MODERATE_TREND"
        else:
            return "WEAK_TREND"


class IntradayROC:
    """Rate of Change - Momentum indicator"""
    
    @staticmethod
    def calculate(closes: List[float], period: int = 12) -> float:
        """
        Calculate Rate of Change
        ROC = ((Close - Close N periods ago) / Close N periods ago) * 100
        """
        if len(closes) < period + 1:
            return 0
        
        current_close = closes[-1]
        prev_close = closes[-period-1]
        
        if prev_close == 0:
            return 0
        
        roc = ((current_close - prev_close) / prev_close) * 100
        return roc
    
    @staticmethod
    def get_signal(roc: float) -> str:
        """Get signal from ROC"""
        if roc > 5:
            return "STRONG_BULLISH"
        elif roc > 2:
            return "BULLISH"
        elif roc < -5:
            return "STRONG_BEARISH"
        elif roc < -2:
            return "BEARISH"
        else:
            return "NEUTRAL"


class IntradayVolumeIndicator:
    """Volume-based indicators"""
    
    @staticmethod
    def calculate_sma_volume(volumes: List[int], period: int = 20) -> float:
        """Calculate average volume"""
        if len(volumes) < period:
            return statistics.mean(volumes) if volumes else 0
        return statistics.mean(volumes[-period:])
    
    @staticmethod
    def volume_roc(volumes: List[int], period: int = 14) -> float:
        """Volume Rate of Change"""
        if len(volumes) < period + 1:
            return 0
        
        current_vol = volumes[-1]
        prev_vol = volumes[-period-1]
        
        if prev_vol == 0:
            return 0
        
        return ((current_vol - prev_vol) / prev_vol) * 100
    
    @staticmethod
    def is_volume_bullish(current_volume: int, avg_volume: int, threshold: float = 1.5) -> bool:
        """Check if volume is above average (bullish volume)"""
        return current_volume > (avg_volume * threshold)


class IntradayMACD:
    """MACD Fast - optimized for intraday"""
    
    @staticmethod
    def calculate(closes: List[float], fast: int = 5, slow: int = 13, signal: int = 5) -> Tuple[float, float, float]:
        """
        Calculate Fast MACD (5, 13, 5)
        
        Returns:
            (MACD, Signal, Histogram)
        """
        if len(closes) < slow:
            return 0, 0, 0
        
        # Calculate EMAs
        ema_fast = IntradayMACD._calculate_ema(closes, fast)
        ema_slow = IntradayMACD._calculate_ema(closes, slow)
        
        macd = ema_fast - ema_slow
        
        # Signal line (SMA of MACD)
        signal_val = macd  # Simplified
        histogram = macd - signal_val
        
        return macd, signal_val, histogram
    
    @staticmethod
    def _calculate_ema(closes: List[float], period: int) -> float:
        """Calculate EMA for latest close"""
        if len(closes) < period:
            return statistics.mean(closes) if closes else 0
        
        multiplier = 2 / (period + 1)
        ema = statistics.mean(closes[-period:])  # Start with SMA
        
        for close in closes[-period:]:
            ema = close * multiplier + ema * (1 - multiplier)
        
        return ema
    
    @staticmethod
    def get_signal(macd: float, signal: float, histogram: float) -> str:
        """Get trading signal from MACD"""
        if macd > signal and histogram > 0:
            return "BULLISH_MOMENTUM"
        elif macd < signal and histogram < 0:
            return "BEARISH_MOMENTUM"
        elif macd > signal and histogram < 0:
            return "BULL_DIVERGENCE"
        elif macd < signal and histogram > 0:
            return "BEAR_DIVERGENCE"
        else:
            return "NEUTRAL"


class IntradayIndicatorSuite:
    """Complete indicator package for intraday analysis"""
    
    def __init__(self):
        self.rsi_obj = IntradayRSI()
        self.stoch_obj = IntradayStochastic()
        self.adx_obj = IntradayADX()
        self.roc_obj = IntradayROC()
        self.volume_obj = IntradayVolumeIndicator()
        self.macd_obj = IntradayMACD()
    
    def analyze_candles(self, candles: List[Dict]) -> Dict:
        """
        Comprehensive analysis of candles
        
        Args:
            candles: List of candles with {"open", "high", "low", "close", "volume"}
        
        Returns:
            Dictionary with all indicator values and signals
        """
        if len(candles) < 14:
            return {"error": "Need at least 14 candles"}
        
        closes = [c["close"] for c in candles]
        highs = [c["high"] for c in candles]
        lows = [c["low"] for c in candles]
        volumes = [c["volume"] for c in candles]
        
        # Calculate all indicators
        rsi_vals, rsi = IntradayRSI.calculate(closes)
        stoch_k, stoch_d = IntradayStochastic.calculate(highs, lows, closes)
        plus_di, minus_di, adx = IntradayADX.calculate_di(highs, lows, closes)
        roc = IntradayROC.calculate(closes)
        macd, macd_signal, macd_hist = IntradayMACD.calculate(closes)
        avg_vol = IntradayVolumeIndicator.calculate_sma_volume(volumes)
        vol_roc = IntradayVolumeIndicator.volume_roc(volumes)
        
        return {
            "rsi": round(rsi, 2),
            "rsi_signal": IntradayRSI.get_signal(rsi),
            "stoch_k": round(stoch_k, 2),
            "stoch_d": round(stoch_d, 2),
            "stoch_signal": IntradayStochastic.get_signal(stoch_k, stoch_d),
            "adx": round(adx, 2),
            "adx_strength": IntradayADX.get_strength(adx),
            "plus_di": round(plus_di, 2),
            "minus_di": round(minus_di, 2),
            "roc": round(roc, 2),
            "roc_signal": IntradayROC.get_signal(roc),
            "macd": round(macd, 4),
            "macd_signal": round(macd_signal, 4),
            "macd_histogram": round(macd_hist, 4),
            "macd_signal_text": IntradayMACD.get_signal(macd, macd_signal, macd_hist),
            "volume": volumes[-1],
            "avg_volume": round(avg_vol, 0),
            "volume_roc": round(vol_roc, 2),
            "volume_is_bullish": IntradayVolumeIndicator.is_volume_bullish(volumes[-1], avg_vol),
            "current_price": closes[-1],
            "current_time": candles[-1].get("time", "")
        }
