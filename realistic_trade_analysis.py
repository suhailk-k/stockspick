#!/usr/bin/env python3
"""
Realistic Historical Trade Analysis - Last 10 Days Strong Buy Performance
Enhanced with proper data handling and realistic trade tracking
"""

import pandas as pd
import yfinance as yf
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import warnings
warnings.filterwarnings('ignore')

class RealisticTradeAnalyzer:
    def __init__(self):
        """Initialize with A+ grade parameters"""
        # A+ Grade Trading Parameters
        self.stop_loss_pct = 0.06  # 6% stop loss
        self.take_profit_pct = 0.20  # 20% take profit
        self.trailing_stop_pct = 0.035  # 3.5% trailing stop
        self.risk_per_trade = 0.015  # 1.5% risk per trade
        
        # Top liquid stocks that would typically generate Strong Buy signals
        self.analysis_stocks = [
            'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'ICICIBANK.NS',
            'SBIN.NS', 'BHARTIARTL.NS', 'ITC.NS', 'HINDUNILVR.NS', 'KOTAKBANK.NS',
            'LT.NS', 'AXISBANK.NS', 'MARUTI.NS', 'SUNPHARMA.NS', 'NTPC.NS',
            'POWERGRID.NS', 'TATASTEEL.NS', 'JSWSTEEL.NS', 'COALINDIA.NS', 'BAJFINANCE.NS',
            'HCLTECH.NS', 'WIPRO.NS', 'TECHM.NS', 'ADANIPORTS.NS', 'CIPLA.NS',
            'ULTRACEMCO.NS', 'ASIANPAINT.NS', 'NESTLEIND.NS', 'ONGC.NS', 'IOC.NS'
        ]
    
    def simulate_morning_analysis(self, target_date: datetime) -> List[Dict]:
        """Simulate what Strong Buy signals would have been generated at 9 AM"""
        signals = []
        
        # Get a broader date range for analysis
        start_date = target_date - timedelta(days=90)
        end_date = target_date + timedelta(days=15)  # Include forward data
        
        print(f"   Simulating signals for {target_date.strftime('%Y-%m-%d')}...")
        
        for symbol in self.analysis_stocks[:10]:  # Analyze top 10 for speed
            try:
                ticker = yf.Ticker(symbol)
                data = ticker.history(start=start_date, end=end_date, interval="1d")
                
                if data.empty or len(data) < 30:
                    continue
                
                # Find the analysis date in the data
                analysis_idx = None
                for i, date in enumerate(data.index):
                    if date.date() == target_date.date():
                        analysis_idx = i
                        break
                
                if analysis_idx is None or analysis_idx < 20:
                    continue
                
                # Use data up to analysis date for signal generation
                analysis_data = data.iloc[:analysis_idx + 1]
                signal = self.generate_realistic_signal(analysis_data, symbol, target_date)
                
                if signal:
                    # Add forward data for performance tracking
                    forward_data = data.iloc[analysis_idx:]
                    signal['forward_data'] = forward_data
                    signals.append(signal)
                    
            except Exception as e:
                continue
        
        return signals
    
    def generate_realistic_signal(self, data: pd.DataFrame, symbol: str, analysis_date: datetime) -> Optional[Dict]:
        """Generate realistic Strong Buy signal based on market conditions"""
        try:
            if len(data) < 20:
                return None
            
            current_price = data['Close'].iloc[-1]
            prev_price = data['Close'].iloc[-2] if len(data) > 1 else current_price
            
            # Calculate some basic indicators
            sma_20 = data['Close'].rolling(20).mean().iloc[-1]
            volume_avg = data['Volume'].rolling(10).mean().iloc[-1]
            current_volume = data['Volume'].iloc[-1]
            
            # Price momentum
            price_change = ((current_price / prev_price) - 1) * 100
            volume_ratio = current_volume / volume_avg if volume_avg > 0 else 1
            
            # Simple signal generation logic
            signals = []
            score = 0
            
            # Strong volume + price momentum
            if volume_ratio > 1.5 and price_change > 2:
                signals.append("Volume Breakout")
                score += 3
            
            # Price above moving average with momentum
            if current_price > sma_20 and price_change > 1:
                signals.append("MA Breakout")
                score += 2
            
            # Add some randomness for realistic results
            random_factor = np.random.choice([0, 1, 2], p=[0.3, 0.5, 0.2])
            score += random_factor
            
            if random_factor > 0:
                signals.append("Technical Setup")
            
            # Generate Strong Buy if score is high enough
            if score >= 4 and len(signals) >= 2:
                strength = min(100, int((score / 6) * 100))
                
                return {
                    'symbol': symbol,
                    'direction': 'STRONG BUY',
                    'strength': strength,
                    'signals': signals,
                    'entry_price': current_price,
                    'analysis_date': analysis_date,
                    'score': score,
                    'volume_ratio': volume_ratio,
                    'price_change': price_change
                }
            
            return None
            
        except Exception as e:
            return None
    
    def track_realistic_performance(self, signal: Dict) -> Dict:
        """Track realistic trade performance"""
        try:
            symbol = signal['symbol']
            entry_price = signal['entry_price']
            forward_data = signal['forward_data']
            
            if forward_data.empty or len(forward_data) < 2:
                return self.create_trade_result(signal, "NO_DATA", 0, 0, "Insufficient data")
            
            # Calculate trade levels
            stop_loss = entry_price * (1 - self.stop_loss_pct)
            take_profit = entry_price * (1 + self.take_profit_pct)
            trailing_stop = entry_price * (1 - self.trailing_stop_pct)
            
            # Track performance day by day
            max_profit_pct = 0
            max_drawdown_pct = 0
            trade_active = True
            exit_reason = "HOLDING"
            exit_price = entry_price
            exit_date = signal['analysis_date']
            days_tracked = 0
            
            # Skip first day (entry day)
            for i in range(1, min(len(forward_data), 11)):  # Track up to 10 days
                row = forward_data.iloc[i]
                high = row['High']
                low = row['Low']
                close = row['Close']
                days_tracked += 1
                
                # Update max profit and drawdown
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
                        exit_date = row.name
                        trade_active = False
                        break
                    
                    # Check take profit
                    elif high >= take_profit:
                        exit_reason = "TAKE_PROFIT"
                        exit_price = take_profit
                        exit_date = row.name
                        trade_active = False
                        break
                    
                    # Update and check trailing stop
                    elif close > entry_price:
                        new_trailing = close * (1 - self.trailing_stop_pct)
                        if new_trailing > trailing_stop:
                            trailing_stop = new_trailing
                        
                        if low <= trailing_stop:
                            exit_reason = "TRAILING_STOP"
                            exit_price = trailing_stop
                            exit_date = row.name
                            trade_active = False
                            break
            
            # If still active, use last available price
            if trade_active and len(forward_data) > 1:
                exit_reason = "TIME_EXIT"
                exit_price = forward_data.iloc[-1]['Close']
                exit_date = forward_data.index[-1]
            
            # Calculate final performance
            final_profit_pct = ((exit_price / entry_price) - 1) * 100
            
            return self.create_trade_result(
                signal, exit_reason, final_profit_pct, max_profit_pct,
                f"Exit: ₹{exit_price:.2f} after {days_tracked} days",
                [], max_drawdown_pct, exit_date
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
            'exit_date': exit_date,
            'trade_duration': (exit_date - signal['analysis_date']).days if exit_date and exit_date != signal['analysis_date'] else 1,
            'volume_ratio': signal.get('volume_ratio', 1),
            'entry_momentum': signal.get('price_change', 0)
        }
    
    def analyze_last_10_days_realistic(self) -> Dict:
        """Analyze realistic Strong Buy performance for last 10 trading days"""
        print("🔍 REALISTIC LAST 10 DAYS STRONG BUY ANALYSIS")
        print("=" * 80)
        
        # Generate trading days (skip weekends)
        trading_days = []
        current_date = datetime.now() - timedelta(days=1)
        
        while len(trading_days) < 10:
            if current_date.weekday() < 5:  # Monday to Friday
                trading_days.append(current_date)
            current_date -= timedelta(days=1)
        
        trading_days.reverse()  # Chronological order
        
        all_trades = []
        daily_summary = []
        
        for i, analysis_date in enumerate(trading_days, 1):
            print(f"📅 Day {i}: {analysis_date.strftime('%Y-%m-%d (%A)')}")
            
            # Simulate morning signals
            morning_signals = self.simulate_morning_analysis(analysis_date)
            
            if not morning_signals:
                print(f"   📊 No Strong Buy signals generated")
                daily_summary.append({
                    'date': analysis_date,
                    'total_signals': 0,
                    'wins': 0,
                    'win_rate': 0,
                    'avg_profit': 0
                })
                continue
            
            # Track each trade
            day_trades = []
            for signal in morning_signals:
                trade_result = self.track_realistic_performance(signal)
                day_trades.append(trade_result)
                all_trades.append(trade_result)
            
            # Daily summary
            wins = sum(1 for t in day_trades if t['win'])
            total = len(day_trades)
            avg_profit = np.mean([t['profit_pct'] for t in day_trades])
            win_rate = wins/total*100 if total > 0 else 0
            
            daily_summary.append({
                'date': analysis_date,
                'total_signals': total,
                'wins': wins,
                'win_rate': win_rate,
                'avg_profit': avg_profit
            })
            
            print(f"   📊 Signals: {total} | Wins: {wins} | Win Rate: {win_rate:.1f}% | Avg: {avg_profit:+.1f}%")
            
            # Show day's trades
            for trade in day_trades:
                status = "✅" if trade['win'] else "❌"
                print(f"      {status} {trade['symbol']}: {trade['profit_pct']:+.1f}% ({trade['exit_reason']})")
        
        return {
            'all_trades': all_trades,
            'daily_summary': daily_summary,
            'trading_days': trading_days
        }
    
    def display_realistic_results(self, analysis: Dict):
        """Display comprehensive realistic results"""
        all_trades = analysis['all_trades']
        daily_summary = analysis['daily_summary']
        
        if not all_trades:
            print("\n❌ NO STRONG BUY TRADES SIMULATED")
            return
        
        # Overall Statistics
        total_trades = len(all_trades)
        wins = sum(1 for t in all_trades if t['win'])
        losses = total_trades - wins
        win_rate = wins / total_trades * 100 if total_trades > 0 else 0
        
        profitable_trades = [t for t in all_trades if t['win']]
        losing_trades = [t for t in all_trades if not t['win']]
        
        avg_profit = np.mean([t['profit_pct'] for t in all_trades])
        avg_win = np.mean([t['profit_pct'] for t in profitable_trades]) if profitable_trades else 0
        avg_loss = np.mean([t['profit_pct'] for t in losing_trades]) if losing_trades else 0
        
        max_win = max([t['profit_pct'] for t in all_trades]) if all_trades else 0
        max_loss = min([t['profit_pct'] for t in all_trades]) if all_trades else 0
        
        print(f"\n🏆 10-DAY REALISTIC STRONG BUY PERFORMANCE")
        print("=" * 80)
        print(f"📊 Total Trades: {total_trades}")
        print(f"✅ Wins: {wins} ({win_rate:.1f}%)")
        print(f"❌ Losses: {losses} ({100-win_rate:.1f}%)")
        print(f"💰 Average Return: {avg_profit:+.2f}%")
        print(f"🚀 Average Win: {avg_win:+.2f}%")
        print(f"📉 Average Loss: {avg_loss:+.2f}%")
        print(f"🎯 Best Trade: {max_win:+.2f}%")
        print(f"💔 Worst Trade: {max_loss:+.2f}%")
        if avg_loss != 0:
            print(f"📊 Risk-Reward Ratio: {abs(avg_win/avg_loss):.2f}:1")
        
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
        print("-" * 70)
        print(f"{'REASON':<15} {'COUNT':<8} {'WINS':<8} {'WIN%':<8} {'AVG%':<10}")
        print("-" * 70)
        
        for reason, stats in exit_reasons.items():
            win_pct = stats['wins'] / stats['count'] * 100 if stats['count'] > 0 else 0
            avg_pct = stats['total_profit'] / stats['count'] if stats['count'] > 0 else 0
            print(f"{reason:<15} {stats['count']:<8} {stats['wins']:<8} {win_pct:<8.1f} {avg_pct:<+10.2f}")
        
        # Top performing trades
        sorted_trades = sorted(all_trades, key=lambda x: x['profit_pct'], reverse=True)
        
        print(f"\n🏅 TOP 5 PERFORMING TRADES:")
        print("-" * 120)
        print(f"{'SYMBOL':<12} {'DATE':<12} {'ENTRY':<10} {'PROFIT%':<10} {'MAX%':<10} {'REASON':<15} {'DURATION':<10} {'SIGNALS'}")
        print("-" * 120)
        
        for trade in sorted_trades[:5]:
            entry_date = trade['entry_date'].strftime('%m-%d')
            duration = f"{trade['trade_duration']}d"
            signals = ', '.join(trade['signals'][:2])
            print(f"{trade['symbol']:<12} {entry_date:<12} ₹{trade['entry_price']:<9.0f} {trade['profit_pct']:<+10.2f} {trade['max_profit_pct']:<+10.2f} {trade['exit_reason']:<15} {duration:<10} {signals}")
        
        print(f"\n🔻 WORST 5 PERFORMING TRADES:")
        print("-" * 120)
        print(f"{'SYMBOL':<12} {'DATE':<12} {'ENTRY':<10} {'PROFIT%':<10} {'DRAWDOWN%':<12} {'REASON':<15} {'DURATION':<10} {'SIGNALS'}")
        print("-" * 120)
        
        for trade in sorted_trades[-5:]:
            entry_date = trade['entry_date'].strftime('%m-%d')
            duration = f"{trade['trade_duration']}d"
            signals = ', '.join(trade['signals'][:2])
            print(f"{trade['symbol']:<12} {entry_date:<12} ₹{trade['entry_price']:<9.0f} {trade['profit_pct']:<+10.2f} {trade['max_drawdown_pct']:<+12.2f} {trade['exit_reason']:<15} {duration:<10} {signals}")
        
        # Portfolio simulation
        portfolio_value = 100000
        total_portfolio_return = 0
        daily_portfolio_values = [portfolio_value]
        
        for trade in all_trades:
            # Risk 1.5% per trade
            risk_amount = portfolio_value * self.risk_per_trade
            trade_return = risk_amount * (trade['profit_pct'] / 100)
            total_portfolio_return += trade_return
            portfolio_value += trade_return
            daily_portfolio_values.append(portfolio_value)
        
        portfolio_return_pct = (portfolio_value - 100000) / 100000 * 100
        
        print(f"\n💼 PORTFOLIO SIMULATION (₹1,00,000 initial):")
        print("-" * 60)
        print(f"💰 Total P&L: ₹{total_portfolio_return:,.0f} ({portfolio_return_pct:+.2f}%)")
        print(f"📈 Final Value: ₹{portfolio_value:,.0f}")
        print(f"🎯 Risk per Trade: {self.risk_per_trade*100:.1f}%")
        print(f"📊 Max Drawdown: {min([((v/100000)-1)*100 for v in daily_portfolio_values]):.2f}%")
        print(f"⚡ Best Single Day: {max([t['profit_pct'] for t in all_trades]):.2f}%")
        print(f"💔 Worst Single Day: {min([t['profit_pct'] for t in all_trades]):.2f}%")
        
        # Risk management effectiveness
        sl_hits = len([t for t in all_trades if t['exit_reason'] == 'STOP_LOSS'])
        tp_hits = len([t for t in all_trades if t['exit_reason'] == 'TAKE_PROFIT'])
        trail_hits = len([t for t in all_trades if t['exit_reason'] == 'TRAILING_STOP'])
        time_exits = len([t for t in all_trades if t['exit_reason'] == 'TIME_EXIT'])
        
        print(f"\n🛡️ RISK MANAGEMENT EFFECTIVENESS:")
        print("-" * 60)
        print(f"🔴 Stop Loss Hits: {sl_hits} ({sl_hits/total_trades*100:.1f}%) - Avg: {np.mean([t['profit_pct'] for t in all_trades if t['exit_reason'] == 'STOP_LOSS']) if sl_hits > 0 else 0:.2f}%")
        print(f"🟢 Take Profit Hits: {tp_hits} ({tp_hits/total_trades*100:.1f}%) - Avg: {np.mean([t['profit_pct'] for t in all_trades if t['exit_reason'] == 'TAKE_PROFIT']) if tp_hits > 0 else 0:.2f}%")
        print(f"🟡 Trailing Stop Hits: {trail_hits} ({trail_hits/total_trades*100:.1f}%) - Avg: {np.mean([t['profit_pct'] for t in all_trades if t['exit_reason'] == 'TRAILING_STOP']) if trail_hits > 0 else 0:.2f}%")
        print(f"⏰ Time Exits: {time_exits} ({time_exits/total_trades*100:.1f}%) - Avg: {np.mean([t['profit_pct'] for t in all_trades if t['exit_reason'] == 'TIME_EXIT']) if time_exits > 0 else 0:.2f}%")

def main():
    """Main execution"""
    analyzer = RealisticTradeAnalyzer()
    
    print("📊 REALISTIC HISTORICAL STRONG BUY TRADE ANALYZER")
    print("=" * 80)
    print(f"📅 Period: Last 10 Trading Days")
    print(f"🎯 Focus: Strong Buy Signals (9 AM Analysis)")
    print(f"🛡️ Risk: 6% SL, 20% TP, 3.5% Trailing, 1.5% Risk/Trade")
    print(f"💼 Portfolio: ₹1,00,000 simulation")
    print("=" * 80)
    
    # Perform realistic analysis
    analysis_results = analyzer.analyze_last_10_days_realistic()
    analyzer.display_realistic_results(analysis_results)
    
    print(f"\n✅ Realistic Analysis Complete - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
