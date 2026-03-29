"""
Intraday Paper Trader - Dummy Trade Tracking

Simulates intraday trades without real money. Tracks:
- Entry: Stock, time, price, quantity
- Exit: Time, price, profit/loss
- Daily P&L, win rate, statistics

All trades stored in JSON file for analysis.
"""

import json
import os
from datetime import datetime, time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import statistics


@dataclass
class IntradayTrade:
    """Single intraday trade record"""
    trade_id: str                    # Unique ID: INFY_20260329_093000_1
    stock: str                       # Stock symbol
    entry_date: str                  # YYYY-MM-DD
    entry_time: str                  # HH:MM:SS (IST)
    entry_price: float               # Entry price
    quantity: int                    # Shares
    entry_setup: str                 # ORB / Pivot / Momentum / S-R
    
    exit_time: Optional[str] = None  # HH:MM:SS (IST)
    exit_price: Optional[float] = None
    exit_reason: Optional[str] = None  # Hit target / Stop loss / 3:15 PM close
    
    # Calculated fields
    status: str = "OPEN"             # OPEN / CLOSED
    profit_loss: Optional[float] = None
    profit_loss_pct: Optional[float] = None
    broker_charges: float = 0        # ₹10-20 per trade
    net_profit_loss: Optional[float] = None
    risk_reward_ratio: Optional[float] = None
    
    def close_trade(self, exit_price: float, exit_time: str, exit_reason: str, broker_charges: float = 15.0):
        """Close an open trade"""
        self.exit_price = exit_price
        self.exit_time = exit_time
        self.exit_reason = exit_reason
        self.broker_charges = broker_charges
        
        # Calculate P&L
        self.profit_loss = (exit_price - self.entry_price) * self.quantity
        self.net_profit_loss = self.profit_loss - broker_charges
        self.profit_loss_pct = ((exit_price - self.entry_price) / self.entry_price) * 100
        
        self.status = "CLOSED"
        
    def calculate_risk_reward(self, stop_loss: float, target: float):
        """Calculate potential risk-reward ratio"""
        risk = abs(self.entry_price - stop_loss)
        reward = abs(target - self.entry_price)
        if risk > 0:
            self.risk_reward_ratio = reward / risk
            

