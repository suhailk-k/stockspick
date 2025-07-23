#!/usr/bin/env python3
"""
6-Month Backtest Results Table Generator
Create formatted tables from the comprehensive backtesting data
"""

import pandas as pd
import json
import os
from datetime import datetime
from typing import Dict, List
import glob

class BacktestTableGenerator:
    """Generate formatted tables from backtest results"""
    
    def __init__(self):
        """Initialize table generator"""
        self.results_dir = 'backtest_results'
        
    def load_latest_results(self) -> Dict:
        """Load the most recent backtest results"""
        try:
            # Find the latest JSON file
            json_files = glob.glob(f"{self.results_dir}/6month_backtest_*.json")
            if not json_files:
                print("❌ No backtest results found. Run historical_6month_backtester.py first.")
                return {}
            
            latest_file = max(json_files)
            print(f"📊 Loading results from: {os.path.basename(latest_file)}")
            
            with open(latest_file, 'r') as f:
                return json.load(f)
                
        except Exception as e:
            print(f"❌ Error loading results: {e}")
            return {}
    
    def format_percentage(self, value: float) -> str:
        """Format percentage values"""
        return f"{value:+6.2f}%"
    
    def format_currency(self, value: float) -> str:
        """Format currency values"""
        return f"₹{value:8,.2f}"
    
    def generate_summary_table(self, results: Dict):
        """Generate executive summary table"""
        if not results:
            return
        
        perf = results['overall_performance']
        period = results['analysis_period']
        
        print("\n" + "="*80)
        print("📊 6-MONTH BACKTEST EXECUTIVE SUMMARY")
        print("="*80)
        
        # Main metrics table
        summary_data = [
            ["📅 Analysis Period", f"{period['start_date']} to {period['end_date']}"],
            ["📊 Trading Days", f"{period['trading_days']} days"],
            ["🎯 Total Trades", f"{perf['total_trades']} trades"],
            ["✅ Win Rate", f"{perf['win_rate']:.1f}%"],
            ["❌ Loss Rate", f"{perf['loss_rate']:.1f}%"],
            ["📈 Average Return", self.format_percentage(perf['avg_return'])],
            ["🟢 Average Win", self.format_percentage(perf['avg_win'])],
            ["🔴 Average Loss", self.format_percentage(perf['avg_loss'])],
            ["🚀 Best Trade", self.format_percentage(perf['max_win'])],
            ["📉 Worst Trade", self.format_percentage(perf['max_loss'])],
            ["🎯 Target Hit Rate", f"{perf['target_hit_rate']:.1f}%"],
            ["🛑 Stop Loss Rate", f"{perf['stop_loss_rate']:.1f}%"],
            ["⏰ Time Exit Rate", f"{perf['time_exit_rate']:.1f}%"]
        ]
        
        # Print formatted table
        for metric, value in summary_data:
            print(f"{metric:<20} │ {value:>15}")
        
        print("="*80)
    
    def generate_monthly_table(self, results: Dict):
        """Generate monthly performance breakdown table"""
        if not results or 'monthly_performance' not in results:
            return
        
        print("\n" + "="*90)
        print("📅 MONTHLY PERFORMANCE BREAKDOWN")
        print("="*90)
        
        # Table headers
        headers = ["Month", "Trades", "Wins", "Losses", "Win%", "Avg%", "Best%", "Worst%"]
        print(f"{'Month':<8} │ {'Trades':<6} │ {'Wins':<5} │ {'Loss':<5} │ {'Win%':<6} │ {'Avg%':<8} │ {'Best%':<8} │ {'Worst%':<8}")
        print("─" * 90)
        
        monthly_data = results['monthly_performance']
        total_trades = 0
        total_wins = 0
        
        for month in sorted(monthly_data.keys()):
            data = monthly_data[month]
            total_trades += data['trades']
            total_wins += data['wins']
            
            print(f"{month:<8} │ {data['trades']:<6} │ {data['wins']:<5} │ {data['losses']:<5} │ "
                  f"{data['win_rate']:<6.1f} │ {data['avg_return']:<+8.2f} │ "
                  f"{data['best_trade']:<+8.2f} │ {data['worst_trade']:<+8.2f}")
        
        print("─" * 90)
        overall_win_rate = (total_wins / total_trades * 100) if total_trades > 0 else 0
        print(f"{'TOTAL':<8} │ {total_trades:<6} │ {total_wins:<5} │ {total_trades-total_wins:<5} │ {overall_win_rate:<6.1f} │ {'N/A':<8} │ {'N/A':<8} │ {'N/A':<8}")
        print("="*90)
    
    def generate_top_stocks_table(self, results: Dict, top_n: int = 15):
        """Generate top performing stocks table"""
        if not results or 'stock_performance' not in results:
            return
        
        print(f"\n" + "="*95)
        print(f"🏆 TOP {top_n} PERFORMING STOCKS")
        print("="*95)
        
        # Sort stocks by average return
        stock_data = results['stock_performance']
        sorted_stocks = sorted(stock_data.items(), key=lambda x: x[1]['avg_return'], reverse=True)[:top_n]
        
        # Table headers
        print(f"{'Rank':<4} │ {'Symbol':<15} │ {'Trades':<6} │ {'Wins':<5} │ {'Win%':<6} │ {'Avg%':<8} │ {'Best%':<8} │ {'Worst%':<8} │ {'Strength':<8}")
        print("─" * 95)
        
        for rank, (symbol, data) in enumerate(sorted_stocks, 1):
            print(f"{rank:<4} │ {symbol:<15} │ {data['trades']:<6} │ {data['wins']:<5} │ "
                  f"{data['win_rate']:<6.1f} │ {data['avg_return']:<+8.2f} │ "
                  f"{data['best_trade']:<+8.2f} │ {data['worst_trade']:<+8.2f} │ {data['avg_strength']:<8.1f}")
        
        print("="*95)
    
    def generate_worst_stocks_table(self, results: Dict, bottom_n: int = 10):
        """Generate worst performing stocks table"""
        if not results or 'stock_performance' not in results:
            return
        
        print(f"\n" + "="*95)
        print(f"📉 WORST {bottom_n} PERFORMING STOCKS")
        print("="*95)
        
        # Sort stocks by average return (ascending for worst)
        stock_data = results['stock_performance']
        sorted_stocks = sorted(stock_data.items(), key=lambda x: x[1]['avg_return'])[:bottom_n]
        
        # Table headers
        print(f"{'Rank':<4} │ {'Symbol':<15} │ {'Trades':<6} │ {'Wins':<5} │ {'Win%':<6} │ {'Avg%':<8} │ {'Best%':<8} │ {'Worst%':<8} │ {'Strength':<8}")
        print("─" * 95)
        
        for rank, (symbol, data) in enumerate(sorted_stocks, 1):
            print(f"{rank:<4} │ {symbol:<15} │ {data['trades']:<6} │ {data['wins']:<5} │ "
                  f"{data['win_rate']:<6.1f} │ {data['avg_return']:<+8.2f} │ "
                  f"{data['best_trade']:<+8.2f} │ {data['worst_trade']:<+8.2f} │ {data['avg_strength']:<8.1f}")
        
        print("="*95)
    
    def generate_position_sizing_table(self, account_size: float = 100000):
        """Generate position sizing table for different stock prices"""
        print(f"\n" + "="*100)
        print(f"💰 POSITION SIZING TABLE (₹{account_size:,.0f} Account)")
        print("="*100)
        
        risk_per_trade = account_size * 0.02  # 2%
        max_position = account_size * 0.10    # 10%
        stop_loss_pct = 0.06                  # 6%
        
        # Sample stock prices
        stock_prices = [100, 200, 500, 1000, 1500, 2000, 3000, 5000, 10000, 15000]
        
        print(f"{'Price':<8} │ {'Max Shares':<10} │ {'Investment':<12} │ {'Risk Amount':<12} │ {'Stop Loss':<10} │ {'Take Profit':<12}")
        print("─" * 100)
        
        for price in stock_prices:
            # Calculate position size based on risk
            max_shares_by_risk = int(risk_per_trade / (price * stop_loss_pct))
            max_shares_by_position = int(max_position / price)
            max_shares = min(max_shares_by_risk, max_shares_by_position)
            
            investment = max_shares * price
            risk_amount = max_shares * price * stop_loss_pct
            stop_loss_price = price * (1 - stop_loss_pct)
            take_profit_price = price * 1.20
            
            print(f"₹{price:<7} │ {max_shares:<10} │ ₹{investment:<11,.0f} │ ₹{risk_amount:<11,.0f} │ ₹{stop_loss_price:<9.2f} │ ₹{take_profit_price:<11.2f}")
        
        print("="*100)
        print(f"📋 Rules: Max 2% risk per trade | Max 10% position size | 6% stop loss | 20% take profit")
    
    def generate_sector_analysis_table(self, results: Dict):
        """Generate sector-wise performance analysis"""
        if not results or 'detailed_trades' not in results:
            return
        
        print(f"\n" + "="*85)
        print("🏢 SECTOR-WISE PERFORMANCE ANALYSIS")
        print("="*85)
        
        # Categorize trades by sector
        sector_data = {}
        
        for trade in results['detailed_trades']:
            symbol = trade['symbol'].replace('.NS', '')
            
            # Sector classification
            if any(bank in symbol for bank in ['BANK', 'HDFC', 'ICICI', 'KOTAK', 'AXIS', 'SBIN', 'BAJFINANCE', 'AUBANK']):
                sector = 'Banking'
            elif symbol in ['TCS', 'INFY', 'HCLTECH', 'WIPRO', 'TECHM', 'LTIM', 'PERSISTENT', 'LTTS', 'MPHASIS', 'COFORGE']:
                sector = 'IT'
            elif symbol in ['RELIANCE', 'ONGC', 'IOC', 'BPCL', 'TATASTEEL', 'JSWSTEEL', 'HINDALCO', 'VEDL', 'COALINDIA']:
                sector = 'Energy & Commodities'
            elif symbol in ['SUNPHARMA', 'DRREDDY', 'CIPLA', 'DIVISLAB', 'BIOCON', 'LUPIN', 'TORNTPHARM', 'APOLLOHOSP', 'FORTIS', 'LALPATHLAB']:
                sector = 'Pharma & Healthcare'
            elif symbol in ['HINDUNILVR', 'ITC', 'NESTLEIND', 'BRITANNIA', 'MARICO', 'DABUR', 'GODREJCP', 'TATACONSUM', 'JUBLFOOD', 'TRENT']:
                sector = 'FMCG & Retail'
            elif symbol in ['MARUTI', 'TATAMOTORS', 'M&M', 'BAJAJ-AUTO', 'HEROMOTOCO', 'EICHERMOT', 'ASHOKLEY', 'MRF', 'APOLLOTYRE', 'ESCORTS']:
                sector = 'Automotive'
            else:
                sector = 'Others'
            
            if sector not in sector_data:
                sector_data[sector] = {
                    'trades': 0,
                    'wins': 0,
                    'total_return': 0,
                    'returns': []
                }
            
            sector_data[sector]['trades'] += 1
            sector_data[sector]['total_return'] += trade['return_pct']
            sector_data[sector]['returns'].append(trade['return_pct'])
            
            if trade['return_pct'] > 0:
                sector_data[sector]['wins'] += 1
        
        # Calculate sector metrics and sort by average return
        sector_metrics = []
        for sector, data in sector_data.items():
            win_rate = (data['wins'] / data['trades'] * 100) if data['trades'] > 0 else 0
            avg_return = data['total_return'] / data['trades'] if data['trades'] > 0 else 0
            best_trade = max(data['returns']) if data['returns'] else 0
            worst_trade = min(data['returns']) if data['returns'] else 0
            
            sector_metrics.append({
                'sector': sector,
                'trades': data['trades'],
                'wins': data['wins'],
                'win_rate': win_rate,
                'avg_return': avg_return,
                'best_trade': best_trade,
                'worst_trade': worst_trade
            })
        
        # Sort by average return
        sector_metrics.sort(key=lambda x: x['avg_return'], reverse=True)
        
        # Print table
        print(f"{'Sector':<20} │ {'Trades':<6} │ {'Wins':<5} │ {'Win%':<6} │ {'Avg%':<8} │ {'Best%':<8} │ {'Worst%':<8}")
        print("─" * 85)
        
        for sector in sector_metrics:
            print(f"{sector['sector']:<20} │ {sector['trades']:<6} │ {sector['wins']:<5} │ "
                  f"{sector['win_rate']:<6.1f} │ {sector['avg_return']:<+8.2f} │ "
                  f"{sector['best_trade']:<+8.2f} │ {sector['worst_trade']:<+8.2f}")
        
        print("="*85)
    
    def generate_all_tables(self):
        """Generate all formatted tables"""
        print("🔍 Loading 6-Month Backtest Results...")
        results = self.load_latest_results()
        
        if not results:
            return
        
        # Generate all tables
        self.generate_summary_table(results)
        self.generate_monthly_table(results)
        self.generate_top_stocks_table(results, 15)
        self.generate_worst_stocks_table(results, 10)
        self.generate_sector_analysis_table(results)
        self.generate_position_sizing_table()
        
        print(f"\n✅ All tables generated successfully!")
        print(f"📊 Based on {results['overall_performance']['total_trades']} trades over 6 months")
        print(f"🏆 Overall win rate: {results['overall_performance']['win_rate']:.1f}%")

def main():
    """Generate formatted tables from backtest results"""
    generator = BacktestTableGenerator()
    generator.generate_all_tables()

if __name__ == "__main__":
    main()
