#!/usr/bin/env python3
"""
6-Month Historical Backtesting System
Analyzes every trading day for the last 6 months
Tracks top 5 stock suggestions with complete performance data
"""

import pandas as pd
import yfinance as yf
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')
from daily_stock_picker import DailyStockPicker
import json
import os

class Historical6MonthBacktester:
    """Complete 6-month historical analysis with daily stock picks"""
    
    def __init__(self):
        """Initialize backtester with enhanced tracking"""
        self.picker = DailyStockPicker()
        self.results = []
        self.trade_log = []
        self.performance_summary = {}
        
        # Trading parameters
        self.holding_period = 10  # Hold for 10 trading days
        self.max_trades_per_day = 5  # Top 5 picks per day
        
        # Create results directory
        os.makedirs('backtest_results', exist_ok=True)
    
    def get_trading_days(self, start_date: datetime, end_date: datetime) -> List[datetime]:
        """Get all valid trading days in the period"""
        trading_days = []
        current_date = start_date
        
        while current_date <= end_date:
            # Skip weekends
            if current_date.weekday() < 5:  # Monday = 0, Friday = 4
                trading_days.append(current_date)
            current_date += timedelta(days=1)
        
        return trading_days
    
    def get_future_price(self, symbol: str, entry_date: datetime, days_ahead: int) -> Optional[float]:
        """Get stock price after specified days"""
        try:
            start_date = entry_date
            end_date = entry_date + timedelta(days=days_ahead + 10)  # Buffer for weekends
            
            ticker = yf.Ticker(symbol)
            data = ticker.history(start=start_date, end=end_date, interval="1d")
            
            if len(data) < days_ahead:
                return None
            
            # Get price after specified trading days
            return data['Close'].iloc[min(days_ahead, len(data)-1)]
            
        except Exception:
            return None
    
    def calculate_trade_outcome(self, entry_price: float, stop_loss: float, take_profit: float, 
                               symbol: str, entry_date: datetime) -> Dict:
        """Calculate detailed trade outcome with day-by-day tracking"""
        trade_result = {
            'symbol': symbol,
            'entry_date': entry_date.strftime('%Y-%m-%d'),
            'entry_price': entry_price,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'outcome': 'ONGOING',
            'exit_price': None,
            'exit_date': None,
            'return_pct': 0,
            'days_held': 0,
            'hit_target': False,
            'hit_stop_loss': False,
            'daily_prices': []
        }
        
        try:
            # Get daily prices for holding period
            start_date = entry_date
            end_date = entry_date + timedelta(days=self.holding_period + 10)
            
            ticker = yf.Ticker(symbol)
            data = ticker.history(start=start_date, end=end_date, interval="1d")
            
            if data.empty:
                return trade_result
            
            # Track day-by-day performance
            for i, (date, row) in enumerate(data.iterrows()):
                if i == 0:
                    continue  # Skip entry day
                
                current_price = row['Close']
                days_held = i
                
                trade_result['daily_prices'].append({
                    'date': date.strftime('%Y-%m-%d'),
                    'price': current_price,
                    'return_pct': ((current_price - entry_price) / entry_price * 100)
                })
                
                # Check if stop loss hit
                if current_price <= stop_loss:
                    trade_result['outcome'] = 'STOP_LOSS'
                    trade_result['exit_price'] = stop_loss
                    trade_result['exit_date'] = date.strftime('%Y-%m-%d')
                    trade_result['return_pct'] = ((stop_loss - entry_price) / entry_price * 100)
                    trade_result['days_held'] = days_held
                    trade_result['hit_stop_loss'] = True
                    break
                
                # Check if take profit hit
                if current_price >= take_profit:
                    trade_result['outcome'] = 'TAKE_PROFIT'
                    trade_result['exit_price'] = take_profit
                    trade_result['exit_date'] = date.strftime('%Y-%m-%d')
                    trade_result['return_pct'] = ((take_profit - entry_price) / entry_price * 100)
                    trade_result['days_held'] = days_held
                    trade_result['hit_target'] = True
                    break
                
                # Exit after holding period
                if days_held >= self.holding_period:
                    trade_result['outcome'] = 'TIME_EXIT'
                    trade_result['exit_price'] = current_price
                    trade_result['exit_date'] = date.strftime('%Y-%m-%d')
                    trade_result['return_pct'] = ((current_price - entry_price) / entry_price * 100)
                    trade_result['days_held'] = days_held
                    break
            
        except Exception as e:
            pass
        
        return trade_result
    
    def run_historical_analysis(self, months_back: int = 6) -> Dict:
        """Run complete 6-month historical analysis"""
        print(f"🚀 STARTING 6-MONTH HISTORICAL BACKTEST")
        print("=" * 80)
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=months_back * 30)
        
        print(f"📅 Analysis Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        print(f"🎯 Strategy: Top 5 daily picks, 10-day holding period")
        print(f"🛡️ Risk Management: 6% SL, 20% TP")
        
        # Get all trading days
        trading_days = self.get_trading_days(start_date, end_date)
        print(f"📊 Total Trading Days: {len(trading_days)}")
        print("=" * 80)
        
        all_trades = []
        daily_results = []
        
        for day_num, analysis_date in enumerate(trading_days, 1):
            print(f"\n📈 Day {day_num}/{len(trading_days)}: {analysis_date.strftime('%Y-%m-%d %A')}")
            
            # Get stock picks for this date
            opportunities = self.picker.scan_for_date(analysis_date)
            
            if not opportunities:
                print("   ❌ No opportunities found")
                continue
            
            # Take top 5 picks
            top_5_picks = sorted(opportunities, key=lambda x: x['strength'], reverse=True)[:5]
            
            print(f"   ✅ Found {len(opportunities)} opportunities, analyzing top 5:")
            
            daily_trades = []
            
            for rank, pick in enumerate(top_5_picks, 1):
                symbol = pick['symbol']
                entry_price = pick['price']
                stop_loss = pick['stop_loss']
                take_profit = pick['take_profit']
                
                print(f"      {rank}. {symbol} @ ₹{entry_price:.2f} (Strength: {pick['strength']}%)")
                
                # Calculate trade outcome
                trade_result = self.calculate_trade_outcome(
                    entry_price, stop_loss, take_profit, symbol, analysis_date
                )
                trade_result['rank'] = rank
                trade_result['strength'] = pick['strength']
                trade_result['signals'] = pick['signals']
                
                daily_trades.append(trade_result)
                all_trades.append(trade_result)
            
            # Store daily summary
            daily_summary = {
                'date': analysis_date.strftime('%Y-%m-%d'),
                'total_opportunities': len(opportunities),
                'trades_taken': len(daily_trades),
                'avg_strength': np.mean([t['strength'] for t in daily_trades]),
                'trades': daily_trades
            }
            daily_results.append(daily_summary)
            
            # Progress update
            if day_num % 10 == 0:
                completed_trades = [t for t in all_trades if t['outcome'] != 'ONGOING']
                if completed_trades:
                    win_rate = len([t for t in completed_trades if t['return_pct'] > 0]) / len(completed_trades) * 100
                    avg_return = np.mean([t['return_pct'] for t in completed_trades])
                    print(f"   📊 Progress: {day_num} days analyzed, {len(completed_trades)} trades completed")
                    print(f"   📈 Current Win Rate: {win_rate:.1f}%, Avg Return: {avg_return:+.2f}%")
        
        print(f"\n✅ Historical Analysis Complete!")
        print(f"📊 Total Trades Analyzed: {len(all_trades)}")
        
        # Generate comprehensive results
        return self.generate_comprehensive_results(all_trades, daily_results, start_date, end_date)
    
    def generate_comprehensive_results(self, all_trades: List[Dict], daily_results: List[Dict], 
                                     start_date: datetime, end_date: datetime) -> Dict:
        """Generate detailed performance analysis"""
        print(f"\n📊 GENERATING COMPREHENSIVE RESULTS...")
        
        # Filter completed trades
        completed_trades = [t for t in all_trades if t['outcome'] != 'ONGOING']
        
        if not completed_trades:
            print("❌ No completed trades to analyze")
            return {}
        
        # Performance metrics
        winning_trades = [t for t in completed_trades if t['return_pct'] > 0]
        losing_trades = [t for t in completed_trades if t['return_pct'] <= 0]
        
        # Calculate metrics
        total_trades = len(completed_trades)
        win_rate = len(winning_trades) / total_trades * 100
        loss_rate = len(losing_trades) / total_trades * 100
        
        avg_win = np.mean([t['return_pct'] for t in winning_trades]) if winning_trades else 0
        avg_loss = np.mean([t['return_pct'] for t in losing_trades]) if losing_trades else 0
        avg_return = np.mean([t['return_pct'] for t in completed_trades])
        
        # Risk metrics
        max_win = max([t['return_pct'] for t in completed_trades])
        max_loss = min([t['return_pct'] for t in completed_trades])
        
        # Target/Stop analysis
        target_hits = len([t for t in completed_trades if t['hit_target']])
        stop_hits = len([t for t in completed_trades if t['hit_stop_loss']])
        time_exits = len([t for t in completed_trades if t['outcome'] == 'TIME_EXIT'])
        
        # Monthly breakdown
        monthly_performance = self.calculate_monthly_performance(completed_trades)
        
        # Stock-wise performance
        stock_performance = self.calculate_stock_performance(completed_trades)
        
        # Results summary
        results = {
            'analysis_period': {
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'trading_days': len(daily_results)
            },
            'overall_performance': {
                'total_trades': total_trades,
                'win_rate': win_rate,
                'loss_rate': loss_rate,
                'avg_return': avg_return,
                'avg_win': avg_win,
                'avg_loss': avg_loss,
                'max_win': max_win,
                'max_loss': max_loss,
                'target_hit_rate': target_hits / total_trades * 100,
                'stop_loss_rate': stop_hits / total_trades * 100,
                'time_exit_rate': time_exits / total_trades * 100
            },
            'monthly_performance': monthly_performance,
            'stock_performance': stock_performance,
            'detailed_trades': completed_trades,
            'daily_results': daily_results
        }
        
        # Save results
        self.save_results(results)
        
        # Display summary
        self.display_results_summary(results)
        
        return results
    
    def calculate_monthly_performance(self, trades: List[Dict]) -> Dict:
        """Calculate month-wise performance breakdown"""
        monthly_data = {}
        
        for trade in trades:
            month_key = trade['entry_date'][:7]  # YYYY-MM
            
            if month_key not in monthly_data:
                monthly_data[month_key] = {
                    'trades': 0,
                    'wins': 0,
                    'losses': 0,
                    'total_return': 0,
                    'returns': []
                }
            
            monthly_data[month_key]['trades'] += 1
            monthly_data[month_key]['total_return'] += trade['return_pct']
            monthly_data[month_key]['returns'].append(trade['return_pct'])
            
            if trade['return_pct'] > 0:
                monthly_data[month_key]['wins'] += 1
            else:
                monthly_data[month_key]['losses'] += 1
        
        # Calculate monthly metrics
        for month in monthly_data:
            data = monthly_data[month]
            data['win_rate'] = data['wins'] / data['trades'] * 100 if data['trades'] > 0 else 0
            data['avg_return'] = data['total_return'] / data['trades'] if data['trades'] > 0 else 0
            data['best_trade'] = max(data['returns']) if data['returns'] else 0
            data['worst_trade'] = min(data['returns']) if data['returns'] else 0
        
        return monthly_data
    
    def calculate_stock_performance(self, trades: List[Dict]) -> Dict:
        """Calculate stock-wise performance metrics"""
        stock_data = {}
        
        for trade in trades:
            symbol = trade['symbol']
            
            if symbol not in stock_data:
                stock_data[symbol] = {
                    'trades': 0,
                    'wins': 0,
                    'losses': 0,
                    'total_return': 0,
                    'returns': [],
                    'avg_strength': 0,
                    'strengths': []
                }
            
            stock_data[symbol]['trades'] += 1
            stock_data[symbol]['total_return'] += trade['return_pct']
            stock_data[symbol]['returns'].append(trade['return_pct'])
            stock_data[symbol]['strengths'].append(trade['strength'])
            
            if trade['return_pct'] > 0:
                stock_data[symbol]['wins'] += 1
            else:
                stock_data[symbol]['losses'] += 1
        
        # Calculate stock metrics
        for symbol in stock_data:
            data = stock_data[symbol]
            data['win_rate'] = data['wins'] / data['trades'] * 100 if data['trades'] > 0 else 0
            data['avg_return'] = data['total_return'] / data['trades'] if data['trades'] > 0 else 0
            data['avg_strength'] = np.mean(data['strengths']) if data['strengths'] else 0
            data['best_trade'] = max(data['returns']) if data['returns'] else 0
            data['worst_trade'] = min(data['returns']) if data['returns'] else 0
        
        return stock_data
    
    def save_results(self, results: Dict):
        """Save comprehensive results to files"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save complete results as JSON
        with open(f'backtest_results/6month_backtest_{timestamp}.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        # Create detailed CSV for trades
        trades_df = pd.DataFrame(results['detailed_trades'])
        trades_df.to_csv(f'backtest_results/6month_trades_{timestamp}.csv', index=False)
        
        # Create summary CSV
        summary_data = []
        for month, data in results['monthly_performance'].items():
            summary_data.append({
                'Month': month,
                'Trades': data['trades'],
                'Win_Rate_%': data['win_rate'],
                'Avg_Return_%': data['avg_return'],
                'Best_Trade_%': data['best_trade'],
                'Worst_Trade_%': data['worst_trade']
            })
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_csv(f'backtest_results/6month_summary_{timestamp}.csv', index=False)
        
        print(f"💾 Results saved to backtest_results/ folder")
    
    def display_results_summary(self, results: Dict):
        """Display comprehensive results summary"""
        print(f"\n🏆 6-MONTH BACKTEST RESULTS SUMMARY")
        print("=" * 80)
        
        perf = results['overall_performance']
        period = results['analysis_period']
        
        print(f"📅 Analysis Period: {period['start_date']} to {period['end_date']}")
        print(f"📊 Trading Days Analyzed: {period['trading_days']}")
        print(f"🎯 Total Trades: {perf['total_trades']}")
        
        print(f"\n📈 PERFORMANCE METRICS:")
        print("-" * 40)
        print(f"✅ Win Rate: {perf['win_rate']:.1f}%")
        print(f"❌ Loss Rate: {perf['loss_rate']:.1f}%")
        print(f"📊 Average Return: {perf['avg_return']:+.2f}%")
        print(f"🟢 Average Win: +{perf['avg_win']:.2f}%")
        print(f"🔴 Average Loss: {perf['avg_loss']:.2f}%")
        print(f"🚀 Best Trade: +{perf['max_win']:.2f}%")
        print(f"📉 Worst Trade: {perf['max_loss']:.2f}%")
        
        print(f"\n🎯 EXIT ANALYSIS:")
        print("-" * 40)
        print(f"🏆 Target Hits: {perf['target_hit_rate']:.1f}%")
        print(f"🛑 Stop Losses: {perf['stop_loss_rate']:.1f}%")
        print(f"⏰ Time Exits: {perf['time_exit_rate']:.1f}%")
        
        # Monthly performance
        print(f"\n📅 MONTHLY PERFORMANCE:")
        print("-" * 60)
        print(f"{'Month':<8} {'Trades':<7} {'Win%':<7} {'Avg%':<8} {'Best%':<8} {'Worst%':<8}")
        print("-" * 60)
        
        for month in sorted(results['monthly_performance'].keys()):
            data = results['monthly_performance'][month]
            print(f"{month:<8} {data['trades']:<7} {data['win_rate']:<7.1f} "
                  f"{data['avg_return']:<+8.2f} {data['best_trade']:<+8.2f} {data['worst_trade']:<+8.2f}")
        
        # Top performing stocks
        print(f"\n🏆 TOP PERFORMING STOCKS:")
        print("-" * 70)
        print(f"{'Symbol':<15} {'Trades':<7} {'Win%':<7} {'Avg%':<8} {'Strength':<9}")
        print("-" * 70)
        
        # Sort stocks by avg return
        sorted_stocks = sorted(results['stock_performance'].items(), 
                             key=lambda x: x[1]['avg_return'], reverse=True)[:10]
        
        for symbol, data in sorted_stocks:
            print(f"{symbol:<15} {data['trades']:<7} {data['win_rate']:<7.1f} "
                  f"{data['avg_return']:<+8.2f} {data['avg_strength']:<9.1f}")
        
        print(f"\n✅ Analysis Complete - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    """Run comprehensive 6-month backtest"""
    backtester = Historical6MonthBacktester()
    
    print("🔍 Welcome to 6-Month Historical Backtester!")
    print("This will analyze EVERY trading day for the past 6 months")
    print("Tracking top 5 stock picks daily with complete performance data")
    
    confirm = input("\nThis analysis will take 10-15 minutes. Continue? (y/n): ").strip().lower()
    
    if confirm != 'y':
        print("❌ Analysis cancelled.")
        return
    
    # Run the analysis
    results = backtester.run_historical_analysis(months_back=6)
    
    if results:
        print(f"\n🎯 KEY FINDINGS:")
        perf = results['overall_performance']
        print(f"   • Analyzed {perf['total_trades']} trades over 6 months")
        print(f"   • Achieved {perf['win_rate']:.1f}% win rate")
        print(f"   • Average return per trade: {perf['avg_return']:+.2f}%")
        print(f"   • Target hit rate: {perf['target_hit_rate']:.1f}%")
        
        print(f"\n💾 Detailed results saved in 'backtest_results/' folder")
        print(f"📊 Files include: JSON data, CSV trades, monthly summary")

if __name__ == "__main__":
    main()
