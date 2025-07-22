#!/usr/bin/env python3
"""
Monthly Profit Grade System - Optimized for 10-12% Monthly Returns
Professional swing trading system with enhanced profit targeting
"""

import pandas as pd
import yfinance as yf
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import warnings
warnings.filterwarnings('ignore')

@dataclass
class MonthlyProfitConfig:
    """Configuration for monthly profit optimization"""
    # Monthly Profit Targets
    target_monthly_return: float = 0.11  # 11% monthly target
    min_monthly_return: float = 0.10     # 10% minimum acceptable
    max_monthly_return: float = 0.12     # 12% stretch target
    
    # Enhanced Risk Management for Monthly Profits
    risk_per_trade: float = 0.025        # 2.5% risk per trade (aggressive but controlled)
    max_positions: int = 6               # 6 concurrent positions for diversification
    min_signal_strength: int = 85        # 85%+ signal strength required
    
    # Optimized Profit Parameters
    take_profit_fast: float = 0.12       # 12% quick profit (faster turnover)
    take_profit_momentum: float = 0.18   # 18% for momentum stocks
    take_profit_breakout: float = 0.25   # 25% for breakout stocks
    stop_loss_tight: float = 0.04        # 4% stop loss (tighter control)
    trailing_stop_aggressive: float = 0.02 # 2% trailing stop (lock profits faster)
    
    # Enhanced Signal Quality
    volume_threshold: float = 2.5        # 2.5x volume requirement
    rsi_oversold: int = 15               # Extreme oversold (15)
    rsi_overbought: int = 85             # Extreme overbought (85)
    momentum_threshold: float = 0.05     # 5% minimum momentum required
    breakout_threshold: float = 0.08     # 8% breakout confirmation
    
    # Monthly Performance Grading
    grade_thresholds = {
        'S+': 0.15,  # 15%+ monthly = S+ LEGENDARY
        'S':  0.12,  # 12%+ monthly = S EXCEPTIONAL  
        'A+': 0.11,  # 11%+ monthly = A+ EXCELLENT
        'A':  0.10,  # 10%+ monthly = A GREAT
        'B+': 0.08,  # 8%+ monthly = B+ GOOD
        'B':  0.06,  # 6%+ monthly = B AVERAGE
        'C':  0.04,  # 4%+ monthly = C POOR
        'F':  0.00   # <4% monthly = F FAIL
    }

