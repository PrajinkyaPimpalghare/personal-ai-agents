"""
Financial Metrics Module - Calculate common stock and portfolio metrics

Implements all standard financial metrics for portfolio analysis:
- Return calculations (absolute, percentage, CAGR, annualized)
- Valuation ratios (P/E, P/B, PEG, dividend yield)
- Profitability metrics (margin, ROE, ROIC)
- Holding period calculations

All calculations are deterministic and designed for fast computation with minimal overhead.
"""

from datetime import datetime
from typing import Union, Tuple


def absolute_return(current_price: float, purchase_price: float) -> float:
    """
    Calculate absolute return in rupees.
    
    Args:
        current_price: Current stock price (₹)
        purchase_price: Purchase price (₹)
    
    Returns:
        Absolute return in rupees (can be negative)
    
    Example:
        >>> absolute_return(150, 100)
        50.0
    """
    return round(current_price - purchase_price, 2)


def percentage_return(current_price: float, purchase_price: float) -> float:
    """
    Calculate percentage return.
    
    Formula: ((Current - Purchase) / Purchase) × 100
    
    Args:
        current_price: Current stock price (₹)
        purchase_price: Purchase price (₹)
    
    Returns:
        Percentage return (can be negative)
    
    Example:
        >>> percentage_return(150, 100)
        50.0
    """
    if purchase_price == 0:
        return 0.0
    return round(((current_price - purchase_price) / purchase_price) * 100, 2)


def cagr(start_value: float, end_value: float, years: float) -> float:
    """
    Calculate Compound Annual Growth Rate.
    
    Formula: (End Value / Start Value)^(1/Years) - 1
    
    Args:
        start_value: Starting value (₹)
        end_value: Ending value (₹)
        years: Number of years
    
    Returns:
        CAGR as decimal (0.20 = 20%)
    
    Example:
        >>> cagr(100000, 250000, 5)
        0.2  # 20% CAGR
    """
    if start_value == 0 or years == 0:
        return 0.0
    return round((end_value / start_value) ** (1 / years) - 1, 4)


def pe_ratio(stock_price: float, eps: float) -> float:
    """
    Calculate Price-to-Earnings ratio.
    
    Formula: Stock Price / EPS
    
    Args:
        stock_price: Current stock price (₹)
        eps: Earnings per share (₹)
    
    Returns:
        P/E ratio (unitless)
    
    Example:
        >>> pe_ratio(3000, 150)
        20.0
    """
    if eps == 0:
        return 0.0
    return round(stock_price / eps, 2)


def pb_ratio(stock_price: float, book_value_per_share: float) -> float:
    """
    Calculate Price-to-Book ratio.
    
    Formula: Stock Price / Book Value Per Share
    
    Args:
        stock_price: Current stock price (₹)
        book_value_per_share: Book value per share (₹)
    
    Returns:
        P/B ratio (unitless)
    
    Example:
        >>> pb_ratio(1500, 200)
        7.5
    """
    if book_value_per_share == 0:
        return 0.0
    return round(stock_price / book_value_per_share, 2)


def peg_ratio(pe_ratio_value: float, eps_growth_rate: float) -> float:
    """
    Calculate PEG Ratio (P/E to Growth).
    
    Formula: P/E Ratio / Expected EPS Growth Rate (%)
    
    Args:
        pe_ratio_value: P/E ratio (from pe_ratio function)
        eps_growth_rate: Expected EPS growth rate as % (e.g., 12 for 12%)
    
    Returns:
        PEG ratio (unitless)
    
    Example:
        >>> peg_ratio(24, 12)
        2.0
    """
    if eps_growth_rate == 0:
        return 0.0
    return round(pe_ratio_value / eps_growth_rate, 2)


def dividend_yield(dividend_per_share: float, stock_price: float) -> float:
    """
    Calculate Dividend Yield.
    
    Formula: (Dividend Per Share / Stock Price) × 100
    
    Args:
        dividend_per_share: Annual dividend per share (₹)
        stock_price: Current stock price (₹)
    
    Returns:
        Dividend yield as percentage (4.0 = 4%)
    
    Example:
        >>> dividend_yield(48, 1200)
        4.0
    """
    if stock_price == 0:
        return 0.0
    return round((dividend_per_share / stock_price) * 100, 2)


def profit_margin(net_profit: float, revenue: float) -> float:
    """
    Calculate Net Profit Margin.
    
    Formula: (Net Profit / Revenue) × 100
    
    Args:
        net_profit: Net profit (₹ Cr or consistent units)
        revenue: Total revenue (₹ Cr or consistent units)
    
    Returns:
        Profit margin as percentage (15.0 = 15%)
    
    Example:
        >>> profit_margin(20000, 100000)
        20.0  # 20% margin
    """
    if revenue == 0:
        return 0.0
    return round((net_profit / revenue) * 100, 2)


