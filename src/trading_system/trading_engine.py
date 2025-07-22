"""
Trading Engine
==============

Main trading engine that orchestrates all components for swing trading.
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import asyncio
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
import time

from .config import TradingConfig
from .data_manager import DataManager, StockData
from .technical_analysis import TechnicalAnalyzer, TechnicalAnalysisResult, SignalType
from .risk_manager import RiskManager, PositionType, Position
from .ai_analyzer import AIAnalyzer, AIAnalysisResult
from .portfolio_manager import PortfolioManager

logger = logging.getLogger(__name__)


class TradingEngine:
    """Main trading engine for swing trading system."""
    
    def __init__(self, config: TradingConfig):
        self.config = config
        
        # Initialize components
        self.data_manager = DataManager(config)
        self.technical_analyzer = TechnicalAnalyzer(config)
        self.risk_manager = RiskManager(config)
        self.ai_analyzer = AIAnalyzer(config)
        self.portfolio_manager = PortfolioManager(config, self.data_manager)
        
        # Trading state
        self.is_running = False
        self.last_analysis_time = None
        
        # Analysis cache
        self.analysis_cache: Dict[str, TechnicalAnalysisResult] = {}
        self.ai_cache: Dict[str, AIAnalysisResult] = {}
        
        logger.info("Trading engine initialized successfully")
    
    def start_trading_session(self) -> None:
        """Start the trading session."""
        try:
            logger.info("Starting trading session...")
            self.is_running = True
            
            # Validate configuration
            self.config.validate()
            
            # Check market status
            market_status = self.data_manager.get_market_status()
            logger.info(f"Market status: {market_status['status']}")
            
            # Run initial analysis
            self.run_daily_analysis()
            
            logger.info("Trading session started successfully")
            
        except Exception as e:
            logger.error(f"Error starting trading session: {e}")
            self.is_running = False
            raise
    
    def stop_trading_session(self) -> None:
        """Stop the trading session."""
        logger.info("Stopping trading session...")
        self.is_running = False
        
        # Save any pending data
        self.portfolio_manager._save_portfolio_data()
        
        logger.info("Trading session stopped")
    
    def run_daily_analysis(self) -> Dict[str, any]:
        """Run comprehensive daily analysis for all stocks."""
        try:
            logger.info("Running daily market analysis...")
            
            # Get stock symbols
            symbols = self.config.get_indian_stock_symbols()
            
            # Analyze all stocks
            analysis_results = self.analyze_multiple_stocks(symbols)
            
            # Get AI market analysis
            market_analysis = self.ai_analyzer.get_daily_market_analysis(symbols)
            
            # Generate trade recommendations
            trade_recommendations = self.ai_analyzer.get_trade_recommendations(
                list(analysis_results.values()),
                max_recommendations=5
            )
            
            # Update portfolio with current prices
            current_prices = self._get_current_prices(symbols)
            self.portfolio_manager.update_portfolio(current_prices)
            
            # Check existing positions for stop loss/take profit
            self._check_position_exits()
            
            # Update analysis time
            self.last_analysis_time = datetime.now()
            
            return {
                'analysis_time': self.last_analysis_time,
                'total_stocks_analyzed': len(analysis_results),
                'high_confidence_signals': len([r for r in analysis_results.values() if r.confidence > 0.7]),
                'trade_recommendations': trade_recommendations,
                'market_analysis': market_analysis,
                'portfolio_summary': self.portfolio_manager.get_portfolio_summary()
            }
            
        except Exception as e:
            logger.error(f"Error in daily analysis: {e}")
            return {}
    
    def analyze_multiple_stocks(self, symbols: List[str]) -> Dict[str, TechnicalAnalysisResult]:
        """Analyze multiple stocks in parallel."""
        try:
            results = {}
            
            # Use ThreadPoolExecutor for parallel processing
            with ThreadPoolExecutor(max_workers=10) as executor:
                # Submit all analysis tasks
                future_to_symbol = {
                    executor.submit(self._analyze_single_stock, symbol): symbol 
                    for symbol in symbols
                }
                
                # Collect results
                for future in future_to_symbol:
                    symbol = future_to_symbol[future]
                    try:
                        result = future.result(timeout=30)  # 30 second timeout per stock
                        if result:
                            results[symbol] = result
                            self.analysis_cache[symbol] = result
                    except Exception as e:
                        logger.error(f"Error analyzing {symbol}: {e}")
                        continue
            
            logger.info(f"Analyzed {len(results)} stocks successfully")
            return results
            
        except Exception as e:
            logger.error(f"Error in multi-stock analysis: {e}")
            return {}
    
    def _analyze_single_stock(self, symbol: str) -> Optional[TechnicalAnalysisResult]:
        """Analyze a single stock."""
        try:
            # Get stock data
            stock_data = self.data_manager.get_stock_data(symbol)
            
            # Perform technical analysis
            analysis_result = self.technical_analyzer.analyze_stock(stock_data)
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {e}")
            return None
    
    def get_trade_recommendations(self, limit: int = 5) -> List[Dict[str, any]]:
        """Get current trade recommendations."""
        try:
            if not self.analysis_cache:
                logger.warning("No analysis cache available. Running fresh analysis...")
                symbols = self.config.get_indian_stock_symbols()[:20]  # Analyze top 20 for speed
                self.analyze_multiple_stocks(symbols)
            
            # Filter high-confidence signals
            potential_trades = []
            
            for symbol, analysis in self.analysis_cache.items():
                if analysis.confidence >= 0.6:  # Minimum confidence threshold
                    if analysis.overall_signal in [SignalType.BUY, SignalType.STRONG_BUY]:
                        # Check if we already have a position
                        if symbol not in self.portfolio_manager.positions:
                            # Calculate position size
                            current_price = analysis.key_levels.get('current_price', 0)
                            stop_loss = analysis.risk_reward.get('stop_loss', 0)
                            
                            if current_price > 0 and stop_loss > 0:
                                position_size = self.risk_manager.calculate_position_size(
                                    symbol, current_price, stop_loss
                                )
                                
                                if position_size.is_viable:
                                    potential_trades.append({
                                        'symbol': symbol,
                                        'signal': analysis.overall_signal.value,
                                        'confidence': analysis.confidence,
                                        'current_price': current_price,
                                        'stop_loss': stop_loss,
                                        'take_profit': analysis.risk_reward.get('take_profit', 0),
                                        'risk_reward_ratio': analysis.risk_reward.get('risk_reward_ratio', 0),
                                        'position_size': position_size.recommended_quantity,
                                        'position_value': position_size.position_value,
                                        'risk_amount': position_size.risk_amount,
                                        'analysis': analysis
                                    })
            
            # Sort by confidence and risk/reward
            potential_trades.sort(
                key=lambda x: (x['confidence'] * x['risk_reward_ratio']), 
                reverse=True
            )
            
            return potential_trades[:limit]
            
        except Exception as e:
            logger.error(f"Error getting trade recommendations: {e}")
            return []
    
    def execute_trade(self, symbol: str, trade_type: str = "BUY") -> bool:
        """Execute a trade based on current analysis."""
        try:
            if symbol not in self.analysis_cache:
                logger.error(f"No analysis available for {symbol}")
                return False
            
            analysis = self.analysis_cache[symbol]
            current_price = analysis.key_levels.get('current_price', 0)
            stop_loss = analysis.risk_reward.get('stop_loss', 0)
            take_profit = analysis.risk_reward.get('take_profit', 0)
            
            if current_price <= 0 or stop_loss <= 0:
                logger.error(f"Invalid price levels for {symbol}")
                return False
            
            # Calculate position size
            position_size = self.risk_manager.calculate_position_size(
                symbol, current_price, stop_loss
            )
            
            if not position_size.is_viable:
                logger.error(f"Position not viable for {symbol}: {position_size.message}")
                return False
            
            # Create position
            position = Position(
                symbol=symbol,
                position_type=PositionType.LONG if trade_type == "BUY" else PositionType.SHORT,
                entry_price=current_price,
                quantity=position_size.recommended_quantity,
                entry_date=datetime.now(),
                stop_loss=stop_loss,
                take_profit=take_profit
            )
            
            # Add to portfolio
            success = self.portfolio_manager.add_position(position)
            
            if success:
                logger.info(f"Trade executed: {symbol} {trade_type} {position.quantity} @ ₹{current_price}")
                return True
            else:
                logger.error(f"Failed to add position for {symbol}")
                return False
            
        except Exception as e:
            logger.error(f"Error executing trade for {symbol}: {e}")
            return False
    
    def _check_position_exits(self) -> None:
        """Check all positions for stop loss and take profit triggers."""
        try:
            positions_to_close = []
            
            for symbol, position in self.portfolio_manager.positions.items():
                try:
                    # Get current price
                    stock_data = self.data_manager.get_stock_data(symbol, period="2d")
                    current_price = stock_data.data['Close'].iloc[-1]
                    
                    # Update trailing stop
                    self.risk_manager.update_trailing_stop(symbol, current_price)
                    
                    # Check for exit conditions
                    exit_reason = self.risk_manager.check_stop_loss_take_profit(symbol, current_price)
                    
                    if exit_reason:
                        positions_to_close.append((symbol, current_price, exit_reason))
                        
                except Exception as e:
                    logger.error(f"Error checking position {symbol}: {e}")
                    continue
            
            # Close positions that hit stop loss or take profit
            for symbol, exit_price, reason in positions_to_close:
                self.portfolio_manager.close_position(symbol, exit_price, reason)
                logger.info(f"Position closed: {symbol} @ ₹{exit_price} ({reason})")
                
        except Exception as e:
            logger.error(f"Error checking position exits: {e}")
    
    def _get_current_prices(self, symbols: List[str]) -> Dict[str, float]:
        """Get current prices for symbols."""
        prices = {}
        
        for symbol in symbols:
            try:
                if symbol in self.analysis_cache:
                    prices[symbol] = self.analysis_cache[symbol].key_levels.get('current_price', 0)
                else:
                    # Fetch fresh data if not in cache
                    stock_data = self.data_manager.get_stock_data(symbol, period="1d")
                    prices[symbol] = stock_data.data['Close'].iloc[-1]
            except Exception as e:
                logger.error(f"Error getting price for {symbol}: {e}")
                continue
        
        return prices
    
    def get_market_summary(self) -> str:
        """Get comprehensive market summary."""
        try:
            summary = f"Swing Trading System - Market Summary\n"
            summary += f"{'='*60}\n"
            summary += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            
            # Market status
            market_status = self.data_manager.get_market_status()
            summary += f"Market Status: {market_status['status']}\n"
            
            if market_status['status'] == 'OPEN':
                summary += f"Session ends: {market_status['session_end'].strftime('%H:%M')}\n"
            elif market_status['status'] == 'CLOSED' and 'next_open' in market_status:
                summary += f"Next session: {market_status['next_open'].strftime('%Y-%m-%d %H:%M')}\n"
            
            summary += f"\n"
            
            # Portfolio summary
            portfolio_summary = self.portfolio_manager.get_portfolio_summary()
            summary += f"Portfolio Overview:\n"
            summary += f"{'-'*30}\n"
            summary += f"Portfolio Value: ₹{portfolio_summary.get('portfolio_value', 0):,.2f}\n"
            summary += f"Total Return: {portfolio_summary.get('total_return_pct', 0):.2f}%\n"
            summary += f"Active Positions: {portfolio_summary.get('positions_count', 0)}\n"
            summary += f"Cash: {portfolio_summary.get('cash_pct', 0):.1f}%\n\n"
            
            # Recent analysis
            if self.last_analysis_time:
                summary += f"Last Analysis: {self.last_analysis_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                summary += f"Stocks Analyzed: {len(self.analysis_cache)}\n"
                
                # High confidence signals
                high_conf_signals = [
                    symbol for symbol, analysis in self.analysis_cache.items()
                    if analysis.confidence > 0.7
                ]
                summary += f"High Confidence Signals: {len(high_conf_signals)}\n\n"
            
            # Trade recommendations
            recommendations = self.get_trade_recommendations(3)
            if recommendations:
                summary += f"Top Trade Recommendations:\n"
                summary += f"{'-'*30}\n"
                for i, rec in enumerate(recommendations, 1):
                    summary += f"{i}. {rec['symbol']}: {rec['signal']} "
                    summary += f"(Conf: {rec['confidence']:.2f}, R:R: 1:{rec['risk_reward_ratio']:.2f})\n"
                    summary += f"   Entry: ₹{rec['current_price']:.2f}, Stop: ₹{rec['stop_loss']:.2f}\n"
            else:
                summary += f"No trade recommendations at this time.\n"
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating market summary: {e}")
            return "Error generating market summary"
    
    def get_system_status(self) -> Dict[str, any]:
        """Get system status and health check."""
        try:
            return {
                'is_running': self.is_running,
                'last_analysis': self.last_analysis_time,
                'analysis_cache_size': len(self.analysis_cache),
                'market_status': self.data_manager.get_market_status(),
                'portfolio_positions': len(self.portfolio_manager.positions),
                'data_cache_size': len(self.data_manager.cache),
                'config_valid': self.config.validate() if hasattr(self.config, 'validate') else True
            }
            
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {'error': str(e)}
    
    def cleanup(self) -> None:
        """Cleanup resources and save state."""
        try:
            logger.info("Cleaning up trading engine...")
            
            # Stop trading session
            self.stop_trading_session()
            
            # Clear caches
            self.analysis_cache.clear()
            self.ai_cache.clear()
            self.data_manager.clear_cache()
            
            logger.info("Trading engine cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
