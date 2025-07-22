#!/usr/bin/env python3
"""
Comprehensive Backtesting System - A+ Grade Stock Picks
Detailed win/loss analysis with realistic trading results
"""

import pandas as pd
import yfinance as yf
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

class ComprehensiveBacktester:
    """Advanced backtesting system for A+ grade stock picks"""
    
    def __init__(self):
        """Initialize backtesting parameters for A+ Grade Performance"""
        # Enhanced A+ Grade Trading Parameters for 10        print(f"🛡️ Risk Management: 4% SL | 25% TP | 2.5% Trailing | 2.5% Risk/Trade")+ Monthly Returns
        self.stop_loss_pct = 0.04  # 4% tight stop loss for better R:R
        self.take_profit_pct = 0.25  # 25% aggressive take profit
        self.trailing_stop_pct = 0.025  # 2.5% tighter trailing stop
        self.risk_per_trade = 0.025  # 2.5% risk per trade for higher returns
        self.min_signal_strength = 85  # 85% minimum strength for A+ grade
        
        # Enhanced signal criteria
        self.min_rsi_oversold = 20  # More extreme oversold
        self.min_volume_multiplier = 2.0  # Higher volume requirement
        self.min_score_threshold = 5  # Higher score threshold
        
        # Current A+ picks from today's scan
        self.current_aplus_picks = [
            'RELIANCE.NS', 'RPOWER.NS', 'AUBANK.NS', 'INDIACEM.NS', 'MOIL.NS',
            'NOCIL.NS', 'CLEAN.NS', 'GLAXO.NS', 'EICHERMOT.NS', 'GTLINFRA.NS',
            'SANDHAR.NS', 'TATACHEM.NS', 'JSWSTEEL.NS', 'SHREECEM.NS', 'NATIONALUM.NS',
            'JUBLFOOD.NS', 'BHARTIARTL.NS', 'DMART.NS', 'DLF.NS', 'SUNTECK.NS'
        ]
        
    def analyze_stock_historical_signals(self, symbol: str, analysis_date: datetime) -> Optional[Dict]:
        """Analyze if stock would have generated A+ signal on given date"""
        try:
            # Get data for analysis
            end_date = analysis_date + timedelta(days=1)
            start_date = analysis_date - timedelta(days=180)
            
            ticker = yf.Ticker(symbol)
            data = ticker.history(start=start_date, end=end_date, interval="1d")
            
            if data.empty or len(data) < 30:
                return None
            
            # Find analysis date in data
            analysis_idx = None
            for i, date in enumerate(data.index):
                if date.date() == analysis_date.date():
                    analysis_idx = i
                    break
            
            if analysis_idx is None or analysis_idx < 25:
                return None
            
            # Use data up to analysis date
            analysis_data = data.iloc[:analysis_idx + 1]
            
            # Calculate indicators
            indicators = self.calculate_indicators(analysis_data)
            if not indicators:
                return None
            
            current_price = analysis_data['Close'].iloc[-1]
            current_volume = analysis_data['Volume'].iloc[-1]
            
            # Enhanced A+ Signal generation logic for 10%+ monthly returns
            signals = []
            score = 0
            
            # Enhanced RSI Analysis - More selective
            rsi = indicators['rsi'].iloc[-1] if 'rsi' in indicators else 50
            if rsi <= self.min_rsi_oversold:  # Extreme oversold (20 or below)
                signals.append("RSI Extreme Oversold")
                score += 4  # Higher score for extreme conditions
            elif 20 < rsi <= 30:
                signals.append("RSI Deep Oversold")
                score += 3
            elif rsi >= 80:
                signals.append("RSI Extreme Overbought")
                score -= 4  # Penalize overbought more
            
            # Enhanced MACD Analysis
            if 'macd' in indicators and 'macd_signal' in indicators:
                macd = indicators['macd'].iloc[-1]
                macd_signal = indicators['macd_signal'].iloc[-1]
                if len(indicators['macd']) > 1:
                    macd_prev = indicators['macd'].iloc[-2]
                    macd_signal_prev = indicators['macd_signal'].iloc[-2]
                    
                    # Fresh bullish crossover
                    if macd > macd_signal and macd_prev <= macd_signal_prev:
                        signals.append("MACD Fresh Bull Crossover")
                        score += 4  # Higher score for fresh signals
                    
                    # Momentum acceleration
                    if macd > macd_signal and macd > macd_prev:
                        signals.append("MACD Momentum Acceleration")
                        score += 2
            
            # Enhanced Moving Average Analysis - Perfect Stack
            if 'sma_20' in indicators and 'sma_50' in indicators:
                sma_20 = indicators['sma_20'].iloc[-1]
                sma_50 = indicators['sma_50'].iloc[-1]
                
                # Perfect bullish alignment
                if current_price > sma_20 > sma_50:
                    price_above_20 = (current_price - sma_20) / sma_20 * 100
                    if price_above_20 >= 2:  # At least 2% above MA20
                        signals.append("Strong MA Breakout")
                        score += 3
                    else:
                        signals.append("Perfect MA Alignment")
                        score += 2
            
            # Enhanced Volume Analysis - Higher threshold
            if 'volume_ma' in indicators:
                volume_ma = indicators['volume_ma'].iloc[-1]
                volume_ratio = current_volume / volume_ma if volume_ma > 0 else 1
                if volume_ratio >= 3.0:
                    signals.append(f"Explosive Volume ({volume_ratio:.1f}x)")
                    score += 4
                elif volume_ratio >= self.min_volume_multiplier:
                    signals.append(f"High Volume ({volume_ratio:.1f}x)")
                    score += 2
            
            # Enhanced Bollinger Bands - Squeeze & Breakout
            if 'bb_upper' in indicators and 'bb_lower' in indicators:
                bb_upper = indicators['bb_upper'].iloc[-1]
                bb_lower = indicators['bb_lower'].iloc[-1]
                bb_width = (bb_upper - bb_lower) / current_price * 100
                bb_position = (current_price - bb_lower) / (bb_upper - bb_lower)
                
                # Bollinger squeeze breakout
                if bb_width < 15 and bb_position > 0.8:  # Tight bands + upper breakout
                    signals.append("BB Squeeze Breakout")
                    score += 3
                elif bb_position <= 0.05:  # Extreme oversold
                    signals.append("BB Extreme Oversold")
                    score += 3
                elif bb_position >= 0.95:  # Extreme overbought
                    signals.append("BB Extreme Overbought")
                    score -= 3
            
            # Additional momentum indicators
            if 'sma_20' in indicators and len(indicators['sma_20']) > 5:
                # Price momentum
                price_5d_ago = analysis_data['Close'].iloc[-6] if len(analysis_data) > 5 else current_price
                momentum_5d = (current_price - price_5d_ago) / price_5d_ago * 100
                
                if momentum_5d > 5:  # Strong 5-day momentum
                    signals.append("Strong Momentum")
                    score += 2
                elif momentum_5d < -10:  # Deep pullback
                    signals.append("Deep Pullback Opportunity")
                    score += 1
            
            # Calculate enhanced strength
            strength = min(100, max(0, int((score + 6) / 12 * 100)))
            
            # Enhanced A+ criteria - More selective
            if strength >= self.min_signal_strength and score >= self.min_score_threshold:
                if score >= 8:
                    direction = "STRONG BUY"
                elif score >= 6:
                    direction = "BUY"
                else:
                    direction = "WEAK BUY"
                
                return {
                    'symbol': symbol,
                    'analysis_date': analysis_date,
                    'entry_price': current_price,
                    'direction': direction,
                    'strength': strength,
                    'signals': signals,
                    'score': score,
                    'rsi': rsi
                }
            
            return None
            
        except Exception as e:
            return None
    
    def calculate_indicators(self, data: pd.DataFrame) -> Dict:
        """Calculate technical indicators"""
        if len(data) < 26:
            return {}
        
        # Enhanced indicators calculation
        indicators = {}
        
        try:
            # Enhanced RSI with smoothing
            delta = data['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            indicators['rsi'] = 100 - (100 / (1 + rs))
            
            # Multiple timeframe moving averages
            indicators['sma_10'] = data['Close'].rolling(10).mean()
            indicators['sma_20'] = data['Close'].rolling(20).mean()
            indicators['sma_50'] = data['Close'].rolling(50).mean()
            indicators['ema_9'] = data['Close'].ewm(span=9).mean()
            indicators['ema_12'] = data['Close'].ewm(span=12).mean()
            indicators['ema_26'] = data['Close'].ewm(span=26).mean()
            
            # Enhanced MACD with histogram
            indicators['macd'] = indicators['ema_12'] - indicators['ema_26']
            indicators['macd_signal'] = indicators['macd'].ewm(span=9).mean()
            indicators['macd_histogram'] = indicators['macd'] - indicators['macd_signal']
            
            # Dynamic Bollinger Bands
            sma_20 = indicators['sma_20']
            std_20 = data['Close'].rolling(20).std()
            indicators['bb_upper'] = sma_20 + (std_20 * 2)
            indicators['bb_lower'] = sma_20 - (std_20 * 2)
            indicators['bb_middle'] = sma_20
            
            # Enhanced volume indicators
            indicators['volume_ma'] = data['Volume'].rolling(20).mean()
            indicators['volume_sma_10'] = data['Volume'].rolling(10).mean()
            
            # Price momentum indicators
            indicators['momentum_5'] = data['Close'].pct_change(5) * 100
            indicators['momentum_10'] = data['Close'].pct_change(10) * 100
            
        except Exception as e:
            pass
        
        return indicators
    
    def backtest_trade(self, signal: Dict, days_forward: int = 15) -> Dict:
        """Backtest a single trade with detailed tracking"""
        try:
            symbol = signal['symbol']
            entry_date = signal['analysis_date']
            entry_price = signal['entry_price']
            
            # Calculate trade levels
            stop_loss = entry_price * (1 - self.stop_loss_pct)
            take_profit = entry_price * (1 + self.take_profit_pct)
            trailing_stop_initial = entry_price * (1 - self.trailing_stop_pct)
            
            # Get forward data
            start_date = entry_date
            end_date = entry_date + timedelta(days=days_forward + 10)
            
            ticker = yf.Ticker(symbol)
            forward_data = ticker.history(start=start_date, end=end_date, interval="1d")
            
            if forward_data.empty or len(forward_data) < 2:
                return self.create_trade_result(signal, "NO_DATA", 0, 0, "Insufficient forward data")
            
            # Track trade performance
            max_profit_pct = 0
            max_drawdown_pct = 0
            trailing_stop = trailing_stop_initial
            exit_reason = "HOLDING"
            exit_price = entry_price
            exit_date = entry_date
            trade_active = True
            
            # Day-by-day tracking
            for i in range(1, min(len(forward_data), days_forward + 1)):
                row = forward_data.iloc[i]
                date = forward_data.index[i]
                high = row['High']
                low = row['Low']
                close = row['Close']
                
                # Update max profit/drawdown
                day_high_pct = ((high / entry_price) - 1) * 100
                day_low_pct = ((low / entry_price) - 1) * 100
                close_pct = ((close / entry_price) - 1) * 100
                
                max_profit_pct = max(max_profit_pct, day_high_pct)
                max_drawdown_pct = min(max_drawdown_pct, day_low_pct)
                
                if trade_active:
                    # Check stop loss
                    if low <= stop_loss:
                        exit_reason = "STOP_LOSS"
                        exit_price = stop_loss
                        exit_date = date
                        trade_active = False
                        break
                    
                    # Check take profit
                    elif high >= take_profit:
                        exit_reason = "TAKE_PROFIT"
                        exit_price = take_profit
                        exit_date = date
                        trade_active = False
                        break
                    
                    # Update trailing stop
                    elif close > entry_price:
                        new_trailing = close * (1 - self.trailing_stop_pct)
                        if new_trailing > trailing_stop:
                            trailing_stop = new_trailing
                        
                        # Check trailing stop hit
                        if low <= trailing_stop:
                            exit_reason = "TRAILING_STOP"
                            exit_price = trailing_stop
                            exit_date = date
                            trade_active = False
                            break
            
            # If still active after tracking period
            if trade_active and len(forward_data) > 1:
                exit_reason = "TIME_EXIT"
                exit_price = forward_data.iloc[-1]['Close']
                exit_date = forward_data.index[-1]
            
            # Calculate final performance
            final_profit_pct = ((exit_price / entry_price) - 1) * 100
            trade_duration = (exit_date - entry_date).days
            
            return self.create_trade_result(
                signal, exit_reason, final_profit_pct, max_profit_pct,
                f"Exit: ₹{exit_price:.2f} after {trade_duration} days",
                [], max_drawdown_pct, exit_date, trade_duration
            )
            
        except Exception as e:
            return self.create_trade_result(signal, "ERROR", 0, 0, f"Error: {str(e)}")
    
    def create_trade_result(self, signal: Dict, exit_reason: str, profit_pct: float,
                          max_profit_pct: float, notes: str, daily_data: List = None,
                          max_drawdown_pct: float = 0, exit_date: datetime = None,
                          duration: int = 0) -> Dict:
        """Create standardized trade result"""
        return {
            'symbol': signal['symbol'],
            'entry_date': signal['analysis_date'],
            'entry_price': signal['entry_price'],
            'exit_reason': exit_reason,
            'profit_pct': profit_pct,
            'max_profit_pct': max_profit_pct,
            'max_drawdown_pct': max_drawdown_pct,
            'win': profit_pct > 0,
            'strength': signal['strength'],
            'signals': signal['signals'],
            'notes': notes,
            'exit_date': exit_date,
            'duration': duration,
            'direction': signal['direction']
        }
    
    def run_comprehensive_backtest(self, days_back: int = 60) -> Dict:
        """Run comprehensive backtest for specified period"""
        print(f"🔍 COMPREHENSIVE A+ GRADE BACKTESTING")
        print("=" * 80)
        print(f"📅 Backtest Period: Last {days_back} days")
        print(f"🎯 Testing Enhanced A+ Grade Criteria (85%+ strength)")
        print(f"🛡️ Risk Management: 4% SL | 25% TP | 2.5% Trailing")
        print("=" * 80)
        
        # Generate trading days for backtest
        end_date = datetime.now() - timedelta(days=1)
        trading_days = []
        current_date = end_date
        
        while len(trading_days) < days_back:
            if current_date.weekday() < 5:  # Weekdays only
                trading_days.append(current_date)
            current_date -= timedelta(days=1)
        
        trading_days.reverse()
        
        all_trades = []
        daily_signals = {}
        
        print(f"📊 Scanning {len(self.current_aplus_picks)} stocks across {len(trading_days)} trading days...")
        
        # Test each day
        for i, test_date in enumerate(trading_days[::5], 1):  # Test every 5th day for speed
            if i % 5 == 0:
                print(f"   📅 Testing {test_date.strftime('%Y-%m-%d')} ({i}/12)...")
            
            day_signals = []
            
            # Test subset of stocks for each day
            test_stocks = self.current_aplus_picks[:10] if i % 2 == 0 else self.current_aplus_picks[10:]
            
            for symbol in test_stocks:
                signal = self.analyze_stock_historical_signals(symbol, test_date)
                if signal:
                    day_signals.append(signal)
            
            daily_signals[test_date.strftime('%Y-%m-%d')] = day_signals
            
            # Backtest each signal
            for signal in day_signals:
                trade_result = self.backtest_trade(signal, days_forward=15)
                all_trades.append(trade_result)
        
        print(f"✅ Backtest Complete: {len(all_trades)} trades analyzed")
        
        return {
            'trades': all_trades,
            'daily_signals': daily_signals,
            'test_period': f"{trading_days[0].strftime('%Y-%m-%d')} to {trading_days[-1].strftime('%Y-%m-%d')}",
            'total_days': len(trading_days)
        }
    
    def analyze_backtest_results(self, backtest_data: Dict) -> Dict:
        """Analyze comprehensive backtest results"""
        trades = backtest_data['trades']
        
        if not trades:
            return {'error': 'No trades found'}
        
        # Overall statistics
        total_trades = len(trades)
        wins = sum(1 for t in trades if t['win'])
        losses = total_trades - wins
        win_rate = wins / total_trades * 100 if total_trades > 0 else 0
        
        profitable_trades = [t for t in trades if t['win']]
        losing_trades = [t for t in trades if not t['win']]
        
        avg_profit = np.mean([t['profit_pct'] for t in trades])
        avg_win = np.mean([t['profit_pct'] for t in profitable_trades]) if profitable_trades else 0
        avg_loss = np.mean([t['profit_pct'] for t in losing_trades]) if losing_trades else 0
        
        max_win = max([t['profit_pct'] for t in trades]) if trades else 0
        max_loss = min([t['profit_pct'] for t in trades]) if trades else 0
        
        # Exit reason analysis
        exit_reasons = {}
        for trade in trades:
            reason = trade['exit_reason']
            if reason not in exit_reasons:
                exit_reasons[reason] = {'count': 0, 'wins': 0, 'total_profit': 0}
            exit_reasons[reason]['count'] += 1
            if trade['win']:
                exit_reasons[reason]['wins'] += 1
            exit_reasons[reason]['total_profit'] += trade['profit_pct']
        
        # Monthly performance projection
        avg_daily_return = avg_profit / 15  # Average holding period
        monthly_projection = avg_daily_return * 22  # 22 trading days
        annual_projection = monthly_projection * 12
        
        return {
            'total_trades': total_trades,
            'wins': wins,
            'losses': losses,
            'win_rate': win_rate,
            'avg_profit': avg_profit,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'max_win': max_win,
            'max_loss': max_loss,
            'exit_reasons': exit_reasons,
            'profitable_trades': profitable_trades,
            'losing_trades': losing_trades,
            'monthly_projection': monthly_projection,
            'annual_projection': annual_projection
        }
    
    def display_comprehensive_results(self, backtest_data: Dict, analysis: Dict):
        """Display comprehensive backtest results"""
        if 'error' in analysis:
            print(f"\n❌ {analysis['error']}")
            return
        
        trades = backtest_data['trades']
        
        print(f"\n🏆 A+ GRADE BACKTESTING RESULTS")
        print("=" * 100)
        print(f"📊 Test Period: {backtest_data['test_period']}")
        print(f"📈 Total Trades: {analysis['total_trades']}")
        print(f"✅ Winning Trades: {analysis['wins']} ({analysis['win_rate']:.1f}%)")
        print(f"❌ Losing Trades: {analysis['losses']} ({100-analysis['win_rate']:.1f}%)")
        print(f"💰 Average Return: {analysis['avg_profit']:+.2f}%")
        print(f"🚀 Average Win: {analysis['avg_win']:+.2f}%")
        print(f"📉 Average Loss: {analysis['avg_loss']:+.2f}%")
        print(f"🎯 Best Trade: {analysis['max_win']:+.2f}%")
        print(f"💔 Worst Trade: {analysis['max_loss']:+.2f}%")
        if analysis['avg_loss'] != 0:
            print(f"📊 Risk-Reward Ratio: {abs(analysis['avg_win']/analysis['avg_loss']):.2f}:1")
        
        # Exit reason breakdown
        print(f"\n📋 EXIT STRATEGY PERFORMANCE:")
        print("-" * 80)
        print(f"{'STRATEGY':<15} {'TRADES':<8} {'WINS':<8} {'WIN%':<8} {'AVG%':<10} {'EFFECTIVENESS'}")
        print("-" * 80)
        
        for reason, stats in analysis['exit_reasons'].items():
            win_pct = stats['wins'] / stats['count'] * 100 if stats['count'] > 0 else 0
            avg_pct = stats['total_profit'] / stats['count'] if stats['count'] > 0 else 0
            
            if reason == 'TAKE_PROFIT':
                effectiveness = "🎯 EXCELLENT"
            elif reason == 'TRAILING_STOP':
                effectiveness = "✅ GOOD"
            elif reason == 'STOP_LOSS':
                effectiveness = "🛡️ PROTECTIVE"
            else:
                effectiveness = "⏰ NEUTRAL"
            
            print(f"{reason:<15} {stats['count']:<8} {stats['wins']:<8} {win_pct:<8.1f} {avg_pct:<+10.2f} {effectiveness}")
        
        # Best and worst performing trades
        sorted_trades = sorted(trades, key=lambda x: x['profit_pct'], reverse=True)
        
        print(f"\n🏅 TOP 5 WINNING TRADES:")
        print("-" * 120)
        print(f"{'SYMBOL':<12} {'DATE':<12} {'ENTRY':<10} {'PROFIT%':<10} {'MAX%':<8} {'EXIT':<15} {'DURATION':<10} {'SIGNALS'}")
        print("-" * 120)
        
        for i, trade in enumerate(sorted_trades[:5], 1):
            entry_date = trade['entry_date'].strftime('%m-%d')
            duration = f"{trade['duration']}d"
            signals = ', '.join(trade['signals'][:2])
            print(f"{trade['symbol']:<12} {entry_date:<12} ₹{trade['entry_price']:<9.0f} {trade['profit_pct']:<+10.2f} {trade['max_profit_pct']:<+8.1f} {trade['exit_reason']:<15} {duration:<10} {signals}")
        
        print(f"\n🔻 WORST 5 TRADES:")
        print("-" * 120)
        print(f"{'SYMBOL':<12} {'DATE':<12} {'ENTRY':<10} {'LOSS%':<10} {'DRAWDOWN%':<12} {'EXIT':<15} {'DURATION':<10} {'SIGNALS'}")
        print("-" * 120)
        
        for i, trade in enumerate(sorted_trades[-5:], 1):
            entry_date = trade['entry_date'].strftime('%m-%d')
            duration = f"{trade['duration']}d"
            signals = ', '.join(trade['signals'][:2])
            print(f"{trade['symbol']:<12} {entry_date:<12} ₹{trade['entry_price']:<9.0f} {trade['profit_pct']:<+10.2f} {trade['max_drawdown_pct']:<+12.2f} {trade['exit_reason']:<15} {duration:<10} {signals}")
        
        # Portfolio performance simulation
        portfolio_value = 100000
        total_return = 0
        
        for trade in trades:
            risk_amount = portfolio_value * self.risk_per_trade
            trade_return = risk_amount * (trade['profit_pct'] / 100)
            total_return += trade_return
            portfolio_value += trade_return
        
        portfolio_return_pct = (portfolio_value - 100000) / 100000 * 100
        
        print(f"\n💼 PORTFOLIO PERFORMANCE SIMULATION:")
        print("-" * 80)
        print(f"💰 Starting Capital: ₹1,00,000")
        print(f"📈 Final Portfolio Value: ₹{portfolio_value:,.0f}")
        print(f"💵 Total Return: ₹{total_return:,.0f} ({portfolio_return_pct:+.2f}%)")
        print(f"📊 Monthly Projection: {analysis['monthly_projection']:+.2f}%")
        print(f"📅 Annual Projection: {analysis['annual_projection']:+.2f}%")
        
        # System grade based on enhanced performance criteria for A+ target
        if analysis['win_rate'] >= 75 and abs(analysis['avg_win']/analysis['avg_loss']) >= 3.0:
            grade = "S+ LEGENDARY"
        elif analysis['win_rate'] >= 70 and abs(analysis['avg_win']/analysis['avg_loss']) >= 2.5:
            grade = "A+ EXCELLENT"
        elif analysis['win_rate'] >= 65 and abs(analysis['avg_win']/analysis['avg_loss']) >= 2.0:
            grade = "A GREAT"
        elif analysis['win_rate'] >= 60:
            grade = "B+ GOOD"
        else:
            grade = "B AVERAGE"
        
        print(f"\n🎖️ SYSTEM PERFORMANCE GRADE: {grade}")
        print("=" * 80)
        
        # Key insights
        print(f"🎯 KEY INSIGHTS:")
        print(f"✅ System Win Rate: {analysis['win_rate']:.1f}% ({'EXCELLENT' if analysis['win_rate'] > 65 else 'GOOD' if analysis['win_rate'] > 55 else 'AVERAGE'})")
        print(f"✅ Risk Management: {len([t for t in trades if t['exit_reason'] == 'STOP_LOSS'])} stop losses protected capital")
        print(f"✅ Profit Taking: {len([t for t in trades if t['exit_reason'] == 'TAKE_PROFIT'])} trades hit 20% targets")
        print(f"✅ Trailing Stops: {len([t for t in trades if t['exit_reason'] == 'TRAILING_STOP'])} trades secured profits")
        
        monthly_target_met = analysis['monthly_projection'] >= 7.0  # Enhanced target
        print(f"✅ Monthly Target: {analysis['monthly_projection']:+.1f}% ({'MET' if monthly_target_met else 'NEEDS IMPROVEMENT'}) [Target: 7%+ min, 10%+ avg]")

def main():
    """Main execution"""
    backtester = ComprehensiveBacktester()
    
    print("📊 A+ GRADE COMPREHENSIVE BACKTESTING SYSTEM")
    print("=" * 80)
    print(f"📅 Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 Testing Current A+ Grade Criteria")
    print(f"📊 Stocks Under Test: {len(backtester.current_aplus_picks)}")
    print(f"🛡️ Risk Management: 6% SL | 20% TP | 3.5% Trailing | 1.5% Risk/Trade")
    print("=" * 80)
    
    # Run comprehensive backtest
    backtest_results = backtester.run_comprehensive_backtest(days_back=40)
    analysis_results = backtester.analyze_backtest_results(backtest_results)
    backtester.display_comprehensive_results(backtest_results, analysis_results)
    
    print(f"\n✅ Comprehensive Backtesting Complete - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
