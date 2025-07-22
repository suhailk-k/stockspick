"""
Professional Backtesting Engine
===============================

Comprehensive backtesting system for analyzing trading strategy performance
with detailed metrics, win/loss analysis, and portfolio tracking.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class TradeStatus(Enum):
    OPEN = "OPEN"
    CLOSED_PROFIT = "CLOSED_PROFIT"
    CLOSED_LOSS = "CLOSED_LOSS"
    STOPPED_OUT = "STOPPED_OUT"

@dataclass
class BacktestTrade:
    """Individual trade record for backtesting."""
    symbol: str
    entry_date: datetime
    entry_price: float
    quantity: int
    stop_loss: float
    take_profit: float
    trailing_stop: Optional[float] = None
    trailing_stop_pct: float = 0.04  # 4% trailing stop
    exit_date: Optional[datetime] = None
    exit_price: Optional[float] = None
    exit_reason: Optional[str] = None
    pnl: Optional[float] = None
    pnl_pct: Optional[float] = None
    status: TradeStatus = TradeStatus.OPEN
    days_held: Optional[int] = None
    max_favorable: Optional[float] = None
    max_adverse: Optional[float] = None
    highest_price: Optional[float] = None  # Track highest price for trailing stops

@dataclass
class BacktestMetrics:
    """Comprehensive backtesting performance metrics."""
    # Basic Performance
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    
    # Financial Metrics
    initial_capital: float
    final_capital: float
    total_return: float
    total_return_pct: float
    max_drawdown: float
    max_drawdown_pct: float
    
    # Trade Analysis
    avg_win: float
    avg_loss: float
    largest_win: float
    largest_loss: float
    profit_factor: float
    
    # Risk Metrics
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    
    # Trade Duration
    avg_days_held: float
    avg_winning_days: float
    avg_losing_days: float
    
    # Advanced Metrics
    consecutive_wins: int
    consecutive_losses: int
    recovery_factor: float
    expectancy: float

class Backtester:
    """Professional backtesting engine."""
    
    def __init__(self, config, data_manager, technical_analyzer, risk_manager):
        self.config = config
        self.data_manager = data_manager
        self.technical_analyzer = technical_analyzer
        self.risk_manager = risk_manager
        
        self.trades: List[BacktestTrade] = []
        self.equity_curve: List[float] = []
        self.daily_returns: List[float] = []
        
    def run_backtest(self, symbols: List[str], start_date: str, end_date: str, 
                    initial_capital: float = 100000) -> BacktestMetrics:
        """
        Run comprehensive backtest on given symbols and date range.
        
        Args:
            symbols: List of stock symbols to test
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            initial_capital: Starting capital in INR
            
        Returns:
            BacktestMetrics with comprehensive performance analysis
        """
        logger.info(f"Starting backtest: {len(symbols)} symbols, {start_date} to {end_date}")
        
        self.trades = []
        self.equity_curve = [initial_capital]
        self.daily_returns = []
        
        current_capital = initial_capital
        active_trades = []
        
        # Get date range
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        
        # Generate trading days
        current_date = start_dt
        trading_days = []
        
        while current_date <= end_dt:
            # Skip weekends (Saturday=5, Sunday=6)
            if current_date.weekday() < 5:
                trading_days.append(current_date)
            current_date += timedelta(days=1)
        
        logger.info(f"Analyzing {len(trading_days)} trading days")
        
        # Daily backtesting loop
        for day_idx, trading_day in enumerate(trading_days):
            if day_idx % 50 == 0:
                logger.info(f"Processing day {day_idx + 1}/{len(trading_days)}: {trading_day.date()}")
            
            day_start_capital = current_capital
            
            # 1. Check exits for active trades
            current_capital = self._process_exits(active_trades, trading_day, current_capital)
            
            # 2. Look for new entry signals
            if len(active_trades) < self.config.max_positions:
                new_trades = self._scan_for_entries(symbols, trading_day, current_capital)
                
                for trade in new_trades:
                    if len(active_trades) < self.config.max_positions and current_capital > trade.entry_price * trade.quantity:
                        active_trades.append(trade)
                        current_capital -= trade.entry_price * trade.quantity
                        self.trades.append(trade)
            
            # 3. Update equity curve
            portfolio_value = current_capital + sum(self._get_trade_value(trade, trading_day) for trade in active_trades)
            self.equity_curve.append(portfolio_value)
            
            # 4. Calculate daily return
            if day_idx > 0:
                daily_return = (portfolio_value - self.equity_curve[-2]) / self.equity_curve[-2]
                self.daily_returns.append(daily_return)
        
        # Close any remaining trades
        final_date = trading_days[-1] if trading_days else end_dt
        for trade in active_trades:
            if trade.status == TradeStatus.OPEN:
                self._close_trade(trade, final_date, trade.entry_price, "BACKTEST_END")
        
        # Calculate final metrics
        final_capital = self.equity_curve[-1] if self.equity_curve else initial_capital
        metrics = self._calculate_metrics(initial_capital, final_capital)
        
        logger.info(f"Backtest completed: {metrics.total_trades} trades, {metrics.win_rate:.1f}% win rate")
        
        return metrics
    
    def _scan_for_entries(self, symbols: List[str], date: datetime, available_capital: float) -> List[BacktestTrade]:
        """Scan for entry signals on given date."""
        new_trades = []
        
        # Limit to top symbols to avoid overloading
        scan_symbols = symbols[:50]  # Scan top 50 each day
        
        for symbol in scan_symbols:
            try:
                # Get historical data up to this date
                end_date_str = date.strftime('%Y-%m-%d')
                start_date_str = (date - timedelta(days=200)).strftime('%Y-%m-%d')
                
                data = self.data_manager.get_stock_data(
                    symbol, 
                    start_date=start_date_str, 
                    end_date=end_date_str,
                    use_cache=True
                )
                
                if data is None or len(data) < 50:
                    continue
                
                # Ensure we have data for this specific date
                data_date = date.strftime('%Y-%m-%d')
                if data_date not in data.index.astype(str):
                    continue
                
                # Calculate indicators up to this date
                indicators = self.technical_analyzer.calculate_indicators(data)
                signals = self.technical_analyzer.generate_signals(data, indicators)
                
                if not signals:
                    continue
                
                # Check for buy signal
                overall_signal = self.technical_analyzer.get_overall_signal(signals)
                
                if overall_signal.name in ['BUY', 'STRONG_BUY']:
                    confidence = len([s for s in signals if s.signal_type.name in ['BUY', 'STRONG_BUY']]) / len(signals)
                    
                    if confidence >= 0.5:  # At least 50% confidence
                        # Get current price (use close of current day)
                        current_price = data.loc[data_date, 'close']
                        
                        # Calculate position size
                        atr = indicators.get('atr', 0)
                        if atr > 0:
                            stop_loss = current_price - (2 * atr)
                            take_profit = current_price + (3 * atr)
                            
                            # Calculate position size based on risk
                            risk_amount = available_capital * self.config.risk_per_trade
                            position_size = int(risk_amount / (current_price - stop_loss))
                            
                            if position_size > 0 and (position_size * current_price) <= available_capital * 0.2:  # Max 20% per position
                                trade = BacktestTrade(
                                    symbol=symbol,
                                    entry_date=date,
                                    entry_price=current_price,
                                    quantity=position_size,
                                    stop_loss=stop_loss,
                                    take_profit=take_profit,
                                    trailing_stop=None,  # Will be set after entry
                                    trailing_stop_pct=0.04,  # 4% trailing stop
                                    highest_price=current_price,  # Initialize with entry price
                                    status=TradeStatus.OPEN
                                )
                                new_trades.append(trade)
                                
                                # Only one trade per day to manage risk
                                break
                                
            except Exception as e:
                logger.debug(f"Error scanning {symbol} on {date}: {e}")
                continue
        
        return new_trades
    
    def _process_exits(self, active_trades: List[BacktestTrade], date: datetime, capital: float) -> float:
        """Process exits for active trades."""
        trades_to_remove = []
        
        for trade in active_trades:
            if trade.status != TradeStatus.OPEN:
                continue
            
            try:
                # Get current price data
                data = self.data_manager.get_stock_data(
                    trade.symbol,
                    start_date=trade.entry_date.strftime('%Y-%m-%d'),
                    end_date=date.strftime('%Y-%m-%d'),
                    use_cache=True
                )
                
                if data is None:
                    continue
                
                date_str = date.strftime('%Y-%m-%d')
                if date_str not in data.index.astype(str):
                    continue
                
                current_price = data.loc[date_str, 'close']
                high_price = data.loc[date_str, 'high']
                low_price = data.loc[date_str, 'low']
                
                # Update max favorable/adverse and highest price
                if trade.max_favorable is None:
                    trade.max_favorable = current_price
                    trade.max_adverse = current_price
                    trade.highest_price = current_price
                else:
                    trade.max_favorable = max(trade.max_favorable, high_price)
                    trade.max_adverse = min(trade.max_adverse, low_price)
                    trade.highest_price = max(trade.highest_price, high_price)
                
                # Update trailing stop based on highest price achieved
                if trade.highest_price > trade.entry_price:
                    # Only activate trailing stop when in profit
                    new_trailing_stop = trade.highest_price * (1 - trade.trailing_stop_pct)
                    
                    if trade.trailing_stop is None:
                        # Initialize trailing stop (but not below original stop loss)
                        trade.trailing_stop = max(trade.stop_loss, new_trailing_stop)
                    else:
                        # Update trailing stop (can only move up for long positions)
                        trade.trailing_stop = max(trade.trailing_stop, new_trailing_stop)
                
                # Check for exits (including trailing stop)
                exit_price = None
                exit_reason = None
                
                # Check trailing stop first (if active and in profit)
                if (trade.trailing_stop is not None and 
                    trade.highest_price > trade.entry_price and 
                    low_price <= trade.trailing_stop):
                    exit_price = trade.trailing_stop
                    exit_reason = "TRAILING_STOP"
                    trade.status = TradeStatus.CLOSED_PROFIT
                
                # Check original stop loss (use low of day)
                elif low_price <= trade.stop_loss:
                    exit_price = trade.stop_loss
                    exit_reason = "STOP_LOSS"
                    trade.status = TradeStatus.STOPPED_OUT
                
                # Check take profit (use high of day)
                elif high_price >= trade.take_profit:
                    exit_price = trade.take_profit
                    exit_reason = "TAKE_PROFIT"
                    trade.status = TradeStatus.CLOSED_PROFIT
                
                # Check maximum holding period (10 days for swing trades)
                elif (date - trade.entry_date).days >= 10:
                    exit_price = current_price
                    exit_reason = "MAX_DAYS"
                    trade.status = TradeStatus.CLOSED_PROFIT if current_price > trade.entry_price else TradeStatus.CLOSED_LOSS
                
                # Execute exit if triggered
                if exit_price is not None:
                    self._close_trade(trade, date, exit_price, exit_reason)
                    capital += exit_price * trade.quantity
                    trades_to_remove.append(trade)
                    
            except Exception as e:
                logger.debug(f"Error processing exit for {trade.symbol}: {e}")
                continue
        
        # Remove closed trades
        for trade in trades_to_remove:
            if trade in active_trades:
                active_trades.remove(trade)
        
        return capital
    
    def _close_trade(self, trade: BacktestTrade, exit_date: datetime, exit_price: float, exit_reason: str):
        """Close a trade and calculate P&L."""
        trade.exit_date = exit_date
        trade.exit_price = exit_price
        trade.exit_reason = exit_reason
        trade.days_held = (exit_date - trade.entry_date).days
        
        # Calculate P&L
        trade.pnl = (exit_price - trade.entry_price) * trade.quantity
        trade.pnl_pct = (exit_price - trade.entry_price) / trade.entry_price * 100
        
        # Update status if not already set
        if trade.status == TradeStatus.OPEN:
            trade.status = TradeStatus.CLOSED_PROFIT if trade.pnl > 0 else TradeStatus.CLOSED_LOSS
    
    def _get_trade_value(self, trade: BacktestTrade, date: datetime) -> float:
        """Get current value of an open trade."""
        try:
            data = self.data_manager.get_stock_data(
                trade.symbol,
                start_date=trade.entry_date.strftime('%Y-%m-%d'),
                end_date=date.strftime('%Y-%m-%d'),
                use_cache=True
            )
            
            if data is None:
                return trade.entry_price * trade.quantity
            
            date_str = date.strftime('%Y-%m-%d')
            if date_str not in data.index.astype(str):
                return trade.entry_price * trade.quantity
            
            current_price = data.loc[date_str, 'close']
            return current_price * trade.quantity
            
        except Exception:
            return trade.entry_price * trade.quantity
    
    def _calculate_metrics(self, initial_capital: float, final_capital: float) -> BacktestMetrics:
        """Calculate comprehensive performance metrics."""
        if not self.trades:
            return BacktestMetrics(
                total_trades=0, winning_trades=0, losing_trades=0, win_rate=0,
                initial_capital=initial_capital, final_capital=final_capital,
                total_return=0, total_return_pct=0, max_drawdown=0, max_drawdown_pct=0,
                avg_win=0, avg_loss=0, largest_win=0, largest_loss=0, profit_factor=0,
                sharpe_ratio=0, sortino_ratio=0, calmar_ratio=0,
                avg_days_held=0, avg_winning_days=0, avg_losing_days=0,
                consecutive_wins=0, consecutive_losses=0, recovery_factor=0, expectancy=0
            )
        
        # Basic trade statistics
        total_trades = len(self.trades)
        winning_trades = len([t for t in self.trades if t.pnl and t.pnl > 0])
        losing_trades = len([t for t in self.trades if t.pnl and t.pnl <= 0])
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        # P&L analysis
        wins = [t.pnl for t in self.trades if t.pnl and t.pnl > 0]
        losses = [t.pnl for t in self.trades if t.pnl and t.pnl <= 0]
        
        avg_win = np.mean(wins) if wins else 0
        avg_loss = abs(np.mean(losses)) if losses else 0
        largest_win = max(wins) if wins else 0
        largest_loss = abs(min(losses)) if losses else 0
        
        total_wins = sum(wins) if wins else 0
        total_losses = abs(sum(losses)) if losses else 0
        profit_factor = total_wins / total_losses if total_losses > 0 else float('inf')
        
        # Returns and drawdown
        total_return = final_capital - initial_capital
        total_return_pct = (total_return / initial_capital * 100) if initial_capital > 0 else 0
        
        # Calculate max drawdown
        peak = initial_capital
        max_dd = 0
        max_dd_pct = 0
        
        for value in self.equity_curve:
            if value > peak:
                peak = value
            drawdown = peak - value
            drawdown_pct = (drawdown / peak * 100) if peak > 0 else 0
            
            if drawdown > max_dd:
                max_dd = drawdown
                max_dd_pct = drawdown_pct
        
        # Risk metrics
        if self.daily_returns:
            daily_returns_array = np.array(self.daily_returns)
            avg_daily_return = np.mean(daily_returns_array)
            std_daily_return = np.std(daily_returns_array)
            
            # Annualized metrics
            sharpe_ratio = (avg_daily_return / std_daily_return * np.sqrt(252)) if std_daily_return > 0 else 0
            
            # Sortino ratio (using negative returns only)
            negative_returns = daily_returns_array[daily_returns_array < 0]
            downside_std = np.std(negative_returns) if len(negative_returns) > 0 else 0
            sortino_ratio = (avg_daily_return / downside_std * np.sqrt(252)) if downside_std > 0 else 0
            
            # Calmar ratio
            calmar_ratio = (total_return_pct / max_dd_pct) if max_dd_pct > 0 else 0
        else:
            sharpe_ratio = sortino_ratio = calmar_ratio = 0
        
        # Trade duration analysis
        holding_periods = [t.days_held for t in self.trades if t.days_held is not None]
        winning_periods = [t.days_held for t in self.trades if t.days_held is not None and t.pnl and t.pnl > 0]
        losing_periods = [t.days_held for t in self.trades if t.days_held is not None and t.pnl and t.pnl <= 0]
        
        avg_days_held = np.mean(holding_periods) if holding_periods else 0
        avg_winning_days = np.mean(winning_periods) if winning_periods else 0
        avg_losing_days = np.mean(losing_periods) if losing_periods else 0
        
        # Consecutive wins/losses
        consecutive_wins = consecutive_losses = 0
        current_wins = current_losses = 0
        
        for trade in self.trades:
            if trade.pnl and trade.pnl > 0:
                current_wins += 1
                current_losses = 0
                consecutive_wins = max(consecutive_wins, current_wins)
            elif trade.pnl and trade.pnl <= 0:
                current_losses += 1
                current_wins = 0
                consecutive_losses = max(consecutive_losses, current_losses)
        
        # Advanced metrics
        recovery_factor = total_return / max_dd if max_dd > 0 else float('inf')
        expectancy = (win_rate / 100 * avg_win) - ((100 - win_rate) / 100 * avg_loss)
        
        return BacktestMetrics(
            total_trades=total_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            win_rate=win_rate,
            initial_capital=initial_capital,
            final_capital=final_capital,
            total_return=total_return,
            total_return_pct=total_return_pct,
            max_drawdown=max_dd,
            max_drawdown_pct=max_dd_pct,
            avg_win=avg_win,
            avg_loss=avg_loss,
            largest_win=largest_win,
            largest_loss=largest_loss,
            profit_factor=profit_factor,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            calmar_ratio=calmar_ratio,
            avg_days_held=avg_days_held,
            avg_winning_days=avg_winning_days,
            avg_losing_days=avg_losing_days,
            consecutive_wins=consecutive_wins,
            consecutive_losses=consecutive_losses,
            recovery_factor=recovery_factor,
            expectancy=expectancy
        )
    
    def get_trade_history(self) -> pd.DataFrame:
        """Get detailed trade history as DataFrame."""
        if not self.trades:
            return pd.DataFrame()
        
        trade_data = []
        for trade in self.trades:
            trade_data.append({
                'Symbol': trade.symbol,
                'Entry Date': trade.entry_date.strftime('%Y-%m-%d') if trade.entry_date else None,
                'Entry Price': trade.entry_price,
                'Quantity': trade.quantity,
                'Stop Loss': trade.stop_loss,
                'Take Profit': trade.take_profit,
                'Trailing Stop': trade.trailing_stop,
                'Highest Price': trade.highest_price,
                'Exit Date': trade.exit_date.strftime('%Y-%m-%d') if trade.exit_date else None,
                'Exit Price': trade.exit_price,
                'Exit Reason': trade.exit_reason,
                'Days Held': trade.days_held,
                'P&L (₹)': trade.pnl,
                'P&L (%)': trade.pnl_pct,
                'Status': trade.status.value,
                'Max Favorable': trade.max_favorable,
                'Max Adverse': trade.max_adverse
            })
        
        return pd.DataFrame(trade_data)
    
    def get_equity_curve(self) -> pd.DataFrame:
        """Get equity curve as DataFrame."""
        if not self.equity_curve:
            return pd.DataFrame()
        
        return pd.DataFrame({
            'Day': range(len(self.equity_curve)),
            'Portfolio Value': self.equity_curve,
            'Cumulative Return (%)': [(v / self.equity_curve[0] - 1) * 100 for v in self.equity_curve]
        })