class IntradayPaperTrader:
    """Paper trading engine for intraday trades"""
    
    def __init__(self, trades_file: str = "intraday_trades.json", daily_loss_limit: float = 5000.0):
        """
        Initialize paper trader
        
        Args:
            trades_file: Path to store trades JSON
            daily_loss_limit: Max loss allowed per day (₹5,000)
        """
        self.trades_file = trades_file
        self.daily_loss_limit = daily_loss_limit
        self.trades: Dict[str, IntradayTrade] = {}
        self.open_trades: List[str] = []  # Trade IDs of open positions
        
        self.min_risk_reward = 1.5  # Minimum 1:1.5 ratio
        self.max_trades_per_day = 5
        self.auto_close_time = "15:15:00"  # 3:15 PM IST
        
        self._load_trades()
    
    def _load_trades(self):
        """Load existing trades from file"""
        if os.path.exists(self.trades_file):
            try:
                with open(self.trades_file, 'r') as f:
                    trades_data = json.load(f)
                    for trade_id, trade_dict in trades_data.items():
                        self.trades[trade_id] = IntradayTrade(**trade_dict)
            except Exception as e:
                print(f"Error loading trades: {e}")
    
    def _save_trades(self):
        """Save all trades to file"""
        trades_dict = {tid: asdict(trade) for tid, trade in self.trades.items()}
        with open(self.trades_file, 'w') as f:
            json.dump(trades_dict, f, indent=2)
    
    def generate_trade_id(self, stock: str, entry_time: str) -> str:
        """Generate unique trade ID: STOCK_YYYYMMDD_HHMMSS_N"""
        date_str = datetime.now().strftime("%Y%m%d")
        time_str = entry_time.replace(":", "")
        counter = 1
        base_id = f"{stock}_{date_str}_{time_str}"
        trade_id = f"{base_id}_{counter}"
        
        while trade_id in self.trades:
            counter += 1
            trade_id = f"{base_id}_{counter}"
        
        return trade_id
    
    def open_trade(self, stock: str, entry_price: float, entry_time: str, 
                   quantity: int, setup: str, stop_loss: float, target: float) -> Tuple[bool, str]:
        """
        Open a new intraday trade
        
        Args:
            stock: Stock symbol (e.g., 'INFY')
            entry_price: Entry price
            entry_time: Entry time (HH:MM:SS)
            quantity: Number of shares
            setup: Setup type (ORB, Pivot, Momentum, S-R)
            stop_loss: Stop loss price
            target: Target price
        
        Returns:
            (success, message)
        """
        # Check daily loss limit
        today_trades = self._get_today_trades()
        today_loss = self._calculate_today_loss()
        
        if today_loss <= -self.daily_loss_limit:
            return False, f"Daily loss limit (₹{self.daily_loss_limit}) reached"
        
        # Check max trades per day
        if len(today_trades) >= self.max_trades_per_day:
            return False, f"Max {self.max_trades_per_day} trades per day limit reached"
        
        # Check risk-reward ratio
        risk = abs(entry_price - stop_loss)
        reward = abs(target - entry_price)
        if risk > 0:
            rr_ratio = reward / risk
            if rr_ratio < self.min_risk_reward:
                return False, f"R:R ratio {rr_ratio:.2f} < minimum {self.min_risk_reward}"
        
        # Create trade
        trade_id = self.generate_trade_id(stock, entry_time)
        entry_date = datetime.now().strftime("%Y-%m-%d")
        
        trade = IntradayTrade(
            trade_id=trade_id,
            stock=stock,
            entry_date=entry_date,
            entry_time=entry_time,
            entry_price=entry_price,
            quantity=quantity,
            entry_setup=setup
        )
        trade.calculate_risk_reward(stop_loss, target)
        
        self.trades[trade_id] = trade
        self.open_trades.append(trade_id)
        self._save_trades()
        
        potential_pnl = (target - entry_price) * quantity
        return True, f"Trade opened: {trade_id} | Entry: ₹{entry_price} | Target: ₹{target} | Potential: ₹{potential_pnl:.0f}"
    
    def close_trade(self, trade_id: str, exit_price: float, exit_time: str, 
                    exit_reason: str) -> Tuple[bool, str]:
        """Close an open trade"""
        if trade_id not in self.trades:
            return False, f"Trade {trade_id} not found"
        
        trade = self.trades[trade_id]
        if trade.status == "CLOSED":
            return False, f"Trade {trade_id} already closed"
        
        trade.close_trade(exit_price, exit_time, exit_reason)
        self.open_trades.remove(trade_id)
        self._save_trades()
        
        return True, f"Trade closed: {trade_id} | Exit: ₹{exit_price} | P&L: ₹{trade.net_profit_loss:.0f} ({trade.profit_loss_pct:.2f}%)"
    
    def close_all_trades_at_time(self, close_time: str, close_price_dict: Dict[str, float]) -> Dict[str, str]:
        """Close all open trades at specific time (e.g., 3:15 PM)"""
        results = {}
        for trade_id in list(self.open_trades):
            trade = self.trades[trade_id]
            if trade.stock in close_price_dict:
                exit_price = close_price_dict[trade.stock]
                success, msg = self.close_trade(trade_id, exit_price, close_time, "3:15 PM Market Close")
                results[trade_id] = msg
        return results
    
    def _get_today_trades(self) -> List[str]:
        """Get all trades from today"""
        today = datetime.now().strftime("%Y-%m-%d")
        return [tid for tid, trade in self.trades.items() if trade.entry_date == today]
    
    def _calculate_today_loss(self) -> float:
        """Calculate today's net loss"""
        today_trades = self._get_today_trades()
        total_pnl = 0
        for tid in today_trades:
            trade = self.trades[tid]
            if trade.status == "CLOSED" and trade.net_profit_loss:
                total_pnl += trade.net_profit_loss
        return total_pnl
    
    def get_today_summary(self) -> Dict:
        """Get today's trading summary"""
        today_trades = self._get_today_trades()
        
        closed_trades = [self.trades[tid] for tid in today_trades if self.trades[tid].status == "CLOSED"]
        open_trades = [self.trades[tid] for tid in today_trades if self.trades[tid].status == "OPEN"]
        
        if not closed_trades:
            return {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "total_trades": len(today_trades),
                "closed_trades": 0,
                "open_trades": len(open_trades),
                "winning_trades": 0,
                "losing_trades": 0,
                "win_rate": 0,
                "total_profit_loss": 0,
                "avg_profit_trade": 0,
                "avg_loss_trade": 0
            }
        
        # Calculate statistics
        profits = [t.net_profit_loss for t in closed_trades if t.net_profit_loss and t.net_profit_loss > 0]
        losses = [t.net_profit_loss for t in closed_trades if t.net_profit_loss and t.net_profit_loss < 0]
        
        winning = len(profits)
        losing = len(losses)
        total_closed = winning + losing
        win_rate = (winning / total_closed * 100) if total_closed > 0 else 0
        
        total_pnl = sum([t.net_profit_loss for t in closed_trades if t.net_profit_loss])
        avg_profit = statistics.mean(profits) if profits else 0
        avg_loss = statistics.mean(losses) if losses else 0
        
        return {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "total_trades": len(today_trades),
            "closed_trades": total_closed,
            "open_trades": len(open_trades),
            "winning_trades": winning,
            "losing_trades": losing,
            "win_rate": f"{win_rate:.1f}%",
            "total_profit_loss": f"₹{total_pnl:.0f}",
            "avg_profit_per_win": f"₹{avg_profit:.0f}",
            "avg_loss_per_loss": f"₹{avg_loss:.0f}",
            "daily_limit_used": f"₹{abs(self._calculate_today_loss()):.0f} / ₹{self.daily_loss_limit:.0f}"
        }
    
    def get_weekly_summary(self, days: int = 5) -> Dict:
        """Get trading summary for last N days"""
        all_trades = list(self.trades.values())
        closed_trades = [t for t in all_trades if t.status == "CLOSED"]
        
        if not closed_trades:
            return {"message": "No closed trades yet"}
        
        profits = [t.net_profit_loss for t in closed_trades if t.net_profit_loss and t.net_profit_loss > 0]
        losses = [t.net_profit_loss for t in closed_trades if t.net_profit_loss and t.net_profit_loss < 0]
        
        winning = len(profits)
        losing = len(losses)
        total_trades = winning + losing
        
        total_pnl = sum([t.net_profit_loss for t in closed_trades if t.net_profit_loss])
        
        summary_by_setup = {}
        for trade in closed_trades:
            setup = trade.entry_setup
            if setup not in summary_by_setup:
                summary_by_setup[setup] = {"count": 0, "wins": 0, "pnl": 0}
            summary_by_setup[setup]["count"] += 1
            if trade.net_profit_loss and trade.net_profit_loss > 0:
                summary_by_setup[setup]["wins"] += 1
            summary_by_setup[setup]["pnl"] += trade.net_profit_loss or 0
        
        return {
            "total_trades": total_trades,
            "winning_trades": winning,
            "losing_trades": losing,
            "win_rate": f"{(winning/total_trades*100) if total_trades > 0 else 0:.1f}%",
            "total_profit_loss": f"₹{total_pnl:.0f}",
            "avg_profit_per_trade": f"₹{(total_pnl/total_trades) if total_trades > 0 else 0:.0f}",
            "best_trade": f"₹{max(profits) if profits else 0:.0f}",
            "worst_trade": f"₹{min(losses) if losses else 0:.0f}",
            "by_setup": summary_by_setup
        }
    
    def print_today_trades(self):
        """Pretty print today's trades"""
        today_trades = self._get_today_trades()
        if not today_trades:
            print("No trades today")
            return
        
        print(f"\n{'='*100}")
        print(f"TODAY'S TRADES - {datetime.now().strftime('%Y-%m-%d')}")
        print(f"{'='*100}")
        print(f"{'Trade ID':<25} {'Stock':<8} {'Entry':<10} {'Exit':<10} {'Status':<8} {'P&L':<12} {'%':<8} {'Setup':<10}")
        print(f"{'-'*100}")
        
        for tid in today_trades:
            trade = self.trades[tid]
            pnl_str = f"₹{trade.net_profit_loss:.0f}" if trade.net_profit_loss else "OPEN"
            pct_str = f"{trade.profit_loss_pct:.2f}%" if trade.profit_loss_pct else "OPEN"
            
            print(f"{tid:<25} {trade.stock:<8} ₹{trade.entry_price:<9.0f} "
                  f"₹{trade.exit_price if trade.exit_price else '-':<9} "
                  f"{trade.status:<8} {pnl_str:<12} {pct_str:<8} {trade.entry_setup:<10}")
        
        summary = self.get_today_summary()
        print(f"{'-'*100}")
        print(f"Total: {summary['closed_trades']} closed | {summary['open_trades']} open | "
              f"Win Rate: {summary['win_rate']} | P&L: {summary['total_profit_loss']}")
        print(f"{'='*100}\n")