def roe(net_profit: float, shareholder_equity: float) -> float:
    """
    Calculate Return on Equity.
    
    Formula: (Net Profit / Shareholder Equity) × 100
    
    Args:
        net_profit: Net profit (₹ Cr)
        shareholder_equity: Shareholders' equity (₹ Cr)
    
    Returns:
        ROE as percentage (25.0 = 25%)
    
    Example:
        >>> roe(5000, 20000)
        25.0
    """
    if shareholder_equity == 0:
        return 0.0
    return round((net_profit / shareholder_equity) * 100, 2)


def roic(nopat: float, invested_capital: float) -> float:
    """
    Calculate Return on Invested Capital.
    
    Formula: (NOPAT / Invested Capital) × 100
    
    Note: NOPAT = Net Operating Profit After Tax
    
    Args:
        nopat: Net Operating Profit After Tax (₹ Cr)
        invested_capital: Invested capital (₹ Cr)
    
    Returns:
        ROIC as percentage
    
    Example:
        >>> roic(15000, 60000)
        25.0
    """
    if invested_capital == 0:
        return 0.0
    return round((nopat / invested_capital) * 100, 2)


def days_held(purchase_date: Union[str, datetime], current_date: Union[str, datetime] = None) -> int:
    """
    Calculate number of days stock has been held.
    
    Args:
        purchase_date: Purchase date (str 'YYYY-MM-DD' or datetime object)
        current_date: Current date (str 'YYYY-MM-DD' or datetime object, defaults to today)
    
    Returns:
        Number of days held
    
    Example:
        >>> days_held('2021-06-15', '2026-03-29')
        1753
    """
    if isinstance(purchase_date, str):
        purchase_date = datetime.strptime(purchase_date, '%Y-%m-%d').date()
    elif isinstance(purchase_date, datetime):
        purchase_date = purchase_date.date()
    
    if current_date is None:
        current_date = datetime.now().date()
    elif isinstance(current_date, str):
        current_date = datetime.strptime(current_date, '%Y-%m-%d').date()
    elif isinstance(current_date, datetime):
        current_date = current_date.date()
    
    return (current_date - purchase_date).days


def annualized_return(return_percentage: float, num_days: int) -> float:
    """
    Calculate annualized return.
    
    Formula: (1 + Return)^(365/Days Held) - 1
    
    Args:
        return_percentage: Return as percentage (e.g., 50 for 50%)
        num_days: Number of days held
    
    Returns:
        Annualized return as percentage
    
    Example:
        >>> annualized_return(91.6, 2000)  # 91.6% return over 2000 days
        16.76  # ~16.76% annualized
    """
    if num_days == 0 or num_days < 1:
        return 0.0
    
    return_multiplier = 1 + (return_percentage / 100)
    years = num_days / 365
    annualized = (return_multiplier ** year - 1) * 100
    return round(annualized, 2)


# Convenience function for quick metric lookup
def get_stock_metrics(
    current_price: float,
    purchase_price: float,
    purchase_date: Union[str, datetime],
    eps: float = None,
    book_value_per_share: float = None,
    dividend_per_share: float = None,
) -> dict:
    """
    Calculate all available metrics for a stock in one call.
    
    Args:
        current_price: Current stock price (₹)
        purchase_price: Purchase price (₹)
        purchase_date: Purchase date (str 'YYYY-MM-DD' or datetime)
        eps: Earnings per share (optional)
        book_value_per_share: Book value per share (optional)
        dividend_per_share: Annual dividend per share (optional)
    
    Returns:
        Dictionary with all calculated metrics
    
    Example:
        >>> metrics = get_stock_metrics(1820, 950, '2020-01-01', eps=82)
        >>> metrics['percentage_return']
        91.58
    """
    days = days_held(purchase_date)
    years = days / 365.25
    abs_ret = absolute_return(current_price, purchase_price)
    pct_ret = percentage_return(current_price, purchase_price)
    
    metrics = {
        'absolute_return': abs_ret,
        'percentage_return': pct_ret,
        'days_held': days,
        'years_held': round(years, 2),
        'annualized_return': annualized_return(pct_ret, days) if years > 0 else 0,
    }
    
    # Add ratio metrics if data provided
    if eps is not None:
        metrics['pe_ratio'] = pe_ratio(current_price, eps)
    
    if book_value_per_share is not None:
        metrics['pb_ratio'] = pb_ratio(current_price, book_value_per_share)
    
    if dividend_per_share is not None:
        metrics['dividend_yield'] = dividend_yield(dividend_per_share, current_price)
    
    return metrics