class MonthlyProfitAnalyzer:
    """Advanced analyzer for monthly profit optimization"""
    
    def __init__(self, config: MonthlyProfitConfig = None):
        self.config = config or MonthlyProfitConfig()
        self.liquid_stocks = self._get_premium_stocks()
        
    def _get_premium_stocks(self) -> List[str]:
        """Get premium high-liquidity stocks optimized for monthly profits"""
        # Focus on stocks with high volatility and liquidity for monthly profits
        premium_stocks = [
            # High Beta Financial Stocks (Volatile but profitable)
            'HDFCBANK.NS', 'ICICIBANK.NS', 'KOTAKBANK.NS', 'AXISBANK.NS', 'SBIN.NS',
            'BAJFINANCE.NS', 'BAJAJFINSV.NS', 'INDUSINDBK.NS', 'FEDERALBNK.NS', 'AUBANK.NS',
            'RBLBANK.NS', 'BANDHANBNK.NS', 'YESBANK.NS', 'IDFCFIRSTB.NS', 'MUTHOOTFIN.NS',
            
            # High Momentum IT Stocks
            'TCS.NS', 'INFY.NS', 'HCLTECH.NS', 'WIPRO.NS', 'TECHM.NS',
            'LTIM.NS', 'MPHASIS.NS', 'COFORGE.NS', 'PERSISTENT.NS', 'LTTS.NS',
            'TATAELXSI.NS', 'MINDTREE.NS', 'HAPPSTMNDS.NS', 'INTELLECT.NS', 'NEWGEN.NS',
            
            # Volatile Pharma Stocks (High profit potential)
            'SUNPHARMA.NS', 'DRREDDY.NS', 'CIPLA.NS', 'DIVISLAB.NS', 'BIOCON.NS',
            'LUPIN.NS', 'TORNTPHARM.NS', 'GLENMARK.NS', 'ALKEM.NS', 'LALPATHLAB.NS',
            'APOLLOHOSP.NS', 'FORTIS.NS', 'SYNGENE.NS', 'GRANULES.NS', 'AJANTPHARM.NS',
            
            # High Beta Energy & Commodity Stocks
            'RELIANCE.NS', 'ONGC.NS', 'IOC.NS', 'BPCL.NS', 'ADANIGREEN.NS',
            'ADANIPORTS.NS', 'ADANIENT.NS', 'ADANIPOWER.NS', 'TATASTEEL.NS', 'JSWSTEEL.NS',
            'HINDALCO.NS', 'VEDL.NS', 'COALINDIA.NS', 'POWERGRID.NS', 'NTPC.NS',
            
            # Momentum FMCG Stocks
            'HINDUNILVR.NS', 'ITC.NS', 'NESTLEIND.NS', 'BRITANNIA.NS', 'MARICO.NS',
            'DABUR.NS', 'GODREJCP.NS', 'TATACONSUM.NS', 'JUBLFOOD.NS', 'TRENT.NS',
            
            # High Volatility Auto Stocks
            'MARUTI.NS', 'TATAMOTORS.NS', 'M&M.NS', 'BAJAJ-AUTO.NS', 'HEROMOTOCO.NS',
            'EICHERMOT.NS', 'ASHOKLEY.NS', 'MRF.NS', 'APOLLOTYRE.NS', 'ESCORTS.NS',
            
            # Momentum Infrastructure Stocks
            'LT.NS', 'BHARTIARTL.NS', 'ULTRACEMCO.NS', 'SHREECEM.NS', 'GRASIM.NS',
            'HAL.NS', 'BEL.NS', 'BHEL.NS', 'CONCOR.NS', 'IRCTC.NS',
            
            # High Beta Specialty Stocks
            'INDIGO.NS', 'ZOMATO.NS', 'PAYTM.NS', 'NYKAA.NS', 'DMART.NS',
            'RAYMOND.NS', 'BLUEDART.NS', 'MOIL.NS', 'GABRIEL.NS', 'DELTACORP.NS'
        ]
        
        return list(set(premium_stocks))
    
    def calculate_advanced_indicators(self, data: pd.DataFrame) -> Dict:
        """Calculate advanced technical indicators for monthly profit optimization"""
        if len(data) < 50:
            return {}
        
        indicators = {}
        
        try:
            # Enhanced RSI with multiple timeframes
            delta = data['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            indicators['rsi_14'] = 100 - (100 / (1 + rs))
            
            # Faster RSI for quicker signals
            gain_9 = (delta.where(delta > 0, 0)).rolling(window=9).mean()
            loss_9 = (-delta.where(delta < 0, 0)).rolling(window=9).mean()
            rs_9 = gain_9 / loss_9
            indicators['rsi_9'] = 100 - (100 / (1 + rs_9))
            
            # Multiple Moving Averages for trend confirmation
            indicators['ema_8'] = data['Close'].ewm(span=8).mean()
            indicators['ema_21'] = data['Close'].ewm(span=21).mean()
            indicators['ema_50'] = data['Close'].ewm(span=50).mean()
            indicators['sma_20'] = data['Close'].rolling(20).mean()
            
            # Advanced MACD with signal optimization
            ema_12 = data['Close'].ewm(span=12).mean()
            ema_26 = data['Close'].ewm(span=26).mean()
            indicators['macd'] = ema_12 - ema_26
            indicators['macd_signal'] = indicators['macd'].ewm(span=9).mean()
            indicators['macd_histogram'] = indicators['macd'] - indicators['macd_signal']
            
            # Bollinger Bands with squeeze detection
            sma_20 = indicators['sma_20']
            std_20 = data['Close'].rolling(20).std()
            indicators['bb_upper'] = sma_20 + (std_20 * 2)
            indicators['bb_lower'] = sma_20 - (std_20 * 2)
            indicators['bb_squeeze'] = (indicators['bb_upper'] - indicators['bb_lower']) / sma_20
            
            # Volume indicators
            indicators['volume_sma'] = data['Volume'].rolling(20).mean()
            indicators['volume_ratio'] = data['Volume'] / indicators['volume_sma']
            
            # Price momentum indicators
            indicators['momentum_5'] = (data['Close'] / data['Close'].shift(5) - 1) * 100
            indicators['momentum_10'] = (data['Close'] / data['Close'].shift(10) - 1) * 100
            indicators['momentum_20'] = (data['Close'] / data['Close'].shift(20) - 1) * 100
            
            # Volatility indicator (ATR)
            high_low = data['High'] - data['Low']
            high_close = np.abs(data['High'] - data['Close'].shift())
            low_close = np.abs(data['Low'] - data['Close'].shift())
            ranges = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            indicators['atr'] = ranges.rolling(14).mean()
            
            # Support/Resistance levels
            indicators['resistance'] = data['High'].rolling(20).max()
            indicators['support'] = data['Low'].rolling(20).min()
            
        except Exception as e:
            print(f"⚠️ Error calculating indicators: {e}")
        
        return indicators
    
    def analyze_monthly_profit_potential(self, symbol: str) -> Optional[Dict]:
        """Analyze stock for monthly profit potential"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="6mo", interval="1d")
            
            if data.empty or len(data) < 50:
                return None
            
            indicators = self.calculate_advanced_indicators(data)
            if not indicators:
                return None
            
            current_price = data['Close'].iloc[-1]
            current_volume = data['Volume'].iloc[-1]
            
            # Monthly profit scoring system
            signals = []
            score = 0
            profit_category = "STANDARD"
            
            # Enhanced RSI Analysis (Multiple timeframes)
            rsi_14 = indicators['rsi_14'].iloc[-1] if 'rsi_14' in indicators else 50
            rsi_9 = indicators['rsi_9'].iloc[-1] if 'rsi_9' in indicators else 50
            
            if rsi_14 <= self.config.rsi_oversold or rsi_9 <= self.config.rsi_oversold:
                signals.append("EXTREME OVERSOLD")
                score += 4
                profit_category = "BREAKOUT"
            elif rsi_14 >= self.config.rsi_overbought or rsi_9 >= self.config.rsi_overbought:
                signals.append("EXTREME OVERBOUGHT")
                score -= 4
            elif 15 < rsi_14 <= 25:
                signals.append("STRONG BULLISH ZONE")
                score += 3
                profit_category = "MOMENTUM"
            elif 75 <= rsi_14 < 85:
                signals.append("STRONG BEARISH ZONE")
                score -= 3
            
            # Advanced MACD Analysis
            if 'macd' in indicators and 'macd_signal' in indicators:
                macd = indicators['macd'].iloc[-1]
                macd_signal = indicators['macd_signal'].iloc[-1]
                macd_hist = indicators['macd_histogram'].iloc[-1]
                
                if len(indicators['macd']) > 1:
                    macd_prev = indicators['macd'].iloc[-2]
                    macd_signal_prev = indicators['macd_signal'].iloc[-2]
                    
                    # Fresh bullish crossover
                    if macd > macd_signal and macd_prev <= macd_signal_prev:
                        if macd > 0:
                            signals.append("MACD POWER BULL CROSS")
                            score += 4
                            profit_category = "BREAKOUT"
                        else:
                            signals.append("MACD BULL CROSS")
                            score += 3
                    
                    # MACD momentum
                    if macd_hist > 0 and macd_hist > indicators['macd_histogram'].iloc[-2]:
                        signals.append("MACD MOMENTUM+")
                        score += 2
            
            # Multi-timeframe Moving Average Analysis
            if all(key in indicators for key in ['ema_8', 'ema_21', 'ema_50']):
                ema_8 = indicators['ema_8'].iloc[-1]
                ema_21 = indicators['ema_21'].iloc[-1]
                ema_50 = indicators['ema_50'].iloc[-1]
                
                # Perfect trend alignment
                if current_price > ema_8 > ema_21 > ema_50:
                    signals.append("PERFECT TREND STACK")
                    score += 4
                    profit_category = "BREAKOUT"
                elif current_price > ema_8 > ema_21:
                    signals.append("STRONG UPTREND")
                    score += 3
                elif current_price < ema_8 < ema_21 < ema_50:
                    signals.append("PERFECT DOWNTREND")
                    score -= 4
            
            # Volume Explosion Analysis
            if 'volume_ratio' in indicators:
                vol_ratio = indicators['volume_ratio'].iloc[-1]
                
                if vol_ratio >= self.config.volume_threshold:
                    if vol_ratio >= 5.0:
                        signals.append(f"VOLUME EXPLOSION ({vol_ratio:.1f}x)")
                        score += 4
                        profit_category = "BREAKOUT"
                    elif vol_ratio >= 3.0:
                        signals.append(f"HIGH VOLUME SURGE ({vol_ratio:.1f}x)")
                        score += 3
                    else:
                        signals.append(f"VOLUME INCREASE ({vol_ratio:.1f}x)")
                        score += 2
                elif vol_ratio < 0.5:
                    signals.append("LOW VOLUME")
                    score -= 2
            
            # Momentum Analysis
            if 'momentum_5' in indicators and 'momentum_10' in indicators:
                mom_5 = indicators['momentum_5'].iloc[-1]
                mom_10 = indicators['momentum_10'].iloc[-1]
                mom_20 = indicators['momentum_20'].iloc[-1]
                
                if mom_5 >= self.config.breakout_threshold * 100:  # 8%+ in 5 days
                    signals.append(f"BREAKOUT MOMENTUM ({mom_5:.1f}%)")
                    score += 4
                    profit_category = "BREAKOUT"
                elif mom_5 >= self.config.momentum_threshold * 100:  # 5%+ in 5 days
                    signals.append(f"STRONG MOMENTUM ({mom_5:.1f}%)")
                    score += 3
                    if profit_category == "STANDARD":
                        profit_category = "MOMENTUM"
                
                # Accelerating momentum
                if mom_5 > mom_10 > mom_20 and all(m > 0 for m in [mom_5, mom_10, mom_20]):
                    signals.append("ACCELERATING MOMENTUM")
                    score += 2
            
            # Bollinger Band Analysis
            if all(key in indicators for key in ['bb_upper', 'bb_lower', 'bb_squeeze']):
                bb_upper = indicators['bb_upper'].iloc[-1]
                bb_lower = indicators['bb_lower'].iloc[-1]
                bb_squeeze = indicators['bb_squeeze'].iloc[-1]
                
                bb_position = (current_price - bb_lower) / (bb_upper - bb_lower)
                
                if bb_position <= 0.05:  # Extreme oversold
                    signals.append("BB EXTREME OVERSOLD")
                    score += 3
                elif bb_position >= 0.95:  # Extreme overbought
                    signals.append("BB EXTREME OVERBOUGHT")
                    score -= 3
                elif bb_position >= 0.8 and bb_squeeze < 0.1:  # Squeeze breakout
                    signals.append("BB SQUEEZE BREAKOUT")
                    score += 3
                    profit_category = "BREAKOUT"
            
            # Support/Resistance Breakout
            if 'resistance' in indicators and 'support' in indicators:
                resistance = indicators['resistance'].iloc[-1]
                support = indicators['support'].iloc[-1]
                
                # Resistance breakout
                if current_price > resistance * 1.02:  # 2% above resistance
                    signals.append("RESISTANCE BREAKOUT")
                    score += 3
                    profit_category = "BREAKOUT"
                # Support bounce
                elif current_price < support * 1.02:  # Near support
                    signals.append("SUPPORT BOUNCE SETUP")
                    score += 2
            
            # Calculate signal strength
            strength = min(100, max(0, int((score + 6) / 12 * 100)))
            
            # Apply minimum signal strength filter
            if strength < self.config.min_signal_strength:
                return None
            
            # Determine direction and profit target
            if score >= 6:
                direction = "SUPER BUY"
                target_profit = self.config.take_profit_breakout
            elif score >= 4:
                direction = "STRONG BUY"
                target_profit = self.config.take_profit_momentum
            elif score >= 2:
                direction = "BUY"
                target_profit = self.config.take_profit_fast
            elif score <= -6:
                direction = "SUPER SELL"
                target_profit = 0
            elif score <= -4:
                direction = "STRONG SELL"
                target_profit = 0
            elif score <= -2:
                direction = "SELL"
                target_profit = 0
            else:
                return None  # Not strong enough signal
            
            # Calculate price changes
            price_1d = ((current_price / data['Close'].iloc[-2]) - 1) * 100 if len(data) >= 2 else 0
            price_5d = ((current_price / data['Close'].iloc[-6]) - 1) * 100 if len(data) >= 6 else 0
            price_20d = ((current_price / data['Close'].iloc[-21]) - 1) * 100 if len(data) >= 21 else 0
            
            # Calculate trading levels
            if direction in ["SUPER BUY", "STRONG BUY", "BUY"]:
                entry_price = current_price
                stop_loss = entry_price * (1 - self.config.stop_loss_tight)
                take_profit = entry_price * (1 + target_profit)
                trailing_stop = entry_price * (1 - self.config.trailing_stop_aggressive)
                
                # Risk-reward ratio
                risk = (entry_price - stop_loss) / entry_price
                reward = (take_profit - entry_price) / entry_price
                risk_reward_ratio = reward / risk if risk > 0 else 0
            else:
                entry_price = stop_loss = take_profit = trailing_stop = risk_reward_ratio = 0
            
            return {
                'symbol': symbol,
                'name': symbol.replace('.NS', ''),
                'direction': direction,
                'strength': strength,
                'profit_category': profit_category,
                'signals': signals,
                'rsi_14': rsi_14,
                'rsi_9': rsi_9,
                'current_price': current_price,
                'price_change_1d': price_1d,
                'price_change_5d': price_5d,
                'price_change_20d': price_20d,
                'volume_ratio': indicators.get('volume_ratio', pd.Series([1])).iloc[-1],
                'score': score,
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'trailing_stop': trailing_stop,
                'target_profit_pct': target_profit * 100,
                'risk_reward_ratio': risk_reward_ratio,
                'monthly_profit_potential': self._estimate_monthly_potential(score, strength, profit_category)
            }
            
        except Exception as e:
            print(f"⚠️ Error analyzing {symbol}: {str(e)}")
            return None
    
    def _estimate_monthly_potential(self, score: float, strength: int, category: str) -> float:
        """Estimate monthly profit potential based on analysis"""
        base_potential = 0.08  # 8% base
        
        if category == "BREAKOUT":
            base_potential = 0.15  # 15% for breakouts
        elif category == "MOMENTUM":
            base_potential = 0.12  # 12% for momentum
        
        # Adjust based on score and strength
        score_multiplier = min(1.5, max(0.5, score / 6))
        strength_multiplier = min(1.3, max(0.7, strength / 100))
        
        return base_potential * score_multiplier * strength_multiplier
    
    def scan_monthly_profit_stocks(self, max_stocks: int = 20) -> List[Dict]:
        """Scan for monthly profit optimized stocks"""
        print(f"💰 MONTHLY PROFIT OPTIMIZER - {len(self.liquid_stocks)} PREMIUM STOCKS")
        print("=" * 90)
        print(f"🎯 Target: {self.config.target_monthly_return*100:.0f}% Monthly Returns")
        print(f"⭐ Min Signal Strength: {self.config.min_signal_strength}%")
        print(f"📊 Volume Threshold: {self.config.volume_threshold}x")
        print(f"🎯 RSI Extremes: {self.config.rsi_oversold}/{self.config.rsi_overbought}")
        print(f"💡 Risk Per Trade: {self.config.risk_per_trade*100:.1f}%")
        print("=" * 90)
        
        results = []
        processed = 0
        skipped = 0
        
        for i, symbol in enumerate(self.liquid_stocks, 1):
            try:
                if i % 20 == 0:
                    print(f"📊 Progress: {i}/{len(self.liquid_stocks)} analyzed... Found: {len(results)} monthly profit opportunities")
                
                analysis = self.analyze_monthly_profit_potential(symbol)
                if analysis and analysis['direction'] in ['SUPER BUY', 'STRONG BUY', 'BUY']:
                    results.append(analysis)
                    processed += 1
                else:
                    skipped += 1
                    
            except Exception as e:
                skipped += 1
                if skipped <= 3:
                    print(f"⚠️ Skipped {symbol}: {str(e)}")
        
        print(f"✅ Scan Complete: {processed} monthly profit stocks found, {skipped} skipped")
        
        # Sort by monthly profit potential and strength
        results.sort(key=lambda x: (x['monthly_profit_potential'], x['strength']), reverse=True)
        return results[:max_stocks]
    
    def display_monthly_profit_results(self, results: List[Dict]):
        """Display monthly profit optimization results"""
        if not results:
            print("\n❌ NO MONTHLY PROFIT OPPORTUNITIES FOUND")
            print("💡 Consider adjusting criteria or checking during market hours")
            return
        
        print(f"\n💰 FOUND {len(results)} MONTHLY PROFIT OPPORTUNITIES")
        print("=" * 120)
        
        # Group by profit category
        breakout_stocks = [r for r in results if r['profit_category'] == 'BREAKOUT']
        momentum_stocks = [r for r in results if r['profit_category'] == 'MOMENTUM']
        standard_stocks = [r for r in results if r['profit_category'] == 'STANDARD']
        
        print(f"🚀 BREAKOUT (25% targets): {len(breakout_stocks)} stocks")
        print(f"📈 MOMENTUM (18% targets): {len(momentum_stocks)} stocks")
        print(f"📊 FAST PROFIT (12% targets): {len(standard_stocks)} stocks")
        
        print(f"\n🎯 TOP MONTHLY PROFIT OPPORTUNITIES:")
        print("-" * 140)
        print(f"{'RANK':<6} {'SYMBOL':<15} {'SIGNAL':<12} {'CATEGORY':<10} {'STR%':<6} {'MONTHLY%':<9} {'TARGET%':<8} {'R:R':<6} {'1D%':<7} {'5D%':<7} {'SIGNALS'}")
        print("-" * 140)
        
        for i, result in enumerate(results[:15], 1):  # Top 15
            symbol = result['symbol']
            direction = result['direction']
            category = result['profit_category']
            strength = result['strength']
            monthly_potential = result['monthly_profit_potential'] * 100
            target_profit = result['target_profit_pct']
            risk_reward = result['risk_reward_ratio']
            price_1d = result['price_change_1d']
            price_5d = result['price_change_5d']
            signals = ', '.join(result['signals'][:2])
            
            # Direction icon
            if direction == 'SUPER BUY':
                icon = "🚀"
            elif direction == 'STRONG BUY':
                icon = "💎"
            else:
                icon = "📈"
            
            print(f"{i:<6} {symbol:<15} {icon}{direction:<11} {category:<10} {strength:<6} {monthly_potential:<9.1f} {target_profit:<8.1f} {risk_reward:<6.1f} {price_1d:<+7.1f} {price_5d:<+7.1f} {signals}")
        
        # Detailed analysis for top 5
        print(f"\n🔍 TOP 5 MONTHLY PROFIT DETAILED ANALYSIS:")
        print("=" * 120)
        
        total_monthly_potential = 0
        
        for i, result in enumerate(results[:5], 1):
            monthly_pot = result['monthly_profit_potential'] * 100
            total_monthly_potential += monthly_pot
            
            print(f"\n{i}. {result['symbol']} - {result['direction']} ({result['profit_category']} STRATEGY)")
            print(f"   💰 Current Price: ₹{result['current_price']:.2f}")
            print(f"   🎯 Target Profit: {result['target_profit_pct']:.1f}% (₹{result['take_profit']:.2f})")
            print(f"   🛡️ Stop Loss: 4% (₹{result['stop_loss']:.2f})")
            print(f"   📊 Trailing Stop: 2% (₹{result['trailing_stop']:.2f})")
            print(f"   📈 Monthly Potential: {monthly_pot:.1f}%")
            print(f"   ⚡ Risk-Reward: {result['risk_reward_ratio']:.1f}:1")
            print(f"   📊 Performance: 1D: {result['price_change_1d']:+.1f}% | 5D: {result['price_change_5d']:+.1f}% | 20D: {result['price_change_20d']:+.1f}%")
            print(f"   📈 RSI: Fast: {result['rsi_9']:.1f} | Standard: {result['rsi_14']:.1f}")
            print(f"   🎯 Signals: {', '.join(result['signals'])}")
            print(f"   💡 Entry Strategy: ₹{result['entry_price']:.2f} with {self.config.risk_per_trade*100:.1f}% position size")
        
        # Portfolio simulation for monthly profits
        portfolio_analysis = self._simulate_monthly_portfolio(results[:8])  # Top 8 positions
        
        print(f"\n💼 MONTHLY PROFIT PORTFOLIO SIMULATION:")
        print("=" * 80)
        print(f"💰 Starting Capital: ₹5,00,000")
        print(f"🎯 Target Monthly Return: {self.config.target_monthly_return*100:.0f}%")
        print(f"📊 Number of Positions: {min(8, len(results))}")
        print(f"💵 Risk Per Trade: {self.config.risk_per_trade*100:.1f}%")
        print(f"📈 Expected Monthly Return: {portfolio_analysis['expected_return']:.1f}%")
        print(f"🎖️ System Grade: {portfolio_analysis['grade']}")
        print(f"🎯 Probability of 10%+ monthly: {portfolio_analysis['success_probability']:.0f}%")
        print(f"⚡ Best Case Scenario: {portfolio_analysis['best_case']:.1f}%")
        print(f"🛡️ Worst Case Scenario: {portfolio_analysis['worst_case']:.1f}%")
        
        # Monthly performance grading
        expected_return = portfolio_analysis['expected_return'] / 100
        grade = self._calculate_system_grade(expected_return)
        
        print(f"\n🎖️ MONTHLY PROFIT SYSTEM GRADE: {grade}")
        print("=" * 60)
        if grade in ['S+', 'S']:
            print("🏆 LEGENDARY PERFORMANCE - 12%+ monthly target achieved!")
        elif grade == 'A+':
            print("🥇 EXCELLENT PERFORMANCE - 11%+ monthly target achieved!")
        elif grade == 'A':
            print("🥈 GREAT PERFORMANCE - 10%+ monthly target achieved!")
        else:
            print("📈 Needs optimization to reach 10-12% monthly target")
    
    def _simulate_monthly_portfolio(self, top_stocks: List[Dict]) -> Dict:
        """Simulate portfolio performance for monthly profits"""
        if not top_stocks:
            return {'expected_return': 0, 'grade': 'F', 'success_probability': 0, 'best_case': 0, 'worst_case': 0}
        
        # Portfolio diversification (max 8 positions)
        selected_stocks = top_stocks[:min(8, len(top_stocks))]
        
        # Calculate weighted expected return
        total_weight = 0
        weighted_return = 0
        
        for stock in selected_stocks:
            weight = self.config.risk_per_trade  # Equal weighting
            return_potential = stock['monthly_profit_potential']
            weighted_return += weight * return_potential
            total_weight += weight
        
        expected_monthly_return = (weighted_return / total_weight) * 100 if total_weight > 0 else 0
        
        # Calculate success probability (achieving 10%+)
        high_potential_stocks = len([s for s in selected_stocks if s['monthly_profit_potential'] >= 0.10])
        success_probability = min(90, (high_potential_stocks / len(selected_stocks)) * 100)
        
        # Best and worst case scenarios
        best_case = max([s['monthly_profit_potential'] for s in selected_stocks]) * 100 if selected_stocks else 0
        worst_case = min([s['monthly_profit_potential'] for s in selected_stocks]) * 100 * 0.6 if selected_stocks else 0  # 60% of lowest
        
        grade = self._calculate_system_grade(expected_monthly_return / 100)
        
        return {
            'expected_return': expected_monthly_return,
            'grade': grade,
            'success_probability': success_probability,
            'best_case': best_case,
            'worst_case': worst_case
        }
    
    def _calculate_system_grade(self, monthly_return: float) -> str:
        """Calculate system grade based on monthly return"""
        for grade, threshold in self.config.grade_thresholds.items():
            if monthly_return >= threshold:
                return grade
        return 'F'

def main():
    """Main execution"""
    config = MonthlyProfitConfig()
    analyzer = MonthlyProfitAnalyzer(config)
    
    print("💰 MONTHLY PROFIT OPTIMIZATION SYSTEM")
    print("=" * 90)
    print(f"📅 Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 Target: {config.target_monthly_return*100:.0f}% Monthly Returns")
    print(f"📊 Risk Management: {config.stop_loss_tight*100:.0f}% SL | {config.take_profit_fast*100:.0f}-{config.take_profit_breakout*100:.0f}% TP")
    print(f"💼 Portfolio: {config.risk_per_trade*100:.1f}% risk per trade")
    print(f"🏆 Grade System: S+ (15%+) | S (12%+) | A+ (11%+) | A (10%+)")
    print("=" * 90)
    
    # Scan for monthly profit opportunities
    monthly_opportunities = analyzer.scan_monthly_profit_stocks(max_stocks=20)
    analyzer.display_monthly_profit_results(monthly_opportunities)
    
    print(f"\n✅ Monthly Profit Analysis Complete - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🚀 Ready for 10-12% monthly profit trading!")

if __name__ == "__main__":
    main()
