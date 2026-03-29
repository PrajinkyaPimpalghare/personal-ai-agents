"""
Intraday Data Fetcher - Fetch candles and calculate intraday levels

Features:
- Fetch 1/5/15/30 minute candles from Kite MCP
- Calculate pivot points (Daily, Weekly)
- Support/Resistance levels
- Opening range analysis
- Real-time volume profile
"""

from typing import Dict, List, Tuple, Optional
import json
from datetime import datetime, timedelta
import statistics


class IntradayLevel:
    """Intraday price levels"""
    def __init__(self, stock: str, date: str):
        self.stock = stock
        self.date = date
        
        # Previous day data
        self.prev_close = 0
        self.prev_high = 0
        self.prev_low = 0
        self.prev_open = 0
        
        # Opening range (first 15 min)
        self.ema_open = 0
        self.ema_high = 0
        self.ema_low = 0
        self.open_range_high = 0
        self.open_range_low = 0
        
        # Key levels
        self.pivot = 0
        self.r1 = 0
        self.r2 = 0
        self.r3 = 0
        self.s1 = 0
        self.s2 = 0
        self.s3 = 0
        
        # Current price
        self.current_price = 0
        self.current_time = None
        self.current_volume = 0
        
    def calculate_pivots(self):
        """Calculate standard pivot points"""
        hl2 = (self.prev_high + self.prev_low) / 2
        hc2 = (self.prev_high + self.prev_close) / 2
        lc2 = (self.prev_low + self.prev_close) / 2
        
        self.pivot = (self.prev_high + self.prev_low + self.prev_close) / 3
        self.r1 = (2 * self.pivot) - self.prev_low
        self.r2 = self.pivot + (self.prev_high - self.prev_low)
        self.r3 = self.r2 + (self.prev_high - self.prev_low)
        self.s1 = (2 * self.pivot) - self.prev_high
        self.s2 = self.pivot - (self.prev_high - self.prev_low)
        self.s3 = self.s2 - (self.prev_high - self.prev_low)
    
    def is_above_orb(self) -> bool:
        """Check if price is above opening range"""
        return self.current_price > self.open_range_high
    
    def is_below_orb(self) -> bool:
        """Check if price is below opening range"""
        return self.current_price < self.open_range_low
    
    def is_near_pivot(self, tolerance_pct: float = 0.5) -> bool:
        """Check if price is near pivot (within tolerance %)"""
        tolerance = self.pivot * (tolerance_pct / 100)
        return abs(self.current_price - self.pivot) <= tolerance
    
    def distance_to_level(self, level_type: str) -> float:
        """Distance to specific level (in points)"""
        levels = {
            "r1": self.r1,
            "r2": self.r2,
            "r3": self.r3,
            "s1": self.s1,
            "s2": self.s2,
            "s3": self.s3,
            "pivot": self.pivot
        }
        if level_type in levels:
            return abs(self.current_price - levels[level_type])
        return 0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON storage"""
        return {
            "stock": self.stock,
            "date": self.date,
            "prev_close": self.prev_close,
            "prev_high": self.prev_high,
            "prev_low": self.prev_low,
            "open_range_high": self.open_range_high,
            "open_range_low": self.open_range_low,
            "pivot": round(self.pivot, 2),
            "r1": round(self.r1, 2),
            "r2": round(self.r2, 2),
            "r3": round(self.r3, 2),
            "s1": round(self.s1, 2),
            "s2": round(self.s2, 2),
            "s3": round(self.s3, 2),
            "current_price": self.current_price,
            "current_time": self.current_time
        }


class IntradayCandle:
    """Single intraday candle"""
    def __init__(self, time: str, open_: float, high: float, low: float, close: float, volume: int):
        self.time = time
        self.open = open_
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume
        
    def to_dict(self):
        return {
            "time": self.time,
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "volume": self.volume
        }


class IntradayDataFetcher:
    """Fetch and process intraday candle data"""
    
    def __init__(self):
        self.levels_cache: Dict[str, IntradayLevel] = {}
        self.candles_cache: Dict[str, Dict[str, List[IntradayCandle]]] = {}  # {stock: {timeframe: [candles]}}
    
    def fetch_minute_candles(self, instrument_token: int, from_date: str, to_date: str, 
                            interval: str = "5minute") -> List[IntradayCandle]:
        """
        Fetch minute candles from Kite MCP
        
        interval: "minute", "3minute", "5minute", "10minute", "15minute", "30minute", "60minute"
        
        NOTE: This is a placeholder that would call Kite MCP in production:
        candles = kite.get_historical_data(instrument_token, from_date, to_date, interval)
        
        For now, returns mock data for testing
        """
        # In production, this would call:
        # from kite import get_historical_data
        # return get_historical_data(instrument_token, from_date, to_date, interval, oi=False)
        
        # Mock data for testing
        mock_candles = []
        base_price = 1625.0
        for i in range(10):
            mock_candles.append({
                "time": f"09:{15 + i:02d}:00",
                "open": base_price,
                "high": base_price + (i % 3),
                "low": base_price - (i % 2),
                "close": base_price + (i % 2),
                "volume": 1000000 / (i + 1)
            })
        return mock_candles
    
    def calculate_opening_range(self, candles: List[Dict], minutes: int = 15) -> Tuple[float, float]:
        """
        Calculate opening range high and low from first N minutes
        Typically 15-min candle from 9:15-9:30 AM
        """
        if not candles or len(candles) < minutes:
            return 0, 0
        
        prices = [c["high"] for c in candles[:minutes]] + [c["low"] for c in candles[:minutes]]
        orh = max(prices)
        orl = min(prices)
        return orh, orl
    
    def calculate_intraday_levels(self, stock: str, prev_ohlc: Dict, 
                                  current_candles: Dict[str, List]) -> IntradayLevel:
        """
        Calculate all intraday levels for a stock
        
        Args:
            stock: Stock symbol
            prev_ohlc: Previous day's OHLC {"open", "high", "low", "close"}
            current_candles: Current day candles {"1minute": [...], "5minute": [...], etc}
        
        Returns:
            IntradayLevel object with all calculated levels
        """
        level = IntradayLevel(stock, datetime.now().strftime("%Y-%m-%d"))
        
        # Set previous day data
        level.prev_open = prev_ohlc.get("open", 0)
        level.prev_high = prev_ohlc.get("high", 0)
        level.prev_low = prev_ohlc.get("low", 0)
        level.prev_close = prev_ohlc.get("close", 0)
        
        # Calculate pivots
        if level.prev_high > 0 and level.prev_low > 0:
            level.calculate_pivots()
        
        # Calculate opening range
        five_min = current_candles.get("5minute", [])
        if five_min:
            orh, orl = self.calculate_opening_range(five_min, minutes=3)
            level.open_range_high = orh
            level.open_range_low = orl
        
        # Update current price from latest candle
        one_min = current_candles.get("1minute", [])
        if one_min:
            latest = one_min[-1]
            level.current_price = latest["close"]
            level.current_time = latest["time"]
            level.current_volume = latest.get("volume", 0)
        
        self.levels_cache[stock] = level
        return level
    
    def get_levels_for_stocks(self, stocks: List[str]) -> Dict[str, IntradayLevel]:
        """Get intraday levels for multiple stocks"""
        return {stock: self.levels_cache.get(stock) for stock in stocks if stock in self.levels_cache}
    
    def find_support_resistance(self, candles: List[Dict], window: int = 20) -> Tuple[List[float], List[float]]:
        """
        Find support and resistance levels from recent candles
        
        Args:
            candles: List of recent candles
            window: Number of candles to analyze
        
        Returns:
            (support_levels, resistance_levels)
        """
        if len(candles) < window:
            candles = candles
        else:
            candles = candles[-window:]
        
        lows = [c["low"] for c in candles]
        highs = [c["high"] for c in candles]
        
        # Find local lows (support)
        support = []
        for i in range(1, len(lows) - 1):
            if lows[i] < lows[i-1] and lows[i] < lows[i+1]:
                support.append(lows[i])
        
        # Find local highs (resistance)
        resistance = []
        for i in range(1, len(highs) - 1):
            if highs[i] > highs[i-1] and highs[i] > highs[i+1]:
                resistance.append(highs[i])
        
        return sorted(support), sorted(resistance, reverse=True)
    
    def calculate_volume_profile(self, candles: List[Dict]) -> Dict[float, int]:
        """
        Calculate volume profile (volume at each price level)
        Useful for identifying support/resistance
        """
        volume_at_price = {}
        for candle in candles:
            # Round to nearest rupee for aggregation
            price_level = round(candle["close"])
            volume_at_price[price_level] = volume_at_price.get(price_level, 0) + candle.get("volume", 0)
        return dict(sorted(volume_at_price.items(), key=lambda x: x[1], reverse=True))
    
    def identify_trend(self, candles: List[Dict]) -> str:
        """
        Identify current trend direction
        Returns: "UPTREND", "DOWNTREND", "SIDEWAYS"
        """
        if len(candles) < 3:
            return "UNKNOWN"
        
        closes = [c["close"] for c in candles[-10:]]  # Last 10 candles
        
        # Simple trend: compare recent closes to previous
        asc_count = sum(1 for i in range(1, len(closes)) if closes[i] > closes[i-1])
        desc_count = len(closes) - 1 - asc_count
        
        if asc_count > desc_count:
            return "UPTREND"
        elif desc_count > asc_count:
            return "DOWNTREND"
        else:
            return "SIDEWAYS"
    
    def calculate_hl_range(self, candles: List[Dict]) -> float:
        """Calculate high-low range in points (intraday volatility)"""
        if not candles:
            return 0
        
        highs = [c["high"] for c in candles]
        lows = [c["low"] for c in candles]
        
        return max(highs) - min(lows)
    
    def export_levels_json(self, filename: str = "intraday_levels.json"):
        """Export all calculated levels to JSON"""
        levels_dict = {stock: level.to_dict() for stock, level in self.levels_cache.items()}
        with open(filename, 'w') as f:
            json.dump(levels_dict, f, indent=2)
    
    def export_candles_json(self, filename: str = "intraday_candles.json"):
        """Export all candles to JSON"""
        export_data = {}
        for stock, timeframes in self.candles_cache.items():
            export_data[stock] = {
                tf: [c.to_dict() for c in candles] 
                for tf, candles in timeframes.items()
            }
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
