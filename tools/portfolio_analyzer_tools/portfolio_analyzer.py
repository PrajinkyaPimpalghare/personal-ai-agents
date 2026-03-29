"""
Main Portfolio Analyzer Class - Orchestration of all analysis tools

This is the main entry point for the Python tooling. It coordinates:
1. Fetching and calculating financial metrics
2. Technical indicator calculations
3. Weighted scoring
4. Risk management calculations
5. Output formatting

Usage:
    from portfolio_analyzer_tools import PortfolioAnalyzer
    
    analyzer = PortfolioAnalyzer()
    analysis = analyzer.analyze_portfolio(holdings_data)
    
Then pass analysis results to agent for narrative enhancement and recommendations.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime

from . import metrics
from . import technical_analysis
from . import scoring
from . import risk_management
from . import data_cache
from . import output_formatter


class PortfolioAnalyzer:
    """Main orchestration class for portfolio analysis."""
    
    def __init__(self, cache_enabled: bool = True):
        self.cache_enabled = cache_enabled
        if cache_enabled:
            self.cache = data_cache.DataCache()
        else:
            self.cache = None
        self.analysis_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def analyze_holding(
        self,
        symbol: str,
        quantity: float,
        purchase_price: float,
        purchase_date: str,
        current_price: float,
        **optional_data
    ) -> Dict[str, Any]:
        """
        Analyze single holding and return structured data.
        
        Args:
            symbol: Stock ticker
            quantity: Shares held
            purchase_price: Entry price (₹)
            purchase_date: Purchase date (YYYY-MM-DD)
            current_price: Current price (₹)
            **optional_data: eps, roe, pe_ratio, etc.
        
        Returns:
            Dict with all calculated metrics and analysis
        """
        # 1. Calculate basic metrics
        abs_return = metrics.absolute_return(current_price, purchase_price)
        pct_return = metrics.percentage_return(current_price, purchase_price)
        days = metrics.days_held(purchase_date)
        years = days / 365.25
        annualized = metrics.annualized_return(pct_return, days) if years > 0 else 0
        
        holding_metrics = {
            "symbol": symbol,
            "quantity": quantity,
            "purchase_price": purchase_price,
            "purchase_date": purchase_date,
            "current_price": current_price,
            "absolute_return": abs_return,
            "percentage_return": pct_return,
            "days_held": days,
            "years_held": round(years, 2),
            "annualized_return": annualized,
            "position_value": round(quantity * current_price, 2),
        }
        
        # 2. Add optional fundamental metrics if provided
        if optional_data.get("eps"):
            holding_metrics["pe_ratio"] = metrics.pe_ratio(current_price, optional_data["eps"])
        
        if optional_data.get("book_value_per_share"):
            holding_metrics["pb_ratio"] = metrics.pb_ratio(
                current_price, 
                optional_data["book_value_per_share"]
            )
        
        if optional_data.get("dividend_per_share"):
            holding_metrics["dividend_yield"] = metrics.dividend_yield(
                optional_data["dividend_per_share"],
                current_price
            )
        
        return {
            "holding": holding_metrics,
            "analysis_date": self.analysis_date,
        }
    
    def analyze_technical(
        self,
        symbol: str,
        closes: List[float] = None,
        highs: List[float] = None,
        lows: List[float] = None,
        current_price: float = None,
        mcp_callback=None
    ) -> Dict[str, Any]:
        """
        Calculate technical indicators for a stock.
        
        Args:
            symbol: Stock ticker
            closes: List of closing prices (oldest first)
            highs: List of high prices
            lows: List of low prices
            current_price: Current price
            mcp_callback: Function to fetch historical data if not provided
        
        Returns:
            Dict with all technical indicators and signal
        """
        if closes is None and mcp_callback:
            # Fetch historical data
            from datetime import datetime, timedelta
            to_date = datetime.now().strftime("%Y-%m-%d")
            from_date = (datetime.now() - timedelta(days=730)).strftime("%Y-%m-%d")
            
            hist_data = mcp_callback(symbol, from_date, to_date, "day")
            if hist_data and "data" in hist_data:
                data_points = hist_data["data"]
                closes = [d["close"] for d in data_points]
                highs = [d["high"] for d in data_points]
                lows = [d["low"] for d in data_points]
        
        if not closes or len(closes) < 20:
            return {
                "error": "Insufficient historical data",
                "symbol": symbol,
            }
        
        # Calculate all indicators
        rsi = technical_analysis.calculate_rsi(closes)
        macd, signal, histogram = technical_analysis.calculate_macd(closes)
        upper_bb, middle_bb, lower_bb = technical_analysis.calculate_bollinger_bands(closes)
        atr = technical_analysis.calculate_atr(highs, lows, closes) if highs and lows else 0
        ema_20 = technical_analysis.calculate_ema(closes, 20)
        ema_50 = technical_analysis.calculate_ema(closes, 50)
        ema_200 = technical_analysis.calculate_ema(closes, 200)
        supports, resistances = technical_analysis.find_support_resistance(closes)
        
        # Generate signal
        current_price = current_price or closes[-1]
        signal_result = technical_analysis.generate_technical_signal(
            rsi=rsi,
            macd_vs_signal=macd - signal,
            price_vs_upperbb=current_price - upper_bb,
            price_vs_lowerbb=current_price - lower_bb,
            price_vs_ema200=current_price - ema_200,
            atr_as_pct=(atr / current_price * 100) if current_price > 0 else 0,
        )
        
        return {
            "symbol": symbol,
            "current_price": current_price,
            "indicators": {
                "rsi": rsi,
                "macd": macd,
                "signal": signal,
                "histogram": histogram,
                "bollinger_upper": upper_bb,
                "bollinger_middle": middle_bb,
                "bollinger_lower": lower_bb,
                "atr": atr,
                "atr_pct": round((atr / current_price * 100), 2) if current_price > 0 else 0,
                "ema_20": ema_20,
                "ema_50": ema_50,
                "ema_200": ema_200,
            },
            "levels": {
                "supports": supports,
                "resistances": resistances,
            },
            "signal": signal_result,
        }
    
    def analyze_portfolio(
        self,
        holdings: List[Dict],
        account_size: float = None,
        mcp_callback_historical=None,
        mcp_callback_quotes=None,
    ) -> Dict[str, Any]:
        """
        Comprehensive portfolio analysis.
        
        Args:
            holdings: List of holding dicts with symbol, quantity, purchase_price, etc.
            account_size: Total account value (for risk calculation)
            mcp_callback_historical: Function to fetch historical data
            mcp_callback_quotes: Function to fetch quotes
        
        Returns:
            Dict with complete portfolio analysis
        """
        if not holdings:
            return {"error": "No holdings provided"}
        
        # Calculate total portfolio value
        if account_size is None:
            account_size = sum(h.get("quantity", 0) * h.get("current_price", 0) for h in holdings)
        
        portfolio_metrics = []
        portfolio_risk_data = []
        
        # Analyze each holding
        for holding in holdings:
            holding_analysis = self.analyze_holding(
                symbol=holding.get("symbol"),
                quantity=holding.get("quantity", 0),
                purchase_price=holding.get("purchase_price", holding.get("avg_price", 0)),
                purchase_date=holding.get("purchase_date"),
                current_price=holding.get("current_price", holding.get("last_price", 0)),
            )
            
            portfolio_metrics.append(holding_analysis["holding"])
            
            # Add to risk data dict
            portfolio_risk_data.append({
                "symbol": holding.get("symbol"),
                "quantity": holding.get("quantity", 0),
                "entry_price": holding.get("purchase_price", holding.get("avg_price", 0)),
                "current_price": holding.get("current_price", holding.get("last_price", 0)),
                "stop_loss": holding.get("stop_loss", 0),  # Optional
                "sector": holding.get("sector", "Other"),
            })
        
        # Calculate portfolio heat
        portfolio_heat_result = risk_management.portfolio_heat_calculation(
            portfolio_risk_data,
            account_size=account_size
        )
        
        # Format output
        portfolio_overview = output_formatter.format_portfolio_overview(portfolio_metrics)
        
        return {
            "analysis_date": self.analysis_date,
            "portfolio_metrics": portfolio_metrics,
            "portfolio_overview": portfolio_overview,
            "portfolio_heat": portfolio_heat_result,
            "account_size": account_size,
            "total_portfolio_value": sum(h["position_value"] for h in portfolio_metrics),
            "total_gain_loss": sum(h["absolute_return"] * h["quantity"] for h in portfolio_metrics),
        }
    
    def generate_complete_analysis(
        self,
        symbol: str,
        holding: Dict,
        technical_data: Dict = None,
        fundamental_scores: Dict = None,
        sentiment_data: Dict = None,
        macro_data: Dict = None,
    ) -> Dict[str, Any]:
        """
        Generate complete analysis for single stock (for detailed deep-dive).
        
        Args:
            symbol: Stock ticker
            holding: Holding data
            technical_data: Technical indicators
            fundamental_scores: Fundamental metrics
            sentiment_data: Sentiment inputs
            macro_data: Macro inputs
        
        Returns:
            Complete analysis with scores and formatted output
        """
        # Calculate scores
        fundamental_score = scoring.calculate_fundamental_score(
            pe_ratio=fundamental_scores.get("pe_ratio", 20) if fundamental_scores else 20,
            roe=fundamental_scores.get("roe", 15) if fundamental_scores else 15,
            revenue_growth=fundamental_scores.get("revenue_growth", 10) if fundamental_scores else 10,
        )
        
        technical_score = scoring.calculate_technical_score(
            rsi=technical_data.get("indicators", {}).get("rsi", 50) if technical_data else 50,
            macd_histogram=technical_data.get("indicators", {}).get("histogram", 0) if technical_data else 0,
        ) if technical_data else 5.0
        
        sentiment_score = scoring.calculate_sentiment_score(
            analyst_upgrades_downgrades_net=sentiment_data.get("analyst_net", 0) if sentiment_data else 0,
            retail_sentiment=sentiment_data.get("retail", "neutral") if sentiment_data else "neutral",
        )
        
        macro_score = scoring.calculate_macro_score(
            oil_price_wti=macro_data.get("oil_price", 100) if macro_data else 100,
            rupee_level=macro_data.get("rupee", 84) if macro_data else 84,
        )
        
        # For demo, assume balanced debate
        debate_score = 5.0
        
        # Total score
        total_score, verdict, confidence = scoring.calculate_total_score_and_verdict(
            fundamental_score, technical_score, sentiment_score, macro_score, debate_score
        )
        
        scores_dict = {
            "fundamental": fundamental_score,
            "technical": technical_score,
            "sentiment": sentiment_score,
            "macro": macro_score,
            "debate": debate_score,
            "total": total_score,
            "verdict": verdict,
            "confidence": confidence,
        }
        
        # Generate formatted report
        report = output_formatter.generate_analysis_report(
            stock_symbol=symbol,
            portfolio_data=holding,
            technical_data=technical_data,
            scores=scores_dict,
            risk_data={}
        )
        
        return {
            "symbol": symbol,
            "scores": scores_dict,
            "analysis_report": report,
            "analysis_date": self.analysis_date,
        }
