#!/usr/bin/env python3
"""
Daily Stock Picker - Advanced A+ Grade System
Generate stock picks for today (default) or any specific date
Professional swing trading system with date flexibility
"""

import pandas as pd
import yfinance as yf
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

class DailyStockPicker:
    """Advanced daily stock picker with date flexibility"""
    
    def __init__(self):
        """Initialize with A+ grade parameters"""
        # A+ Grade Trading Parameters
        self.stop_loss_pct = 0.06  # 6% stop loss
        self.take_profit_pct = 0.20  # 20% take profit
        self.trailing_stop_pct = 0.035  # 3.5% trailing stop
        self.risk_per_trade = 0.02  # 2% risk per trade
        self.min_signal_strength = 75  # 75% minimum strength
        
        # Premium stock universe
        self.premium_stocks = [
            # Top Banking Stocks
            'HDFCBANK.NS', 'ICICIBANK.NS', 'KOTAKBANK.NS', 'AXISBANK.NS', 'SBIN.NS',
            'BAJFINANCE.NS', 'BAJAJFINSV.NS', 'INDUSINDBK.NS', 'AUBANK.NS', 'FEDERALBNK.NS',
            
            # Leading IT Stocks
            'TCS.NS', 'INFY.NS', 'HCLTECH.NS', 'WIPRO.NS', 'TECHM.NS',
            'LTIM.NS', 'MPHASIS.NS', 'COFORGE.NS', 'PERSISTENT.NS', 'LTTS.NS',
            
            # Energy & Commodity Leaders
            'RELIANCE.NS', 'ONGC.NS', 'IOC.NS', 'BPCL.NS', 'TATASTEEL.NS',
            'JSWSTEEL.NS', 'HINDALCO.NS', 'VEDL.NS', 'COALINDIA.NS', 'POWERGRID.NS',
            
            # Pharma Leaders
            'SUNPHARMA.NS', 'DRREDDY.NS', 'CIPLA.NS', 'DIVISLAB.NS', 'BIOCON.NS',
            'LUPIN.NS', 'TORNTPHARM.NS', 'APOLLOHOSP.NS', 'FORTIS.NS', 'LALPATHLAB.NS',
            
            # FMCG Leaders
            'HINDUNILVR.NS', 'ITC.NS', 'NESTLEIND.NS', 'BRITANNIA.NS', 'MARICO.NS',
            'DABUR.NS', 'GODREJCP.NS', 'TATACONSUM.NS', 'JUBLFOOD.NS', 'TRENT.NS',
            
            # Auto Sector
            'MARUTI.NS', 'TATAMOTORS.NS', 'M&M.NS', 'BAJAJ-AUTO.NS', 'HEROMOTOCO.NS',
            'EICHERMOT.NS', 'ASHOKLEY.NS', 'MRF.NS', 'APOLLOTYRE.NS', 'ESCORTS.NS',
            
            # Infrastructure & Specialty
            'LT.NS', 'BHARTIARTL.NS', 'ULTRACEMCO.NS', 'SHREECEM.NS', 'GRASIM.NS',
            'INDIGO.NS', 'DMART.NS', 'MOIL.NS', 'INDIACEM.NS', 'TATACHEM.NS',
            'NATIONALUM.NS', 'CLEAN.NS', 'GLAXO.NS', 'EICHERMOT.NS', 'RPOWER.NS'
        ]
    
    def calculate_indicators(self, data: pd.DataFrame) -> Dict:
        """Calculate comprehensive technical indicators"""
        if len(data) < 50:
            return {}
        
        indicators = {}
        
        try:
            # RSI Calculation
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
            indicators['macd_histogram'] = indicators['macd'] - indicators['macd_signal']
            
            # Bollinger Bands
            sma_20 = indicators['sma_20']
            std_20 = data['Close'].rolling(20).std()
            indicators['bb_upper'] = sma_20 + (std_20 * 2)
            indicators['bb_lower'] = sma_20 - (std_20 * 2)
            
            # Volume Analysis
            indicators['volume_sma'] = data['Volume'].rolling(20).mean()
            
        except Exception as e:
            pass
        
        return indicators
    
    def analyze_stock(self, symbol: str, analysis_date: datetime) -> Optional[Dict]:
        """Analyze stock for specific date"""
        try:
            # Calculate date range
            end_date = analysis_date + timedelta(days=3)
            start_date = analysis_date - timedelta(days=180)
            
            # Fetch data
            ticker = yf.Ticker(symbol)
            data = ticker.history(start=start_date, end=end_date, interval="1d")
            
            if data.empty or len(data) < 50:
                return None
            
            # Find analysis date in data
            analysis_idx = None
            for i, date in enumerate(data.index):
                if date.date() <= analysis_date.date():
                    analysis_idx = i
                else:
                    break
            
            if analysis_idx is None or analysis_idx < 25:
                return None
            
            # Use data up to analysis date
            historical_data = data.iloc[:analysis_idx + 1]
            
            # Calculate indicators
            indicators = self.calculate_indicators(historical_data)
            if not indicators:
                return None
            
            # Current values
            current_price = historical_data['Close'].iloc[-1]
            current_volume = historical_data['Volume'].iloc[-1]
            previous_close = historical_data['Close'].iloc[-2] if len(historical_data) > 1 else current_price
            
            # Performance calculations
            price_change_1d = ((current_price - previous_close) / previous_close * 100)
            
            # 5-day performance
            if len(historical_data) >= 6:
                price_5d_ago = historical_data['Close'].iloc[-6]
                price_change_5d = ((current_price - price_5d_ago) / price_5d_ago * 100)
            else:
                price_change_5d = 0
            
            # 20-day performance
            if len(historical_data) >= 21:
                price_20d_ago = historical_data['Close'].iloc[-21]
                price_change_20d = ((current_price - price_20d_ago) / price_20d_ago * 100)
            else:
                price_change_20d = 0
            
            # Get indicator values
            rsi = indicators['rsi'].iloc[-1] if len(indicators['rsi']) > 0 else 50
            macd = indicators['macd'].iloc[-1] if len(indicators['macd']) > 0 else 0
            macd_signal = indicators['macd_signal'].iloc[-1] if len(indicators['macd_signal']) > 0 else 0
            
            bb_upper = indicators['bb_upper'].iloc[-1] if len(indicators['bb_upper']) > 0 else current_price * 1.05
            bb_lower = indicators['bb_lower'].iloc[-1] if len(indicators['bb_lower']) > 0 else current_price * 0.95
            
            sma_20 = indicators['sma_20'].iloc[-1] if len(indicators['sma_20']) > 0 else current_price
            sma_50 = indicators['sma_50'].iloc[-1] if len(indicators['sma_50']) > 0 else current_price
            
            volume_avg = indicators['volume_sma'].iloc[-1] if len(indicators['volume_sma']) > 0 else current_volume
            volume_ratio = current_volume / volume_avg if volume_avg > 0 else 1
            
            # Signal generation
            signals = []
            score = 0
            
            # RSI Analysis
            if rsi <= 25:
                signals.append("RSI Extreme Oversold")
                score += 3
            elif 25 < rsi <= 35:
                signals.append("RSI Oversold")
                score += 2
            elif rsi >= 75:
                signals.append("RSI Extreme Overbought")
                score -= 2
            elif 65 <= rsi < 75:
                signals.append("RSI Overbought")
                score -= 1
            
            # MACD Analysis
            if len(indicators['macd']) > 1:
                macd_prev = indicators['macd'].iloc[-2]
                macd_signal_prev = indicators['macd_signal'].iloc[-2]
                
                if macd > macd_signal and macd_prev <= macd_signal_prev:
                    signals.append("MACD Fresh Bull Cross")
                    score += 3
                elif macd < macd_signal and macd_prev >= macd_signal_prev:
                    signals.append("MACD Bear Cross")
                    score -= 2
                elif macd > macd_signal:
                    signals.append("MACD Bullish")
                    score += 1
            
            # Moving Average Analysis
            if current_price > sma_20 > sma_50:
                signals.append("Perfect MA Stack")
                score += 2
            elif current_price > sma_20:
                signals.append("Above SMA 20")
                score += 1
            elif current_price < sma_20 < sma_50:
                signals.append("Below MA Stack")
                score -= 2
            
            # Bollinger Bands
            bb_position = (current_price - bb_lower) / (bb_upper - bb_lower)
            if bb_position <= 0.1:
                signals.append("BB Extreme Oversold")
                score += 2
            elif bb_position >= 0.9:
                signals.append("BB Extreme Overbought")
                score -= 2
            
            # Volume Analysis
            if volume_ratio >= 2.0:
                signals.append(f"High Volume ({volume_ratio:.1f}x)")
                score += 2
            elif volume_ratio >= 1.5:
                signals.append(f"Above Avg Volume ({volume_ratio:.1f}x)")
                score += 1
            elif volume_ratio < 0.5:
                signals.append("Low Volume")
                score -= 1
            
            # Price momentum
            if price_change_1d >= 3:
                signals.append(f"Strong Up Move (+{price_change_1d:.1f}%)")
                score += 1
            elif price_change_1d <= -3:
                signals.append(f"Strong Down Move ({price_change_1d:.1f}%)")
                score += 1
            
            # Calculate strength
            max_score = 12
            strength = min(100, max(0, int((score + 6) / max_score * 100)))
            
            # Determine direction
            if score >= 3:
                direction = "STRONG BUY"
            elif score >= 1:
                direction = "BUY"
            elif score <= -3:
                direction = "STRONG SELL"
            elif score <= -1:
                direction = "SELL"
            else:
                direction = "NEUTRAL"
            
            # Only return if meets minimum criteria
            if strength >= self.min_signal_strength and abs(score) >= 1:
                return {
                    'symbol': symbol,
                    'analysis_date': analysis_date.strftime('%Y-%m-%d'),
                    'price': current_price,
                    'direction': direction,
                    'strength': strength,
                    'score': score,
                    'signals': signals,
                    'rsi': rsi,
                    'volume_ratio': volume_ratio,
                    'price_change_1d': price_change_1d,
                    'price_change_5d': price_change_5d,
                    'price_change_20d': price_change_20d,
                    'stop_loss': current_price * (1 - self.stop_loss_pct),
                    'take_profit': current_price * (1 + self.take_profit_pct),
                    'trailing_stop': current_price * (1 - self.trailing_stop_pct)
                }
            
            return None
            
        except Exception as e:
            return None
    
    def scan_for_date(self, analysis_date: datetime = None) -> List[Dict]:
        """Scan all stocks for specific date (default: today)"""
        if analysis_date is None:
            analysis_date = datetime.now()
        
        print(f"🚀 DAILY STOCK PICKER - A+ GRADE SYSTEM")
        print("=" * 80)
        print(f"📅 Analysis Date: {analysis_date.strftime('%Y-%m-%d %A')}")
        print(f"🎯 Target: A+ Grade Opportunities (75%+ strength)")
        print(f"📊 Universe: {len(self.premium_stocks)} Premium Stocks")
        print(f"🛡️ Risk Management: 6% SL | 20% TP | 3.5% Trailing")
        print("=" * 80)
        
        opportunities = []
        
        for i, symbol in enumerate(self.premium_stocks, 1):
            if i % 10 == 0:
                print(f"📊 Progress: {i}/{len(self.premium_stocks)} stocks analyzed... Found: {len(opportunities)} opportunities")
            
            result = self.analyze_stock(symbol, analysis_date)
            if result:
                opportunities.append(result)
        
        print(f"✅ Scan Complete: {len(opportunities)} opportunities found from {len(self.premium_stocks)} stocks")
        
        return opportunities
    
    def display_results(self, opportunities: List[Dict], analysis_date: datetime):
        """Display comprehensive results"""
        if not opportunities:
            print(f"\n❌ No A+ opportunities found for {analysis_date.strftime('%Y-%m-%d')}")
            return
        
        # Sort by strength
        sorted_opportunities = sorted(opportunities, key=lambda x: x['strength'], reverse=True)
        
        # Categorize by direction
        strong_buys = [opp for opp in sorted_opportunities if opp['direction'] == 'STRONG BUY']
        buys = [opp for opp in sorted_opportunities if opp['direction'] == 'BUY']
        strong_sells = [opp for opp in sorted_opportunities if opp['direction'] == 'STRONG SELL']
        sells = [opp for opp in sorted_opportunities if opp['direction'] == 'SELL']
        
        print(f"\n🏆 A+ OPPORTUNITIES FOR {analysis_date.strftime('%Y-%m-%d %A')}")
        print("=" * 100)
        print(f"🚀 STRONG BUY: {len(strong_buys)} stocks")
        print(f"📈 BUY: {len(buys)} stocks")
        print(f"📉 SELL: {len(sells)} stocks")
        print(f"🔻 STRONG SELL: {len(strong_sells)} stocks")
        
        print(f"\n🎯 TOP OPPORTUNITIES:")
        print("-" * 120)
        print(f"{'RANK':<4} {'SYMBOL':<12} {'SIGNAL':<12} {'STR%':<5} {'1D%':<8} {'5D%':<8} {'20D%':<8} {'RSI':<6} {'VOL':<6} {'KEY SIGNALS'}")
        print("-" * 120)
        
        for i, opp in enumerate(sorted_opportunities[:15], 1):
            direction_emoji = "🚀" if opp['direction'] == 'STRONG BUY' else "📈" if opp['direction'] == 'BUY' else "📉" if opp['direction'] == 'SELL' else "🔻"
            signals_text = ', '.join(opp['signals'][:2])
            
            print(f"{i:<4} {opp['symbol']:<12} {direction_emoji}{opp['direction']:<11} {opp['strength']:<5} "
                  f"{opp['price_change_1d']:<+8.1f} {opp['price_change_5d']:<+8.1f} {opp['price_change_20d']:<+8.1f} "
                  f"{opp['rsi']:<6.1f} {opp['volume_ratio']:<6.1f} {signals_text}")
        
        # Detailed analysis for top 5
        print(f"\n🔍 TOP 5 DETAILED ANALYSIS:")
        print("=" * 100)
        
        for i, opp in enumerate(sorted_opportunities[:5], 1):
            signals_text = ', '.join(opp['signals'])
            
            print(f"\n{i}. {opp['symbol']} - {opp['direction']} (Strength: {opp['strength']}%)")
            print(f"   💰 Price: ₹{opp['price']:.2f}")
            print(f"   📊 Performance: 1D: {opp['price_change_1d']:+.1f}% | 5D: {opp['price_change_5d']:+.1f}% | 20D: {opp['price_change_20d']:+.1f}%")
            print(f"   📈 RSI: {opp['rsi']:.1f} | Volume: {opp['volume_ratio']:.1f}x average")
            print(f"   🎯 Signals: {signals_text}")
            print(f"   💡 Setup: Entry: ₹{opp['price']:.2f} | SL: ₹{opp['stop_loss']:.2f} | TP: ₹{opp['take_profit']:.2f} | Trailing: ₹{opp['trailing_stop']:.2f}")
        
        # Summary insights
        total_bullish = len(strong_buys) + len(buys)
        total_bearish = len(strong_sells) + len(sells)
        
        print(f"\n📋 MARKET INSIGHTS FOR {analysis_date.strftime('%Y-%m-%d')}:")
        print("-" * 60)
        print(f"🟢 Bullish Opportunities: {total_bullish} ({total_bullish/len(opportunities)*100:.1f}%)")
        print(f"🔴 Bearish Opportunities: {total_bearish} ({total_bearish/len(opportunities)*100:.1f}%)")
        
        # Sector analysis
        sectors = {}
        for opp in opportunities:
            symbol = opp['symbol'].replace('.NS', '')
            if 'BANK' in symbol or symbol in ['HDFC', 'ICICI', 'KOTAK', 'AXIS', 'SBIN', 'BAJFINANCE', 'AUBANK']:
                sector = 'Banking'
            elif symbol in ['TCS', 'INFY', 'HCLTECH', 'WIPRO', 'TECHM']:
                sector = 'IT'
            elif symbol in ['RELIANCE', 'ONGC', 'IOC', 'BPCL']:
                sector = 'Energy'
            elif symbol in ['SUNPHARMA', 'DRREDDY', 'CIPLA', 'DIVISLAB']:
                sector = 'Pharma'
            else:
                sector = 'Others'
            
            if sector not in sectors:
                sectors[sector] = 0
            sectors[sector] += 1
        
        print(f"\n🏢 SECTOR BREAKDOWN:")
        for sector, count in sorted(sectors.items(), key=lambda x: x[1], reverse=True):
            print(f"   {sector}: {count} opportunities")

def main():
    """Main execution with date selection"""
    picker = DailyStockPicker()
    
    print("📊 Welcome to Daily Stock Picker!")
    print("1. Today's stock picks (default)")
    print("2. Specific date analysis")
    
    choice = input("\nEnter your choice (1 or 2, press Enter for default): ").strip()
    
    analysis_date = None
    
    if choice == "2":
        date_input = input("Enter date (YYYY-MM-DD format, e.g., 2025-07-15): ").strip()
        try:
            analysis_date = datetime.strptime(date_input, '%Y-%m-%d')
        except ValueError:
            print("❌ Invalid date format. Using today's date.")
            analysis_date = datetime.now()
    else:
        analysis_date = datetime.now()
    
    # Run analysis
    opportunities = picker.scan_for_date(analysis_date)
    picker.display_results(opportunities, analysis_date)
    
    print(f"\n✅ Analysis Complete - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
