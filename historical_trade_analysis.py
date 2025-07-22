#!/usr/bin/env python3
"""
Historical Trade Analysis - Last 10 Days Strong Buy Performance
Track wins, losses, stop loss hits for A+ grade system
"""

import pandas as pd
import yfinance as yf
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import warnings
warnings.filterwarnings('ignore')

class HistoricalTradeAnalyzer:
    def __init__(self):
        """Initialize with A+ grade parameters"""
        # A+ Grade Trading Parameters
        self.stop_loss_pct = 0.06  # 6% stop loss
        self.take_profit_pct = 0.20  # 20% take profit
        self.trailing_stop_pct = 0.035  # 3.5% trailing stop
        self.risk_per_trade = 0.015  # 1.5% risk per trade
        
        # Strong Buy stocks from enhanced picker (verified active)
        self.strong_buy_stocks = [
            'RELIANCE.NS', 'HDFCBANK.NS', 'TCS.NS', 'INFY.NS', 'ICICIBANK.NS',
            'SBIN.NS', 'BHARTIARTL.NS', 'ITC.NS', 'HINDUNILVR.NS', 'KOTAKBANK.NS',
            'LT.NS', 'AXISBANK.NS', 'MARUTI.NS', 'SUNPHARMA.NS', 'ULTRACEMCO.NS',
            'ASIANPAINT.NS', 'NTPC.NS', 'POWERGRID.NS', 'NESTLEIND.NS', 'TITAN.NS',
            'ONGC.NS', 'TATASTEEL.NS', 'JSWSTEEL.NS', 'COALINDIA.NS', 'BAJFINANCE.NS',
            'HCLTECH.NS', 'WIPRO.NS', 'INDUSINDBK.NS', 'ADANIPORTS.NS', 'CIPLA.NS',
            'DRREDDY.NS', 'TECHM.NS', 'DIVISLAB.NS', 'BAJAJ-AUTO.NS', 'HEROMOTOCO.NS',
            'EICHERMOT.NS', 'IOC.NS', 'BPCL.NS', 'GRASIM.NS', 'SHREECEM.NS'
        ]
    
    def get_morning_signals(self, date: datetime, symbols: List[str]) -> List[Dict]:
        """Get Strong Buy signals as of 9 AM on given date"""
        signals = []
        
        for symbol in symbols:
            try:
                # Get data up to the analysis date
                end_date = date
                start_date = date - timedelta(days=180)  # 6 months data for analysis
                
                ticker = yf.Ticker(symbol)
                data = ticker.history(start=start_date, end=end_date, interval="1d")
                
                if data.empty or len(data) < 30:
                    continue
                
                # Calculate indicators as of analysis date
                analysis = self.analyze_stock_historical(data, symbol, date)
                if analysis and analysis['direction'] == 'STRONG BUY':
                    signals.append(analysis)
                    
            except Exception as e:
                continue
        
        return signals
    
    def analyze_stock_historical(self, data: pd.DataFrame, symbol: str, analysis_date: datetime) -> Optional[Dict]:
        """Analyze stock as it would have been on the given date"""
        try:
            if len(data) < 30:
                return None
            
            # Calculate technical indicators
            indicators = self.calculate_indicators(data)
            if not indicators:
                return None
            
            current_price = data['Close'].iloc[-1]
            current_volume = data['Volume'].iloc[-1]
            
            # Signal calculation (simplified version of enhanced analysis)
            signals = []
            score = 0
            
            # RSI Analysis
            rsi = indicators['rsi'].iloc[-1] if 'rsi' in indicators else 50
            if rsi <= 25:
                signals.append("RSI Extreme Oversold")
                score += 3
            elif 25 < rsi <= 35:
                signals.append("RSI Strong Bullish Zone")
                score += 2
            
            # MACD Analysis
            if 'macd' in indicators and 'macd_signal' in indicators:
                macd = indicators['macd'].iloc[-1]
                macd_signal = indicators['macd_signal'].iloc[-1]
                if len(indicators['macd']) > 1:
                    macd_prev = indicators['macd'].iloc[-2]
                    macd_signal_prev = indicators['macd_signal'].iloc[-2]
                    
                    if macd > macd_signal and macd_prev <= macd_signal_prev:
                        signals.append("MACD Fresh Bull Crossover")
                        score += 3
            
            # Moving Average Analysis
            if 'sma_20' in indicators and 'sma_50' in indicators:
                sma_20 = indicators['sma_20'].iloc[-1]
                sma_50 = indicators['sma_50'].iloc[-1]
                if current_price > sma_20 > sma_50:
                    signals.append("Perfect MA Alignment")
                    score += 2.5
            
            # Volume Analysis
            if 'volume_ma' in indicators:
                volume_ma = indicators['volume_ma'].iloc[-1]
                volume_ratio = current_volume / volume_ma if volume_ma > 0 else 1
                if volume_ratio >= 1.8:
                    signals.append(f"High Volume ({volume_ratio:.1f}x)")
                    score += 2
            
            # Determine direction
            if score >= 4:
                direction = "STRONG BUY"
                strength = min(100, int((score + 5) / 10 * 100))
                
                return {
                    'symbol': symbol,
                    'direction': direction,
                    'strength': strength,
                    'signals': signals,
                    'entry_price': current_price,
                    'analysis_date': analysis_date,
                    'rsi': rsi,
                    'score': score
                }
            
            return None
            
        except Exception as e:
            return None
    
    def calculate_indicators(self, data: pd.DataFrame) -> Dict:
        """Calculate technical indicators"""
        if len(data) < 26:
            return {}
        
        indicators = {}
        
        try:
            # RSI
            delta = data['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            indicators['rsi'] = 100 - (100 / (1 + rs))
            
            # Moving Averages
            indicators['sma_20'] = data['Close'].rolling(20).mean()
            indicators['sma_50'] = data['Close'].rolling(50).mean()
            indicators['ema_12'] = data['Close'].ewm(span=12).mean()
            indicators['ema_26'] = data['Close'].ewm(span=26).mean()
            
            # MACD
            indicators['macd'] = indicators['ema_12'] - indicators['ema_26']
            indicators['macd_signal'] = indicators['macd'].ewm(span=9).mean()
            
            # Volume MA
            indicators['volume_ma'] = data['Volume'].rolling(20).mean()
            
        except Exception as e:
            pass
        
        return indicators
    
    def track_trade_performance(self, signal: Dict, days_forward: int = 10) -> Dict:
        """Track trade performance from entry to exit"""
        try:
            symbol = signal['symbol']
            entry_date = signal['analysis_date']
            entry_price = signal['entry_price']
            
            # Calculate trade levels
            stop_loss = entry_price * (1 - self.stop_loss_pct)
            take_profit = entry_price * (1 + self.take_profit_pct)
            trailing_stop_initial = entry_price * (1 - self.trailing_stop_pct)
            
            # Get forward price data
            start_date = entry_date
            end_date = entry_date + timedelta(days=days_forward + 5)  # Extra days for weekends
            
            ticker = yf.Ticker(symbol)
            forward_data = ticker.history(start=start_date, end=end_date, interval="1d")
            
            if forward_data.empty:
                return self.create_trade_result(signal, "NO_DATA", 0, 0, "No forward data available")
            
            # Track day by day performance
            max_profit_pct = 0
            max_drawdown_pct = 0
            trailing_stop = trailing_stop_initial
            trade_active = True
            exit_reason = "HOLDING"
            exit_price = entry_price
            exit_date = entry_date
            
            daily_performance = []
            
            for i, (date, row) in enumerate(forward_data.iterrows()):
                if i == 0:  # Skip entry day
                    continue
                
                if i > days_forward:  # Limit to tracking period
                    break
                
                high = row['High']
                low = row['Low']
                close = row['Close']
                
                # Calculate performance
                profit_pct = ((close / entry_price) - 1) * 100
                max_profit_pct = max(max_profit_pct, ((high / entry_price) - 1) * 100)
                drawdown_pct = ((low / entry_price) - 1) * 100
                max_drawdown_pct = min(max_drawdown_pct, drawdown_pct)
                
                # Check exit conditions
                if trade_active:
                    # Check stop loss hit
                    if low <= stop_loss:
                        exit_reason = "STOP_LOSS"
                        exit_price = stop_loss
                        exit_date = date
                        trade_active = False
                    
                    # Check take profit hit
                    elif high >= take_profit:
                        exit_reason = "TAKE_PROFIT"
                        exit_price = take_profit
                        exit_date = date
                        trade_active = False
                    
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
                
                daily_performance.append({
                    'date': date,
                    'close': close,
                    'profit_pct': profit_pct,
                    'trailing_stop': trailing_stop,
                    'active': trade_active
                })
            
            # If still active after tracking period
            if trade_active and daily_performance:
                exit_reason = "TIME_EXIT"
                exit_price = daily_performance[-1]['close']
                exit_date = daily_performance[-1]['date']
            
            # Calculate final performance
            final_profit_pct = ((exit_price / entry_price) - 1) * 100
            
            return self.create_trade_result(
                signal, exit_reason, final_profit_pct, max_profit_pct,
                f"Exit: ₹{exit_price:.2f} on {exit_date.strftime('%Y-%m-%d')}",
                daily_performance, max_drawdown_pct, exit_date
            )
            
        except Exception as e:
            return self.create_trade_result(signal, "ERROR", 0, 0, f"Error: {str(e)}")
    
    def create_trade_result(self, signal: Dict, exit_reason: str, profit_pct: float, 
                          max_profit_pct: float, notes: str, daily_data: List = None, 
                          max_drawdown_pct: float = 0, exit_date: datetime = None) -> Dict:
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
            'daily_data': daily_data or [],
            'exit_date': exit_date,
            'trade_duration': (exit_date - signal['analysis_date']).days if exit_date else 0
        }
    
    def analyze_last_10_days(self) -> Dict:
        """Analyze Strong Buy performance for last 10 days"""
        print("🔍 ANALYZING LAST 10 DAYS STRONG BUY PERFORMANCE")
        print("=" * 80)
        
        end_date = datetime.now()
        all_trades = []
        daily_summary = []
        
        for i in range(10):
            analysis_date = end_date - timedelta(days=i+1)
            
            # Skip weekends (rough approximation)
            if analysis_date.weekday() >= 5:
                continue
            
            print(f"📅 Analyzing {analysis_date.strftime('%Y-%m-%d')} (Day {i+1})")
            
            # Get morning signals
            morning_signals = self.get_morning_signals(analysis_date, self.strong_buy_stocks)
            
            day_trades = []
            for signal in morning_signals:
                trade_result = self.track_trade_performance(signal, days_forward=10)
                day_trades.append(trade_result)
                all_trades.append(trade_result)
            
            # Daily summary
            if day_trades:
                wins = sum(1 for t in day_trades if t['win'])
                total = len(day_trades)
                avg_profit = np.mean([t['profit_pct'] for t in day_trades])
                
                daily_summary.append({
                    'date': analysis_date,
                    'total_signals': total,
                    'wins': wins,
                    'win_rate': wins/total*100 if total > 0 else 0,
                    'avg_profit': avg_profit
                })
                
                print(f"   📊 Signals: {total} | Wins: {wins} | Win Rate: {wins/total*100:.1f}% | Avg: {avg_profit:+.1f}%")
            else:
                daily_summary.append({
                    'date': analysis_date,
                    'total_signals': 0,
                    'wins': 0,
                    'win_rate': 0,
                    'avg_profit': 0
                })
                print(f"   📊 No Strong Buy signals found")
        
        return {
            'all_trades': all_trades,
            'daily_summary': daily_summary,
            'period_start': end_date - timedelta(days=10),
            'period_end': end_date
        }
    
    def display_comprehensive_results(self, analysis: Dict):
        """Display comprehensive trade analysis results"""
        all_trades = analysis['all_trades']
        daily_summary = analysis['daily_summary']
        
        if not all_trades:
            print("\n❌ NO STRONG BUY TRADES FOUND IN LAST 10 DAYS")
            return
        
        # Overall Statistics
        total_trades = len(all_trades)
        wins = sum(1 for t in all_trades if t['win'])
        losses = total_trades - wins
        win_rate = wins / total_trades * 100 if total_trades > 0 else 0
        avg_profit = np.mean([t['profit_pct'] for t in all_trades])
        avg_win = np.mean([t['profit_pct'] for t in all_trades if t['win']]) if wins > 0 else 0
        avg_loss = np.mean([t['profit_pct'] for t in all_trades if not t['win']]) if losses > 0 else 0
        
        print(f"\n🏆 10-DAY STRONG BUY PERFORMANCE SUMMARY")
        print("=" * 80)
        print(f"📊 Total Trades: {total_trades}")
        print(f"✅ Wins: {wins} ({win_rate:.1f}%)")
        print(f"❌ Losses: {losses} ({100-win_rate:.1f}%)")
        print(f"💰 Average Return: {avg_profit:+.2f}%")
        print(f"🚀 Average Win: {avg_win:+.2f}%")
        print(f"📉 Average Loss: {avg_loss:+.2f}%")
        print(f"🎯 Risk-Reward Ratio: {abs(avg_win/avg_loss):.2f}:1" if avg_loss != 0 else "🎯 Risk-Reward: Perfect (No losses)")
        
        # Exit Reason Analysis
        exit_reasons = {}
        for trade in all_trades:
            reason = trade['exit_reason']
            if reason not in exit_reasons:
                exit_reasons[reason] = {'count': 0, 'wins': 0, 'total_profit': 0}
            exit_reasons[reason]['count'] += 1
            if trade['win']:
                exit_reasons[reason]['wins'] += 1
            exit_reasons[reason]['total_profit'] += trade['profit_pct']
        
        print(f"\n📋 EXIT REASON BREAKDOWN:")
        print("-" * 60)
        print(f"{'REASON':<15} {'COUNT':<8} {'WINS':<8} {'WIN%':<8} {'AVG%':<8}")
        print("-" * 60)
        
        for reason, stats in exit_reasons.items():
            win_pct = stats['wins'] / stats['count'] * 100 if stats['count'] > 0 else 0
            avg_pct = stats['total_profit'] / stats['count'] if stats['count'] > 0 else 0
            print(f"{reason:<15} {stats['count']:<8} {stats['wins']:<8} {win_pct:<8.1f} {avg_pct:<+8.1f}")
        
        # Best and Worst Trades
        best_trades = sorted(all_trades, key=lambda x: x['profit_pct'], reverse=True)[:5]
        worst_trades = sorted(all_trades, key=lambda x: x['profit_pct'])[:5]
        
        print(f"\n🏅 TOP 5 WINNING TRADES:")
        print("-" * 100)
        print(f"{'SYMBOL':<12} {'ENTRY':<12} {'PROFIT%':<10} {'MAX%':<10} {'REASON':<15} {'DURATION':<10} {'SIGNALS'}")
        print("-" * 100)
        
        for trade in best_trades:
            duration = f"{trade['trade_duration']}d" if trade['trade_duration'] > 0 else "Same day"
            signals = ', '.join(trade['signals'][:2])
            print(f"{trade['symbol']:<12} {trade['entry_date'].strftime('%m-%d'):<12} {trade['profit_pct']:<+10.2f} {trade['max_profit_pct']:<+10.2f} {trade['exit_reason']:<15} {duration:<10} {signals}")
        
        print(f"\n🔻 WORST 5 TRADES:")
        print("-" * 100)
        print(f"{'SYMBOL':<12} {'ENTRY':<12} {'PROFIT%':<10} {'DRAWDOWN%':<12} {'REASON':<15} {'DURATION':<10} {'SIGNALS'}")
        print("-" * 100)
        
        for trade in worst_trades:
            duration = f"{trade['trade_duration']}d" if trade['trade_duration'] > 0 else "Same day"
            signals = ', '.join(trade['signals'][:2])
            print(f"{trade['symbol']:<12} {trade['entry_date'].strftime('%m-%d'):<12} {trade['profit_pct']:<+10.2f} {trade['max_drawdown_pct']:<+12.2f} {trade['exit_reason']:<15} {duration:<10} {signals}")
        
        # Daily Performance
        print(f"\n📅 DAILY PERFORMANCE BREAKDOWN:")
        print("-" * 80)
        print(f"{'DATE':<12} {'SIGNALS':<10} {'WINS':<8} {'WIN%':<8} {'AVG%':<10} {'NOTES'}")
        print("-" * 80)
        
        for day in daily_summary:
            if day['total_signals'] > 0:
                notes = "Strong day" if day['win_rate'] > 70 else "Average day" if day['win_rate'] > 50 else "Weak day"
            else:
                notes = "No signals"
            
            print(f"{day['date'].strftime('%m-%d'):<12} {day['total_signals']:<10} {day['wins']:<8} {day['win_rate']:<8.1f} {day['avg_profit']:<+10.1f} {notes}")
        
        # Risk Management Analysis
        stop_loss_hits = [t for t in all_trades if t['exit_reason'] == 'STOP_LOSS']
        take_profit_hits = [t for t in all_trades if t['exit_reason'] == 'TAKE_PROFIT']
        trailing_stop_hits = [t for t in all_trades if t['exit_reason'] == 'TRAILING_STOP']
        
        print(f"\n🛡️ RISK MANAGEMENT EFFECTIVENESS:")
        print("-" * 60)
        print(f"🔴 Stop Loss Hits: {len(stop_loss_hits)} ({len(stop_loss_hits)/total_trades*100:.1f}%)")
        print(f"🟢 Take Profit Hits: {len(take_profit_hits)} ({len(take_profit_hits)/total_trades*100:.1f}%)")
        print(f"🟡 Trailing Stop Hits: {len(trailing_stop_hits)} ({len(trailing_stop_hits)/total_trades*100:.1f}%)")
        
        # Portfolio Impact (assuming ₹100,000 portfolio)
        portfolio_value = 100000
        total_portfolio_return = 0
        
        for trade in all_trades:
            position_size = portfolio_value * self.risk_per_trade
            trade_return = position_size * (trade['profit_pct'] / 100)
            total_portfolio_return += trade_return
        
        print(f"\n💼 PORTFOLIO IMPACT (₹1,00,000 starting capital):")
        print("-" * 60)
        print(f"💰 Total Return: ₹{total_portfolio_return:,.0f} ({total_portfolio_return/portfolio_value*100:+.2f}%)")
        print(f"📈 Final Portfolio Value: ₹{portfolio_value + total_portfolio_return:,.0f}")
        print(f"🎯 Risk Per Trade: {self.risk_per_trade*100:.1f}% (₹{portfolio_value * self.risk_per_trade:,.0f})")
        print(f"⚡ Max Single Trade Impact: {max([abs(t['profit_pct']) for t in all_trades]):.2f}% of total capital")

def main():
    """Main execution"""
    analyzer = HistoricalTradeAnalyzer()
    
    print("📊 HISTORICAL TRADE PERFORMANCE ANALYZER")
    print("=" * 80)
    print(f"📅 Analysis Period: Last 10 Trading Days")
    print(f"🎯 Focus: Strong Buy Signals (A+ Grade)")
    print(f"⏰ Analysis Time: 9:00 AM India (Market Open)")
    print(f"🛡️ Risk Management: 6% SL, 20% TP, 3.5% Trailing")
    print("=" * 80)
    
    # Perform analysis
    analysis_results = analyzer.analyze_last_10_days()
    analyzer.display_comprehensive_results(analysis_results)
    
    print(f"\n✅ Analysis Complete - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
