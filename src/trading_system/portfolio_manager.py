"""
Portfolio Manager
=================

Manages portfolio positions, performance tracking, and reporting.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import logging
import json
from pathlib import Path

from .config import TradingConfig
from .risk_manager import Position, PositionType, RiskMetrics
from .data_manager import DataManager, StockData

logger = logging.getLogger(__name__)


@dataclass
class PortfolioPerformance:
    """Portfolio performance metrics."""
    total_return: float
    total_return_pct: float
    annualized_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    profit_factor: float
    avg_trade_duration: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    largest_win: float
    largest_loss: float
    avg_win: float
    avg_loss: float
    current_streak: int
    max_consecutive_wins: int
    max_consecutive_losses: int


@dataclass
class DailyPerformance:
    """Daily performance snapshot."""
    date: datetime
    portfolio_value: float
    daily_pnl: float
    daily_return: float
    positions_count: int
    cash_balance: float
    exposure: float


class PortfolioManager:
    """Comprehensive portfolio management system."""
    
    def __init__(self, config: TradingConfig, data_manager: DataManager):
        self.config = config
        self.data_manager = data_manager
        self.positions: Dict[str, Position] = {}
        self.trade_history: List[Dict] = []
        self.daily_performance: List[DailyPerformance] = []
        self.initial_capital = config.capital
        self.current_capital = config.capital
        
        # Performance tracking
        self.portfolio_values = []
        self.equity_curve = pd.DataFrame()
        
        # Data persistence
        self.data_dir = Path("data/portfolio")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing data
        self._load_portfolio_data()
    
    def update_portfolio(self, current_prices: Dict[str, float]) -> None:
        """Update portfolio with current market prices."""
        try:
            # Update position prices
            for symbol, position in self.positions.items():
                if symbol in current_prices:
                    position.update_price(current_prices[symbol])
            
            # Calculate portfolio metrics
            portfolio_value = self._calculate_portfolio_value()
            daily_pnl = portfolio_value - self.current_capital
            daily_return = (daily_pnl / self.current_capital) * 100 if self.current_capital > 0 else 0
            
            # Record daily performance
            self._record_daily_performance(portfolio_value, daily_pnl, daily_return)
            
            # Update equity curve
            self._update_equity_curve()
            
        except Exception as e:
            logger.error(f"Error updating portfolio: {e}")
    
    def add_position(self, position: Position) -> bool:
        """Add a new position to the portfolio."""
        try:
            if position.symbol in self.positions:
                logger.warning(f"Position for {position.symbol} already exists")
                return False
            
            # Calculate position cost
            position_cost = position.entry_price * position.quantity
            
            # Check if we have enough capital
            if position_cost > self.current_capital:
                logger.error(f"Insufficient capital for {position.symbol}")
                return False
            
            # Add position
            self.positions[position.symbol] = position
            self.current_capital -= position_cost
            
            # Record trade
            trade_record = {
                'action': 'OPEN',
                'symbol': position.symbol,
                'type': position.position_type.value,
                'price': position.entry_price,
                'quantity': position.quantity,
                'value': position_cost,
                'timestamp': position.entry_date,
                'stop_loss': position.stop_loss,
                'take_profit': position.take_profit
            }
            self.trade_history.append(trade_record)
            
            logger.info(f"Added position: {position.symbol} {position.position_type.value} {position.quantity} @ ₹{position.entry_price}")
            
            # Save portfolio state
            self._save_portfolio_data()
            
            return True
            
        except Exception as e:
            logger.error(f"Error adding position for {position.symbol}: {e}")
            return False
    
    def close_position(self, symbol: str, exit_price: float, reason: str = "Manual") -> bool:
        """Close a position and update portfolio."""
        try:
            if symbol not in self.positions:
                logger.warning(f"No position found for {symbol}")
                return False
            
            position = self.positions[symbol]
            position.update_price(exit_price)
            
            # Calculate realized P&L
            if position.position_type == PositionType.LONG:
                realized_pnl = (exit_price - position.entry_price) * position.quantity
            else:
                realized_pnl = (position.entry_price - exit_price) * position.quantity
            
            # Update capital
            exit_value = exit_price * position.quantity
            self.current_capital += exit_value
            
            # Record trade
            trade_record = {
                'action': 'CLOSE',
                'symbol': symbol,
                'type': position.position_type.value,
                'entry_price': position.entry_price,
                'exit_price': exit_price,
                'quantity': position.quantity,
                'entry_value': position.entry_price * position.quantity,
                'exit_value': exit_value,
                'pnl': realized_pnl,
                'pnl_pct': (realized_pnl / (position.entry_price * position.quantity)) * 100,
                'reason': reason,
                'entry_date': position.entry_date,
                'exit_date': datetime.now(),
                'hold_days': (datetime.now() - position.entry_date).days
            }
            self.trade_history.append(trade_record)
            
            # Remove position
            del self.positions[symbol]
            
            logger.info(f"Closed position: {symbol} @ ₹{exit_price}, P&L: ₹{realized_pnl:.2f}")
            
            # Save portfolio state
            self._save_portfolio_data()
            
            return True
            
        except Exception as e:
            logger.error(f"Error closing position for {symbol}: {e}")
            return False
    
    def get_portfolio_summary(self) -> Dict[str, any]:
        """Get comprehensive portfolio summary."""
        try:
            # Current positions
            total_unrealized_pnl = sum(pos.unrealized_pnl for pos in self.positions.values())
            total_position_value = sum(pos.get_position_value() for pos in self.positions.values())
            portfolio_value = self.current_capital + total_position_value
            
            # Performance metrics
            total_return = portfolio_value - self.initial_capital
            total_return_pct = (total_return / self.initial_capital) * 100
            
            # Exposure metrics
            exposure = (total_position_value / portfolio_value) * 100 if portfolio_value > 0 else 0
            cash_pct = (self.current_capital / portfolio_value) * 100 if portfolio_value > 0 else 100
            
            return {
                'portfolio_value': portfolio_value,
                'initial_capital': self.initial_capital,
                'current_capital': self.current_capital,
                'total_return': total_return,
                'total_return_pct': total_return_pct,
                'unrealized_pnl': total_unrealized_pnl,
                'position_value': total_position_value,
                'exposure_pct': exposure,
                'cash_pct': cash_pct,
                'positions_count': len(self.positions),
                'total_trades': len([t for t in self.trade_history if t['action'] == 'CLOSE'])
            }
            
        except Exception as e:
            logger.error(f"Error calculating portfolio summary: {e}")
            return {}
    
    def get_performance_metrics(self) -> PortfolioPerformance:
        """Calculate comprehensive performance metrics."""
        try:
            closed_trades = [t for t in self.trade_history if t['action'] == 'CLOSE']
            
            if not closed_trades:
                return PortfolioPerformance(
                    total_return=0, total_return_pct=0, annualized_return=0,
                    sharpe_ratio=0, max_drawdown=0, win_rate=0, profit_factor=0,
                    avg_trade_duration=0, total_trades=0, winning_trades=0,
                    losing_trades=0, largest_win=0, largest_loss=0,
                    avg_win=0, avg_loss=0, current_streak=0,
                    max_consecutive_wins=0, max_consecutive_losses=0
                )
            
            # Basic metrics
            total_trades = len(closed_trades)
            winning_trades = len([t for t in closed_trades if t['pnl'] > 0])
            losing_trades = total_trades - winning_trades
            
            # P&L metrics
            total_pnl = sum(t['pnl'] for t in closed_trades)
            win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
            
            wins = [t['pnl'] for t in closed_trades if t['pnl'] > 0]
            losses = [abs(t['pnl']) for t in closed_trades if t['pnl'] < 0]
            
            avg_win = np.mean(wins) if wins else 0
            avg_loss = np.mean(losses) if losses else 0
            largest_win = max(wins) if wins else 0
            largest_loss = -min([t['pnl'] for t in closed_trades if t['pnl'] < 0]) if losses else 0
            
            profit_factor = sum(wins) / sum(losses) if losses and sum(losses) > 0 else float('inf') if wins else 0
            
            # Duration metrics
            durations = [t['hold_days'] for t in closed_trades if 'hold_days' in t]
            avg_trade_duration = np.mean(durations) if durations else 0
            
            # Portfolio metrics
            portfolio_summary = self.get_portfolio_summary()
            total_return = portfolio_summary.get('total_return', 0)
            total_return_pct = portfolio_summary.get('total_return_pct', 0)
            
            # Annualized return (assuming data spans less than a year for now)
            annualized_return = total_return_pct  # Simplified
            
            # Sharpe ratio (simplified calculation)
            if self.daily_performance:
                daily_returns = [dp.daily_return for dp in self.daily_performance]
                if len(daily_returns) > 1:
                    sharpe_ratio = np.mean(daily_returns) / np.std(daily_returns) * np.sqrt(252) if np.std(daily_returns) > 0 else 0
                else:
                    sharpe_ratio = 0
            else:
                sharpe_ratio = 0
            
            # Drawdown calculation
            max_drawdown = self._calculate_max_drawdown()
            
            # Streak calculations
            current_streak, max_consecutive_wins, max_consecutive_losses = self._calculate_streaks(closed_trades)
            
            return PortfolioPerformance(
                total_return=total_return,
                total_return_pct=total_return_pct,
                annualized_return=annualized_return,
                sharpe_ratio=sharpe_ratio,
                max_drawdown=max_drawdown,
                win_rate=win_rate,
                profit_factor=profit_factor,
                avg_trade_duration=avg_trade_duration,
                total_trades=total_trades,
                winning_trades=winning_trades,
                losing_trades=losing_trades,
                largest_win=largest_win,
                largest_loss=largest_loss,
                avg_win=avg_win,
                avg_loss=avg_loss,
                current_streak=current_streak,
                max_consecutive_wins=max_consecutive_wins,
                max_consecutive_losses=max_consecutive_losses
            )
            
        except Exception as e:
            logger.error(f"Error calculating performance metrics: {e}")
            return PortfolioPerformance(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    
    def get_equity_curve(self) -> pd.DataFrame:
        """Get portfolio equity curve."""
        if self.equity_curve.empty:
            self._update_equity_curve()
        return self.equity_curve
    
    def get_monthly_returns(self) -> pd.DataFrame:
        """Calculate monthly returns."""
        try:
            if self.daily_performance:
                df = pd.DataFrame([asdict(dp) for dp in self.daily_performance])
                df['date'] = pd.to_datetime(df['date'])
                df.set_index('date', inplace=True)
                
                # Resample to monthly
                monthly = df['portfolio_value'].resample('M').last()
                monthly_returns = monthly.pct_change() * 100
                
                return monthly_returns.to_frame('monthly_return')
            else:
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error calculating monthly returns: {e}")
            return pd.DataFrame()
    
    def _calculate_portfolio_value(self) -> float:
        """Calculate total portfolio value."""
        position_value = sum(pos.get_position_value() for pos in self.positions.values())
        return self.current_capital + position_value
    
    def _record_daily_performance(self, portfolio_value: float, daily_pnl: float, daily_return: float) -> None:
        """Record daily performance snapshot."""
        daily_perf = DailyPerformance(
            date=datetime.now().date(),
            portfolio_value=portfolio_value,
            daily_pnl=daily_pnl,
            daily_return=daily_return,
            positions_count=len(self.positions),
            cash_balance=self.current_capital,
            exposure=(sum(pos.get_position_value() for pos in self.positions.values()) / portfolio_value) * 100 if portfolio_value > 0 else 0
        )
        
        # Update or add today's performance
        today = datetime.now().date()
        for i, dp in enumerate(self.daily_performance):
            if dp.date == today:
                self.daily_performance[i] = daily_perf
                return
        
        self.daily_performance.append(daily_perf)
    
    def _update_equity_curve(self) -> None:
        """Update equity curve DataFrame."""
        try:
            if self.daily_performance:
                data = []
                for dp in self.daily_performance:
                    data.append({
                        'date': dp.date,
                        'portfolio_value': dp.portfolio_value,
                        'daily_return': dp.daily_return,
                        'cumulative_return': ((dp.portfolio_value - self.initial_capital) / self.initial_capital) * 100
                    })
                
                self.equity_curve = pd.DataFrame(data)
                self.equity_curve['date'] = pd.to_datetime(self.equity_curve['date'])
                self.equity_curve.set_index('date', inplace=True)
                
        except Exception as e:
            logger.error(f"Error updating equity curve: {e}")
    
    def _calculate_max_drawdown(self) -> float:
        """Calculate maximum drawdown."""
        try:
            if not self.daily_performance:
                return 0.0
            
            portfolio_values = [dp.portfolio_value for dp in self.daily_performance]
            
            peak = portfolio_values[0]
            max_drawdown = 0.0
            
            for value in portfolio_values:
                if value > peak:
                    peak = value
                
                drawdown = (peak - value) / peak * 100
                max_drawdown = max(max_drawdown, drawdown)
            
            return max_drawdown
            
        except Exception as e:
            logger.error(f"Error calculating max drawdown: {e}")
            return 0.0
    
    def _calculate_streaks(self, closed_trades: List[Dict]) -> Tuple[int, int, int]:
        """Calculate win/loss streaks."""
        try:
            if not closed_trades:
                return 0, 0, 0
            
            # Sort trades by date
            sorted_trades = sorted(closed_trades, key=lambda x: x.get('exit_date', datetime.now()))
            
            current_streak = 0
            max_consecutive_wins = 0
            max_consecutive_losses = 0
            
            current_win_streak = 0
            current_loss_streak = 0
            
            for trade in sorted_trades:
                if trade['pnl'] > 0:
                    current_win_streak += 1
                    current_loss_streak = 0
                    max_consecutive_wins = max(max_consecutive_wins, current_win_streak)
                else:
                    current_loss_streak += 1
                    current_win_streak = 0
                    max_consecutive_losses = max(max_consecutive_losses, current_loss_streak)
            
            # Current streak (last trade result)
            if sorted_trades:
                last_trade = sorted_trades[-1]
                if last_trade['pnl'] > 0:
                    current_streak = current_win_streak
                else:
                    current_streak = -current_loss_streak
            
            return current_streak, max_consecutive_wins, max_consecutive_losses
            
        except Exception as e:
            logger.error(f"Error calculating streaks: {e}")
            return 0, 0, 0
    
    def _save_portfolio_data(self) -> None:
        """Save portfolio data to files."""
        try:
            # Save positions
            positions_data = {}
            for symbol, position in self.positions.items():
                positions_data[symbol] = {
                    'symbol': position.symbol,
                    'position_type': position.position_type.value,
                    'entry_price': position.entry_price,
                    'quantity': position.quantity,
                    'entry_date': position.entry_date.isoformat(),
                    'stop_loss': position.stop_loss,
                    'take_profit': position.take_profit,
                    'trailing_stop': position.trailing_stop,
                    'current_price': position.current_price
                }
            
            with open(self.data_dir / "positions.json", 'w') as f:
                json.dump(positions_data, f, indent=2)
            
            # Save trade history
            trade_history_serializable = []
            for trade in self.trade_history:
                trade_copy = trade.copy()
                # Convert datetime objects to strings
                for key, value in trade_copy.items():
                    if isinstance(value, datetime):
                        trade_copy[key] = value.isoformat()
                trade_history_serializable.append(trade_copy)
            
            with open(self.data_dir / "trade_history.json", 'w') as f:
                json.dump(trade_history_serializable, f, indent=2)
            
            # Save portfolio state
            portfolio_state = {
                'current_capital': self.current_capital,
                'initial_capital': self.initial_capital,
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.data_dir / "portfolio_state.json", 'w') as f:
                json.dump(portfolio_state, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving portfolio data: {e}")
    
    def _load_portfolio_data(self) -> None:
        """Load portfolio data from files."""
        try:
            # Load positions
            positions_file = self.data_dir / "positions.json"
            if positions_file.exists():
                with open(positions_file, 'r') as f:
                    positions_data = json.load(f)
                
                for symbol, pos_data in positions_data.items():
                    position = Position(
                        symbol=pos_data['symbol'],
                        position_type=PositionType(pos_data['position_type']),
                        entry_price=pos_data['entry_price'],
                        quantity=pos_data['quantity'],
                        entry_date=datetime.fromisoformat(pos_data['entry_date']),
                        stop_loss=pos_data['stop_loss'],
                        take_profit=pos_data['take_profit'],
                        trailing_stop=pos_data.get('trailing_stop'),
                        current_price=pos_data.get('current_price', pos_data['entry_price'])
                    )
                    self.positions[symbol] = position
            
            # Load trade history
            trade_history_file = self.data_dir / "trade_history.json"
            if trade_history_file.exists():
                with open(trade_history_file, 'r') as f:
                    trade_history_data = json.load(f)
                
                for trade in trade_history_data:
                    # Convert ISO strings back to datetime
                    for key, value in trade.items():
                        if key in ['timestamp', 'entry_date', 'exit_date'] and isinstance(value, str):
                            try:
                                trade[key] = datetime.fromisoformat(value)
                            except ValueError:
                                pass
                    self.trade_history.append(trade)
            
            # Load portfolio state
            portfolio_state_file = self.data_dir / "portfolio_state.json"
            if portfolio_state_file.exists():
                with open(portfolio_state_file, 'r') as f:
                    portfolio_state = json.load(f)
                
                self.current_capital = portfolio_state.get('current_capital', self.config.capital)
                self.initial_capital = portfolio_state.get('initial_capital', self.config.capital)
                
        except Exception as e:
            logger.error(f"Error loading portfolio data: {e}")
    
    def generate_portfolio_report(self) -> str:
        """Generate comprehensive portfolio report."""
        try:
            summary = self.get_portfolio_summary()
            performance = self.get_performance_metrics()
            
            report = f"Portfolio Performance Report\n"
            report += f"{'='*60}\n"
            report += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            
            # Portfolio Summary
            report += f"Portfolio Summary:\n"
            report += f"{'-'*40}\n"
            report += f"Initial Capital: ₹{summary.get('initial_capital', 0):,.2f}\n"
            report += f"Current Value: ₹{summary.get('portfolio_value', 0):,.2f}\n"
            report += f"Total Return: ₹{summary.get('total_return', 0):,.2f} ({summary.get('total_return_pct', 0):.2f}%)\n"
            report += f"Cash Balance: ₹{summary.get('current_capital', 0):,.2f} ({summary.get('cash_pct', 0):.1f}%)\n"
            report += f"Positions Value: ₹{summary.get('position_value', 0):,.2f} ({summary.get('exposure_pct', 0):.1f}%)\n"
            report += f"Unrealized P&L: ₹{summary.get('unrealized_pnl', 0):,.2f}\n"
            report += f"Active Positions: {summary.get('positions_count', 0)}\n\n"
            
            # Performance Metrics
            report += f"Performance Metrics:\n"
            report += f"{'-'*40}\n"
            report += f"Total Trades: {performance.total_trades}\n"
            report += f"Win Rate: {performance.win_rate:.1f}% ({performance.winning_trades}W/{performance.losing_trades}L)\n"
            report += f"Profit Factor: {performance.profit_factor:.2f}\n"
            report += f"Avg Win: ₹{performance.avg_win:,.2f}\n"
            report += f"Avg Loss: ₹{performance.avg_loss:,.2f}\n"
            report += f"Largest Win: ₹{performance.largest_win:,.2f}\n"
            report += f"Largest Loss: ₹{performance.largest_loss:,.2f}\n"
            report += f"Avg Trade Duration: {performance.avg_trade_duration:.1f} days\n"
            report += f"Max Drawdown: {performance.max_drawdown:.2f}%\n"
            report += f"Sharpe Ratio: {performance.sharpe_ratio:.2f}\n"
            report += f"Current Streak: {performance.current_streak}\n\n"
            
            # Current Positions
            if self.positions:
                report += f"Current Positions:\n"
                report += f"{'-'*40}\n"
                report += f"{'Symbol':<12} {'Type':<6} {'Qty':<8} {'Entry':<10} {'Current':<10} {'P&L':<10} {'P&L%':<8}\n"
                report += f"{'-'*70}\n"
                
                for position in self.positions.values():
                    pnl_pct = position.get_return_percentage()
                    report += f"{position.symbol:<12} {position.position_type.value:<6} {position.quantity:<8} "
                    report += f"₹{position.entry_price:<9.2f} ₹{position.current_price:<9.2f} "
                    report += f"₹{position.unrealized_pnl:<9.2f} {pnl_pct:<7.2f}%\n"
            else:
                report += f"No active positions\n"
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating portfolio report: {e}")
            return "Error generating portfolio report"
