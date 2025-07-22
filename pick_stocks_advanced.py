#!/usr/bin/env python3
"""
Advanced Stock Picker - Analyze 500+ High Liquidity Indian Stocks
Professional swing trading stock picker with multiple signal strengths
"""

import os
import sys
import pandas as pd
import yfinance as yf
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from trading_system.technical_analysis import TechnicalAnalysis
from trading_system.risk_manager import RiskManager

class AdvancedStockPicker:
    def __init__(self):
        """Initialize the advanced stock picker"""
        self.technical_analysis = TechnicalAnalysis()
        self.risk_manager = RiskManager()
        self.liquid_stocks = self._get_high_liquidity_stocks()
        
    def _get_high_liquidity_stocks(self) -> List[str]:
        """Get 500+ high liquidity Indian stocks"""
        # Top liquid NSE stocks across sectors
        stocks = [
            # Banking & Financial Services
            'HDFCBANK.NS', 'ICICIBANK.NS', 'KOTAKBANK.NS', 'AXISBANK.NS', 'SBIN.NS',
            'INDUSINDBK.NS', 'BANKBARODA.NS', 'PNB.NS', 'FEDERALBNK.NS', 'IDFCFIRSTB.NS',
            'BAJFINANCE.NS', 'BAJAJFINSV.NS', 'SBILIFE.NS', 'HDFCLIFE.NS', 'ICICIPRULI.NS',
            'SBICARD.NS', 'HDFCAMC.NS', 'MUTHOOTFIN.NS', 'LICHSGFIN.NS', 'PFC.NS',
            
            # IT & Technology
            'TCS.NS', 'INFY.NS', 'HCLTECH.NS', 'WIPRO.NS', 'TECHM.NS',
            'LTI.NS', 'MINDTREE.NS', 'MPHASIS.NS', 'COFORGE.NS', 'PERSISTENT.NS',
            'LTTS.NS', 'CYIENT.NS', 'ZENTEC.NS', 'NIITTECH.NS', 'SONATSOFTW.NS',
            
            # Pharmaceuticals
            'SUNPHARMA.NS', 'DRREDDY.NS', 'CIPLA.NS', 'DIVISLAB.NS', 'BIOCON.NS',
            'CADILAHC.NS', 'LUPIN.NS', 'AUROBINDO.NS', 'TORNTPHARM.NS', 'GLENMARK.NS',
            'ALKEM.NS', 'LALPATHLAB.NS', 'APOLLOHOSP.NS', 'FORTIS.NS', 'MAXHEALTH.NS',
            
            # Energy & Oil
            'RELIANCE.NS', 'ONGC.NS', 'IOC.NS', 'BPCL.NS', 'HPCL.NS',
            'GAIL.NS', 'ADANIGREEN.NS', 'NTPC.NS', 'POWERGRID.NS', 'COALINDIA.NS',
            'TATAPOWER.NS', 'ADANITRANS.NS', 'ADANIPORTS.NS', 'JSPL.NS', 'SAIL.NS',
            
            # FMCG & Consumer
            'HINDUNILVR.NS', 'ITC.NS', 'NESTLEIND.NS', 'BRITANNIA.NS', 'MARICO.NS',
            'DABUR.NS', 'GODREJCP.NS', 'COLPAL.NS', 'PGHH.NS', 'UBL.NS',
            'TATACONSUM.NS', 'JUBLFOOD.NS', 'VBL.NS', 'EMAMILTD.NS', 'RADICO.NS',
            
            # Automobiles
            'MARUTI.NS', 'HYUNDAI.NS', 'TATAMOTORS.NS', 'M&M.NS', 'BAJAJ-AUTO.NS',
            'HEROMOTOCO.NS', 'TVSMOTORS.NS', 'EICHERMOT.NS', 'ASHOKLEY.NS', 'FORCE.NS',
            'BOSCHLTD.NS', 'MRF.NS', 'APOLLOTYRE.NS', 'CEAT.NS', 'JK.NS',
            
            # Metals & Mining
            'TATASTEEL.NS', 'JSWSTEEL.NS', 'HINDALCO.NS', 'VEDL.NS', 'NATIONALUM.NS',
            'JINDALSTEL.NS', 'NMDC.NS', 'MOIL.NS', 'HINDZINC.NS', 'RATNAMANI.NS',
            'WELCORP.NS', 'WELSPUNIND.NS', 'JSWENERGY.NS', 'ADANIENT.NS', 'GMRINFRA.NS',
            
            # Cement
            'ULTRACEMCO.NS', 'SHREECEM.NS', 'GRASIM.NS', 'ACC.NS', 'AMBUJACEMENT.NS',
            'JKCEMENT.NS', 'RAMCOCEM.NS', 'HEIDELBERG.NS', 'STARCEMENT.NS', 'PRISMCEM.NS',
            
            # Infrastructure & Construction
            'LT.NS', 'BHARTIARTL.NS', 'JSWINFRA.NS', 'IRB.NS', 'NBCC.NS',
            'NCC.NS', 'KECL.NS', 'BEML.NS', 'HAL.NS', 'COCHINSHIP.NS',
            'BEL.NS', 'BHEL.NS', 'GRINDWELL.NS', 'CUMMINSIND.NS', 'ABB.NS',
            
            # Textiles & Apparel
            'RELIANCE.NS', 'GRASIM.NS', 'VARDHMAN.NS', 'TRIDENT.NS', 'WELSPUNIND.NS',
            'RAYMOND.NS', 'ADITYADG.NS', 'RUPA.NS', 'PAGEIND.NS', 'ARVIND.NS',
            
            # Chemicals
            'UPL.NS', 'PIDILITIND.NS', 'AARTI.NS', 'GHCL.NS', 'TATACHEM.NS',
            'DEEPAKNTR.NS', 'BALRAMCHIN.NS', 'ALKYLAMINE.NS', 'NOCIL.NS', 'JUBILANT.NS',
            'SYMPHONY.NS', 'CHEMCON.NS', 'CLEAN.NS', 'DCMSHRIRAM.NS', 'FCONSUMER.NS',
            
            # Real Estate
            'DLF.NS', 'GODREJPROP.NS', 'OBEROIRLTY.NS', 'BRIGADE.NS', 'SOBHA.NS',
            'PHOENIXLTD.NS', 'MAHLIFE.NS', 'PRESTIGE.NS', 'KOLTEPATIL.NS', 'MAHINDCIE.NS',
            
            # Logistics & Transportation
            'CONCOR.NS', 'GESHIP.NS', 'SCI.NS', 'BLUEDART.NS', 'THERMAX.NS',
            'CRISIL.NS', 'INOXLEISUR.NS', 'PVR.NS', 'SPICEJET.NS', 'INDIGO.NS',
            
            # Media & Entertainment
            'ZEEL.NS', 'SUNTV.NS', 'NETWORK18.NS', 'TVTODAY.NS', 'RWORLD.NS',
            'DISHTV.NS', 'JAGRAN.NS', 'HCL-INSYS.NS', 'KPRMILL.NS', 'FIEMIND.NS',
            
            # Agriculture & Food Processing
            'BRITANNIA.NS', 'VARUN.NS', 'KRBL.NS', 'HSIL.NS', 'RELAXO.NS',
            'VMART.NS', 'SHOPRITE.NS', 'WESTLIFE.NS', 'DEVYANI.NS', 'SAPPHIRE.NS',
            
            # Power & Utilities
            'NTPC.NS', 'POWERGRID.NS', 'NHPC.NS', 'SJVN.NS', 'THERMAX.NS',
            'BHEL.NS', 'CESC.NS', 'RPOWER.NS', 'ADANIPOWER.NS', 'TORNTPOWER.NS',
            
            # Retail & E-commerce
            'AVENUE.NS', 'TRENT.NS', 'RELAXO.NS', 'BATA.NS', 'VMART.NS',
            'SHOPRITE.NS', 'FRETAIL.NS', 'SPENCERS.NS', 'MINDACORP.NS', 'CCL.NS',
            
            # Defense & Aerospace
            'HAL.NS', 'BEL.NS', 'BEML.NS', 'COCHINSHIP.NS', 'GRSE.NS',
            'MIDHANI.NS', 'ORDNANCE.NS', 'ZENTECH.NS', 'ASTRAZEN.NS', 'DYNAMATIC.NS',
            
            # Capital Goods
            'LT.NS', 'BHEL.NS', 'SIEMENS.NS', 'ABB.NS', 'CROMPTON.NS',
            'HAVELLS.NS', 'VOLTAS.NS', 'BLUESTAR.NS', 'THERMAX.NS', 'CUMMINSIND.NS',
            
            # Telecom
            'BHARTIARTL.NS', 'IDEA.NS', 'RCOM.NS', 'GTLINFRA.NS', 'RAILTEL.NS',
            'HFCL.NS', 'STERLTECH.NS', 'OPTIEMUS.NS', 'TEJAS.NS', 'ROUTE.NS',
            
            # Insurance
            'SBILIFE.NS', 'HDFCLIFE.NS', 'ICICIPRULI.NS', 'MAXLIFE.NS', 'STARHEALTH.NS',
            'NIACL.NS', 'ORIENTINS.NS', 'UIIC.NS', 'GICRE.NS', 'NEWGEN.NS',
            
            # Tourism & Hotels
            'INDHOTEL.NS', 'LEMONTREE.NS', 'MAHINDRA.NS', 'COX&KINGS.NS', 'THOMAS.NS',
            'EIHLTD.NS', 'ORIENTHOT.NS', 'MAHINDRA.NS', 'PANTALOONS.NS', 'CHALET.NS',
            
            # Education
            'APTECH.NS', 'NIIT.NS', 'NAVNEET.NS', 'CAREEREDGE.NS', 'KPIT.NS',
            'ZENSAR.NS', 'RAMKY.NS', 'EDUCOMP.NS', 'EVERONN.NS', 'TREE.NS'
        ]
        
        # Remove duplicates and return unique stocks
        return list(set(stocks))
    
    def calculate_signal_strength(self, data: pd.DataFrame) -> Dict:
        """Calculate comprehensive signal strength"""
        if len(data) < 50:
            return {'strength': 0, 'signals': [], 'direction': 'HOLD'}
        
        try:
            # Get technical indicators
            indicators = self.indicators.calculate_all_indicators(data)
            current_price = data['Close'].iloc[-1]
            
            signals = []
            bullish_score = 0
            bearish_score = 0
            
            # RSI Analysis
            rsi = indicators.get('rsi', [50])[-1] if indicators.get('rsi') is not None else 50
            if rsi < 30:
                signals.append("RSI Oversold (Bullish)")
                bullish_score += 2
            elif rsi > 70:
                signals.append("RSI Overbought (Bearish)")
                bearish_score += 2
            elif 30 <= rsi <= 45:
                signals.append("RSI Recovery Zone")
                bullish_score += 1
            elif 55 <= rsi <= 70:
                signals.append("RSI Strong Zone")
                bullish_score += 0.5
            
            # MACD Analysis
            macd_line = indicators.get('macd', [0])[-1] if indicators.get('macd') is not None else 0
            macd_signal = indicators.get('macd_signal', [0])[-1] if indicators.get('macd_signal') is not None else 0
            if macd_line > macd_signal and macd_line > 0:
                signals.append("MACD Bullish Crossover")
                bullish_score += 2
            elif macd_line < macd_signal and macd_line < 0:
                signals.append("MACD Bearish Crossover")
                bearish_score += 2
            
            # Moving Average Analysis
            sma_20 = indicators.get('sma_20', [current_price])[-1] if indicators.get('sma_20') is not None else current_price
            sma_50 = indicators.get('sma_50', [current_price])[-1] if indicators.get('sma_50') is not None else current_price
            ema_12 = indicators.get('ema_12', [current_price])[-1] if indicators.get('ema_12') is not None else current_price
            ema_26 = indicators.get('ema_26', [current_price])[-1] if indicators.get('ema_26') is not None else current_price
            
            if current_price > sma_20 > sma_50:
                signals.append("Above Key MAs")
                bullish_score += 1.5
            elif current_price < sma_20 < sma_50:
                signals.append("Below Key MAs")
                bearish_score += 1.5
            
            if ema_12 > ema_26:
                signals.append("Short EMA > Long EMA")
                bullish_score += 1
            else:
                signals.append("Short EMA < Long EMA")
                bearish_score += 1
            
            # Bollinger Bands Analysis
            bb_upper = indicators.get('bb_upper', [current_price * 1.02])[-1] if indicators.get('bb_upper') is not None else current_price * 1.02
            bb_lower = indicators.get('bb_lower', [current_price * 0.98])[-1] if indicators.get('bb_lower') is not None else current_price * 0.98
            bb_middle = indicators.get('bb_middle', [current_price])[-1] if indicators.get('bb_middle') is not None else current_price
            
            if current_price <= bb_lower:
                signals.append("BB Oversold")
                bullish_score += 1.5
            elif current_price >= bb_upper:
                signals.append("BB Overbought")
                bearish_score += 1.5
            elif current_price > bb_middle:
                signals.append("Above BB Middle")
                bullish_score += 0.5
            
            # Volume Analysis
            volume_sma = data['Volume'].rolling(20).mean().iloc[-1]
            current_volume = data['Volume'].iloc[-1]
            if current_volume > volume_sma * 1.5:
                signals.append("High Volume")
                bullish_score += 1
            
            # Price Action Analysis
            price_change_5d = (current_price / data['Close'].iloc[-6] - 1) * 100 if len(data) >= 6 else 0
            price_change_1d = (current_price / data['Close'].iloc[-2] - 1) * 100 if len(data) >= 2 else 0
            
            if price_change_1d > 2:
                signals.append(f"Strong Daily Gain: +{price_change_1d:.1f}%")
                bullish_score += 1
            elif price_change_1d < -2:
                signals.append(f"Daily Decline: {price_change_1d:.1f}%")
                bearish_score += 1
            
            # Determine overall signal
            net_score = bullish_score - bearish_score
            if net_score >= 3:
                direction = "STRONG BUY"
                strength = min(100, int((net_score / 8) * 100))
            elif net_score >= 1.5:
                direction = "BUY"
                strength = min(85, int((net_score / 6) * 100))
            elif net_score >= 0.5:
                direction = "WEAK BUY"
                strength = min(70, int((net_score / 4) * 100))
            elif net_score <= -3:
                direction = "STRONG SELL"
                strength = min(100, int((abs(net_score) / 8) * 100))
            elif net_score <= -1.5:
                direction = "SELL"
                strength = min(85, int((abs(net_score) / 6) * 100))
            elif net_score <= -0.5:
                direction = "WEAK SELL"
                strength = min(70, int((abs(net_score) / 4) * 100))
            else:
                direction = "HOLD"
                strength = 30
            
            return {
                'strength': strength,
                'direction': direction,
                'signals': signals,
                'rsi': rsi,
                'price_change_1d': price_change_1d,
                'price_change_5d': price_change_5d,
                'current_price': current_price,
                'volume_ratio': current_volume / volume_sma if volume_sma > 0 else 1,
                'bullish_score': bullish_score,
                'bearish_score': bearish_score
            }
            
        except Exception as e:
            return {'strength': 0, 'signals': [f"Error: {str(e)}"], 'direction': 'HOLD'}
    
    def analyze_stock(self, symbol: str) -> Optional[Dict]:
        """Analyze a single stock"""
        try:
            # Download data
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="6mo", interval="1d")
            
            if data.empty or len(data) < 20:
                return None
            
            # Calculate signal
            signal = self.calculate_signal_strength(data)
            
            # Add stock info
            signal['symbol'] = symbol
            signal['name'] = symbol.replace('.NS', '')
            
            return signal
            
        except Exception as e:
            print(f"⚠️ Error analyzing {symbol}: {str(e)}")
            return None
    
    def pick_stocks(self, min_strength: int = 50, max_stocks: int = 50) -> List[Dict]:
        """Pick stocks with analysis"""
        print(f"🔍 ANALYZING {len(self.liquid_stocks)} HIGH LIQUIDITY STOCKS")
        print("=" * 80)
        
        results = []
        processed = 0
        
        for symbol in self.liquid_stocks:
            processed += 1
            if processed % 50 == 0:
                print(f"📊 Processed {processed}/{len(self.liquid_stocks)} stocks...")
            
            analysis = self.analyze_stock(symbol)
            if analysis and analysis['strength'] >= min_strength:
                results.append(analysis)
        
        # Sort by strength
        results.sort(key=lambda x: x['strength'], reverse=True)
        
        return results[:max_stocks]
    
    def display_results(self, results: List[Dict]):
        """Display analysis results"""
        if not results:
            print("\n❌ NO STOCKS FOUND WITH CURRENT CRITERIA")
            print("💡 Try lowering the minimum strength threshold")
            return
        
        print(f"\n🎯 FOUND {len(results)} HIGH-PROBABILITY OPPORTUNITIES")
        print("=" * 100)
        
        # Group by signal strength
        strong_buys = [r for r in results if r['direction'] == 'STRONG BUY']
        buys = [r for r in results if r['direction'] == 'BUY']
        weak_buys = [r for r in results if r['direction'] == 'WEAK BUY']
        sells = [r for r in results if 'SELL' in r['direction']]
        
        print(f"🚀 STRONG BUY: {len(strong_buys)} stocks")
        print(f"📈 BUY: {len(buys)} stocks")
        print(f"📊 WEAK BUY: {len(weak_buys)} stocks")
        print(f"📉 SELL SIGNALS: {len(sells)} stocks")
        
        print("\n🎯 TOP OPPORTUNITIES:")
        print("-" * 100)
        print(f"{'SYMBOL':<15} {'SIGNAL':<12} {'STRENGTH':<10} {'PRICE CHG':<12} {'RSI':<6} {'VOL':<8} {'KEY SIGNALS'}")
        print("-" * 100)
        
        for result in results[:20]:  # Show top 20
            symbol = result['symbol']
            direction = result['direction']
            strength = result['strength']
            price_change = result.get('price_change_1d', 0)
            rsi = result.get('rsi', 50)
            vol_ratio = result.get('volume_ratio', 1)
            signals = ', '.join(result['signals'][:2])  # First 2 signals
            
            # Color coding
            if direction == 'STRONG BUY':
                direction_icon = "🚀"
            elif direction == 'BUY':
                direction_icon = "📈"
            elif direction == 'WEAK BUY':
                direction_icon = "📊"
            else:
                direction_icon = "📉"
            
            print(f"{symbol:<15} {direction_icon}{direction:<11} {strength:<10} {price_change:>+6.1f}%     {rsi:<6.1f} {vol_ratio:<8.1f} {signals}")
        
        # Show detailed analysis for top 5
        print(f"\n🔍 DETAILED ANALYSIS - TOP 5 PICKS:")
        print("=" * 100)
        
        for i, result in enumerate(results[:5], 1):
            print(f"\n{i}. {result['symbol']} - {result['direction']} (Strength: {result['strength']}%)")
            print(f"   💰 Current Price: ₹{result.get('current_price', 0):.2f}")
            print(f"   📊 1D Change: {result.get('price_change_1d', 0):+.1f}% | 5D Change: {result.get('price_change_5d', 0):+.1f}%")
            print(f"   📈 RSI: {result.get('rsi', 50):.1f} | Volume Ratio: {result.get('volume_ratio', 1):.1f}x")
            print(f"   🎯 Signals: {', '.join(result['signals'])}")
            
            # Risk calculation
            if result['direction'] in ['STRONG BUY', 'BUY', 'WEAK BUY']:
                entry_price = result.get('current_price', 100)
                stop_loss = entry_price * 0.92  # 8% stop loss
                take_profit = entry_price * 1.16  # 16% take profit
                trailing_stop = entry_price * 0.96  # 4% trailing stop
                
                print(f"   💡 Entry: ₹{entry_price:.2f} | Stop Loss: ₹{stop_loss:.2f} | Take Profit: ₹{take_profit:.2f}")
                print(f"   🔄 Trailing Stop: ₹{trailing_stop:.2f} (4% from entry)")

