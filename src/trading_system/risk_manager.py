"""
Risk Management System
======================

Comprehensive risk management for swing trading with position sizing,
stop losses, take profits, and portfolio risk control.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, NamedTuple
from dataclasses import dataclass
from enum import Enum
import logging
from datetime import datetime

from .config import TradingConfig
from .technical_analysis import TechnicalAnalysisResult

logger = logging.getLogger(__name__)


class PositionType(Enum):
    """Position types."""
    LONG = "LONG"
    SHORT = "SHORT"


class OrderType(Enum):
    """Order types."""
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP_LOSS = "STOP_LOSS"
    TAKE_PROFIT = "TAKE_PROFIT"
    TRAILING_STOP = "TRAILING_STOP"


@dataclass
class Position:
    """Trading position data."""
    symbol: str
    position_type: PositionType
    entry_price: float
    quantity: int
    entry_date: datetime
    stop_loss: float
    take_profit: float
    trailing_stop: Optional[float] = None
    current_price: float = 0.0
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0
    
    def update_price(self, current_price: float) -> None:
        """Update current price and calculate unrealized P&L."""
        self.current_price = current_price
        
        if self.position_type == PositionType.LONG:
            self.unrealized_pnl = (current_price - self.entry_price) * self.quantity
        else:
            self.unrealized_pnl = (self.entry_price - current_price) * self.quantity
    
    def get_position_value(self) -> float:
        """Get current position value."""
        return self.current_price * self.quantity
    
    def get_return_percentage(self) -> float:
        """Get return percentage."""
        if self.position_type == PositionType.LONG:
            return ((self.current_price - self.entry_price) / self.entry_price) * 100
        else:
            return ((self.entry_price - self.current_price) / self.entry_price) * 100


@dataclass
class RiskMetrics:
    """Portfolio risk metrics."""
    total_capital: float
    used_capital: float
    available_capital: float
    total_positions: int
    portfolio_value: float
    total_unrealized_pnl: float
    portfolio_risk_percentage: float
    max_position_risk: float
    sharpe_ratio: Optional[float] = None
    max_drawdown: float = 0.0
    win_rate: float = 0.0
    avg_win_loss_ratio: float = 0.0


@dataclass
class PositionSizeResult:
    """Position sizing calculation result."""
    recommended_quantity: int
    position_value: float
    risk_amount: float
    risk_percentage: float
    max_loss_amount: float
    is_viable: bool
    message: str


class RiskManager:
    """Advanced risk management system."""
    
    def __init__(self, config: TradingConfig):
        self.config = config
        self.positions: Dict[str, Position] = {}
        self.trade_history: List[Dict] = []
        self.capital = config.capital
        self.max_positions = config.risk.max_positions
        
    def calculate_position_size(self, 
                              symbol: str,
                              entry_price: float,
                              stop_loss: float,
                              position_type: PositionType = PositionType.LONG) -> PositionSizeResult:
        """
        Calculate optimal position size based on risk management rules.
        
        Args:
            symbol: Stock symbol
            entry_price: Entry price
            stop_loss: Stop loss price
            position_type: Long or short position
        
        Returns:
            PositionSizeResult with sizing recommendations
        """
        try:
            # Calculate risk per share
            if position_type == PositionType.LONG:
                risk_per_share = entry_price - stop_loss
            else:
                risk_per_share = stop_loss - entry_price
            
            if risk_per_share <= 0:
                return PositionSizeResult(
                    recommended_quantity=0,
                    position_value=0,
                    risk_amount=0,
                    risk_percentage=0,
                    max_loss_amount=0,
                    is_viable=False,
                    message="Invalid stop loss: Stop loss must create positive risk"
                )
            
            # Calculate risk percentage
            risk_percentage = (risk_per_share / entry_price) * 100
            
            # Check if risk percentage is acceptable
            max_risk_pct = self.config.risk.stop_loss_pct * 100
            if risk_percentage > max_risk_pct:
                return PositionSizeResult(
                    recommended_quantity=0,
                    position_value=0,
                    risk_amount=0,
                    risk_percentage=risk_percentage,
                    max_loss_amount=0,
                    is_viable=False,
                    message=f"Risk too high: {risk_percentage:.2f}% > {max_risk_pct:.2f}%"
                )
            
            # Calculate available capital
            available_capital = self._get_available_capital()
            
            # Calculate maximum risk amount
            max_risk_amount = available_capital * self.config.risk.risk_per_trade
            
            # Calculate quantity based on risk
            quantity = int(max_risk_amount / risk_per_share)
            
            # Check minimum position size
            min_position_value = 10000  # Minimum ₹10,000 position
            if quantity * entry_price < min_position_value:
                quantity = int(min_position_value / entry_price)
            
            position_value = quantity * entry_price
            
            # Check if position fits within available capital
            if position_value > available_capital * 0.8:  # Max 80% of available capital
                quantity = int((available_capital * 0.8) / entry_price)
                position_value = quantity * entry_price
            
            # Check maximum positions limit
            if len(self.positions) >= self.max_positions:
                return PositionSizeResult(
                    recommended_quantity=0,
                    position_value=0,
                    risk_amount=0,
                    risk_percentage=risk_percentage,
                    max_loss_amount=0,
                    is_viable=False,
                    message=f"Maximum positions limit reached: {self.max_positions}"
                )
            
            actual_risk_amount = quantity * risk_per_share
            actual_risk_percentage = (actual_risk_amount / available_capital) * 100
            
            is_viable = (
                quantity > 0 and
                position_value >= min_position_value and
                actual_risk_percentage <= self.config.risk.risk_per_trade * 100
            )
            
            message = "Position size calculated successfully"
            if not is_viable:
                message = "Position not viable with current risk parameters"
            
            return PositionSizeResult(
                recommended_quantity=quantity,
                position_value=position_value,
                risk_amount=actual_risk_amount,
                risk_percentage=actual_risk_percentage,
                max_loss_amount=actual_risk_amount,
                is_viable=is_viable,
                message=message
            )
            
        except Exception as e:
            logger.error(f"Error calculating position size for {symbol}: {e}")
            return PositionSizeResult(
                recommended_quantity=0,
                position_value=0,
                risk_amount=0,
                risk_percentage=0,
                max_loss_amount=0,
                is_viable=False,
                message=f"Error: {str(e)}"
            )
    
    def add_position(self, 
                    symbol: str,
                    position_type: PositionType,
                    entry_price: float,
                    quantity: int,
                    stop_loss: float,
                    take_profit: float) -> bool:
        """Add a new position to the portfolio."""
        try:
            if symbol in self.positions:
                logger.warning(f"Position for {symbol} already exists")
                return False
            
            position = Position(
                symbol=symbol,
                position_type=position_type,
                entry_price=entry_price,
                quantity=quantity,
                entry_date=datetime.now(),
                stop_loss=stop_loss,
                take_profit=take_profit,
                current_price=entry_price
            )
            
            self.positions[symbol] = position
            
            # Log trade
            self.trade_history.append({
                'action': 'OPEN',
                'symbol': symbol,
                'type': position_type.value,
                'price': entry_price,
                'quantity': quantity,
                'timestamp': datetime.now(),
                'stop_loss': stop_loss,
                'take_profit': take_profit
            })
            
            logger.info(f"Added position: {symbol} {position_type.value} {quantity} @ ₹{entry_price}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding position for {symbol}: {e}")
            return False
    
    def close_position(self, symbol: str, exit_price: float, reason: str = "Manual") -> bool:
        """Close a position and realize P&L."""
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
            
            # Log trade
            self.trade_history.append({
                'action': 'CLOSE',
                'symbol': symbol,
                'type': position.position_type.value,
                'entry_price': position.entry_price,
                'exit_price': exit_price,
                'quantity': position.quantity,
                'pnl': realized_pnl,
                'reason': reason,
                'timestamp': datetime.now(),
                'hold_days': (datetime.now() - position.entry_date).days
            })
            
            # Remove position
            del self.positions[symbol]
            
            logger.info(f"Closed position: {symbol} @ ₹{exit_price}, P&L: ₹{realized_pnl:.2f}")
            return True
            
        except Exception as e:
            logger.error(f"Error closing position for {symbol}: {e}")
            return False
    
    def update_trailing_stop(self, symbol: str, current_price: float) -> Optional[float]:
        """Update trailing stop for a position."""
        try:
            if symbol not in self.positions:
                return None
            
            position = self.positions[symbol]
            
            if position.position_type == PositionType.LONG:
                # For long positions, trailing stop moves up
                trailing_stop_price = current_price * (1 - self.config.risk.trailing_stop_pct)
                
                if position.trailing_stop is None:
                    position.trailing_stop = max(position.stop_loss, trailing_stop_price)
                else:
                    position.trailing_stop = max(position.trailing_stop, trailing_stop_price)
            else:
                # For short positions, trailing stop moves down
                trailing_stop_price = current_price * (1 + self.config.risk.trailing_stop_pct)
                
                if position.trailing_stop is None:
                    position.trailing_stop = min(position.stop_loss, trailing_stop_price)
                else:
                    position.trailing_stop = min(position.trailing_stop, trailing_stop_price)
            
            return position.trailing_stop
            
        except Exception as e:
            logger.error(f"Error updating trailing stop for {symbol}: {e}")
            return None
    
    def check_stop_loss_take_profit(self, symbol: str, current_price: float) -> Optional[str]:
        """Check if stop loss or take profit should be triggered."""
        try:
            if symbol not in self.positions:
                return None
            
            position = self.positions[symbol]
            position.update_price(current_price)
            
            if position.position_type == PositionType.LONG:
                # Check stop loss (including trailing stop)
                stop_price = position.trailing_stop if position.trailing_stop else position.stop_loss
                if current_price <= stop_price:
                    return "STOP_LOSS"
                
                # Check take profit
                if current_price >= position.take_profit:
                    return "TAKE_PROFIT"
            else:
                # For short positions
                stop_price = position.trailing_stop if position.trailing_stop else position.stop_loss
                if current_price >= stop_price:
                    return "STOP_LOSS"
                
                if current_price <= position.take_profit:
                    return "TAKE_PROFIT"
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking stop/profit for {symbol}: {e}")
            return None
    
    def get_portfolio_risk_metrics(self) -> RiskMetrics:
        """Calculate comprehensive portfolio risk metrics."""
        try:
            total_capital = self.capital
            used_capital = sum(pos.get_position_value() for pos in self.positions.values())
            available_capital = total_capital - used_capital
            
            total_unrealized_pnl = sum(pos.unrealized_pnl for pos in self.positions.values())
            portfolio_value = total_capital + total_unrealized_pnl
            
            # Calculate portfolio risk percentage
            total_risk = 0
            for position in self.positions.values():
                if position.position_type == PositionType.LONG:
                    risk_per_share = position.entry_price - position.stop_loss
                else:
                    risk_per_share = position.stop_loss - position.entry_price
                total_risk += risk_per_share * position.quantity
            
            portfolio_risk_percentage = (total_risk / total_capital) * 100
            
            # Calculate max position risk
            max_position_risk = 0
            if self.positions:
                position_risks = []
                for position in self.positions.values():
                    if position.position_type == PositionType.LONG:
                        risk = position.entry_price - position.stop_loss
                    else:
                        risk = position.stop_loss - position.entry_price
                    position_risks.append((risk * position.quantity / total_capital) * 100)
                max_position_risk = max(position_risks) if position_risks else 0
            
            # Calculate performance metrics from trade history
            win_rate, avg_win_loss_ratio, max_drawdown = self._calculate_performance_metrics()
            
            return RiskMetrics(
                total_capital=total_capital,
                used_capital=used_capital,
                available_capital=available_capital,
                total_positions=len(self.positions),
                portfolio_value=portfolio_value,
                total_unrealized_pnl=total_unrealized_pnl,
                portfolio_risk_percentage=portfolio_risk_percentage,
                max_position_risk=max_position_risk,
                max_drawdown=max_drawdown,
                win_rate=win_rate,
                avg_win_loss_ratio=avg_win_loss_ratio
            )
            
        except Exception as e:
            logger.error(f"Error calculating risk metrics: {e}")
            return RiskMetrics(
                total_capital=self.capital,
                used_capital=0,
                available_capital=self.capital,
                total_positions=0,
                portfolio_value=self.capital,
                total_unrealized_pnl=0,
                portfolio_risk_percentage=0,
                max_position_risk=0
            )
    
    def _get_available_capital(self) -> float:
        """Calculate available capital for new positions."""
        used_capital = sum(pos.get_position_value() for pos in self.positions.values())
        return self.capital - used_capital
    
    def _calculate_performance_metrics(self) -> Tuple[float, float, float]:
        """Calculate performance metrics from trade history."""
        try:
            closed_trades = [trade for trade in self.trade_history if trade['action'] == 'CLOSE']
            
            if not closed_trades:
                return 0.0, 0.0, 0.0
            
            # Win rate
            winning_trades = [trade for trade in closed_trades if trade['pnl'] > 0]
            win_rate = len(winning_trades) / len(closed_trades) * 100
            
            # Average win/loss ratio
            wins = [trade['pnl'] for trade in winning_trades]
            losses = [abs(trade['pnl']) for trade in closed_trades if trade['pnl'] < 0]
            
            avg_win = np.mean(wins) if wins else 0
            avg_loss = np.mean(losses) if losses else 1
            avg_win_loss_ratio = avg_win / avg_loss if avg_loss > 0 else 0
            
            # Max drawdown (simplified)
            portfolio_values = []
            running_pnl = 0
            for trade in closed_trades:
                running_pnl += trade['pnl']
                portfolio_values.append(self.capital + running_pnl)
            
            if portfolio_values:
                peak = self.capital
                max_drawdown = 0
                for value in portfolio_values:
                    if value > peak:
                        peak = value
                    drawdown = (peak - value) / peak * 100
                    max_drawdown = max(max_drawdown, drawdown)
            else:
                max_drawdown = 0
            
            return win_rate, avg_win_loss_ratio, max_drawdown
            
        except Exception as e:
            logger.error(f"Error calculating performance metrics: {e}")
            return 0.0, 0.0, 0.0
    
    def get_position_summary(self) -> str:
        """Get a summary of all current positions."""
        if not self.positions:
            return "No open positions"
        
        summary = f"Current Positions ({len(self.positions)}):\n"
        summary += f"{'Symbol':<12} {'Type':<6} {'Qty':<8} {'Entry':<10} {'Current':<10} {'P&L':<10} {'P&L%':<8}\n"
        summary += f"{'-'*70}\n"
        
        for position in self.positions.values():
            pnl_pct = position.get_return_percentage()
            summary += f"{position.symbol:<12} {position.position_type.value:<6} {position.quantity:<8} "
            summary += f"₹{position.entry_price:<9.2f} ₹{position.current_price:<9.2f} "
            summary += f"₹{position.unrealized_pnl:<9.2f} {pnl_pct:<7.2f}%\n"
        
        return summary
    
    def get_risk_summary(self) -> str:
        """Get a summary of risk metrics."""
        metrics = self.get_portfolio_risk_metrics()
        
        summary = f"Risk Management Summary:\n"
        summary += f"{'='*50}\n"
        summary += f"Total Capital: ₹{metrics.total_capital:,.2f}\n"
        summary += f"Used Capital: ₹{metrics.used_capital:,.2f}\n"
        summary += f"Available Capital: ₹{metrics.available_capital:,.2f}\n"
        summary += f"Portfolio Value: ₹{metrics.portfolio_value:,.2f}\n"
        summary += f"Unrealized P&L: ₹{metrics.total_unrealized_pnl:,.2f}\n"
        summary += f"Portfolio Risk: {metrics.portfolio_risk_percentage:.2f}%\n"
        summary += f"Max Position Risk: {metrics.max_position_risk:.2f}%\n"
        summary += f"Active Positions: {metrics.total_positions}/{self.max_positions}\n"
        
        if metrics.win_rate > 0:
            summary += f"\nPerformance Metrics:\n"
            summary += f"Win Rate: {metrics.win_rate:.1f}%\n"
            summary += f"Avg Win/Loss Ratio: {metrics.avg_win_loss_ratio:.2f}\n"
            summary += f"Max Drawdown: {metrics.max_drawdown:.2f}%\n"
        
        return summary