def main():
    """Main function"""
    picker = AdvancedStockPicker()
    
    print("🎯 ADVANCED STOCK PICKER - 500+ HIGH LIQUIDITY ANALYSIS")
    print("=" * 80)
    print(f"📅 Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 Market: Indian Stocks (NSE)")
    print(f"📊 Universe: {len(picker.liquid_stocks)} High Liquidity Stocks")
    print(f"⏱️ Timeframe: Daily (1D)")
    print("=" * 80)
    
    # Run analysis with different strength levels
    print("\n🔍 SCANNING FOR OPPORTUNITIES...")
    
    # High probability picks (70%+ strength)
    high_prob = picker.pick_stocks(min_strength=70, max_stocks=30)
    if high_prob:
        print(f"\n🎯 HIGH PROBABILITY PICKS (70%+ Strength):")
        picker.display_results(high_prob)
    
    # Medium probability picks (50%+ strength)
    medium_prob = picker.pick_stocks(min_strength=50, max_stocks=50)
    if medium_prob and not high_prob:
        print(f"\n📊 MEDIUM PROBABILITY PICKS (50%+ Strength):")
        picker.display_results(medium_prob)
    
    # All signals (30%+ strength)
    all_signals = picker.pick_stocks(min_strength=30, max_stocks=100)
    if all_signals and not medium_prob and not high_prob:
        print(f"\n📈 ALL SIGNALS (30%+ Strength):")
        picker.display_results(all_signals)
    
    if not all_signals:
        print(f"\n❌ NO SIGNIFICANT SIGNALS FOUND")
        print("💡 Market may be in consolidation phase")
        print("🔄 Try again later or check broader market conditions")

if __name__ == "__main__":
    main()
