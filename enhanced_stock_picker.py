#!/usr/bin/env python3
"""
Enhanced Stock Picker - Fixed for Delisted Stocks
Professional swing trading analysis with active stocks only
"""

import pandas as pd
import yfinance as yf
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import warnings
warnings.filterwarnings('ignore')

class EnhancedStockPicker:
    def __init__(self):
        """Initialize the enhanced stock picker with active stocks only"""
        self.liquid_stocks = self._get_verified_liquid_stocks()
        # A+ Grade Parameters from .env
        self.min_signal_strength = 75
        self.volume_threshold = 1.8
        self.rsi_oversold = 25
        self.rsi_overbought = 75
        
    def _get_verified_liquid_stocks(self) -> List[str]:
        """Get verified active high liquidity Indian stocks (no delisted stocks)"""
        # Curated list of active, high-liquidity NSE stocks
        active_stocks = [
            # Top Banking & Financial Services (Active Only)
            'HDFCBANK.NS', 'ICICIBANK.NS', 'KOTAKBANK.NS', 'AXISBANK.NS', 'SBIN.NS',
            'INDUSINDBK.NS', 'BANKBARODA.NS', 'PNB.NS', 'FEDERALBNK.NS', 'IDFCFIRSTB.NS',
            'BAJFINANCE.NS', 'BAJAJFINSV.NS', 'SBILIFE.NS', 'HDFCLIFE.NS', 'ICICIPRULI.NS',
            'SBICARD.NS', 'HDFCAMC.NS', 'MUTHOOTFIN.NS', 'LICHSGFIN.NS', 'PFC.NS',
            'REC.NS', 'CHOLAFIN.NS', 'SHRIRAMFIN.NS', 'CANFINHOME.NS', 'RBLBANK.NS',
            'AUBANK.NS', 'BANDHANBNK.NS', 'YESBANK.NS', 'ANGELONE.NS', 'CDSL.NS',
            
            # IT & Technology (Active)
            'TCS.NS', 'INFY.NS', 'HCLTECH.NS', 'WIPRO.NS', 'TECHM.NS',
            'LTIM.NS', 'MPHASIS.NS', 'COFORGE.NS', 'PERSISTENT.NS', 'LTTS.NS',
            'TATAELXSI.NS', 'MINDTREE.NS', 'CYIENT.NS', 'SONATSOFTW.NS', 'INTELLECT.NS',
            'NEWGEN.NS', 'RATEGAIN.NS', 'TANLA.NS', 'HAPPSTMNDS.NS', 'DATAPATTNS.NS',
            
            # Pharmaceuticals & Healthcare (Active)
            'SUNPHARMA.NS', 'DRREDDY.NS', 'CIPLA.NS', 'DIVISLAB.NS', 'BIOCON.NS',
            'LUPIN.NS', 'TORNTPHARM.NS', 'GLENMARK.NS', 'ALKEM.NS', 'LALPATHLAB.NS',
            'APOLLOHOSP.NS', 'FORTIS.NS', 'MAXHEALTH.NS', 'METROPOLIS.NS', 'SYNGENE.NS',
            'GRANULES.NS', 'AJANTPHARM.NS', 'PFIZER.NS', 'ABBOTINDIA.NS', 'GLAXO.NS',
            'SANOFI.NS', 'ERIS.NS', 'MANKIND.NS', 'ZYDUSLIFE.NS', 'STARHEALTH.NS',
            
            # Energy, Oil & Gas (Active)
            'RELIANCE.NS', 'ONGC.NS', 'IOC.NS', 'BPCL.NS', 'HPCL.NS',
            'GAIL.NS', 'ADANIGREEN.NS', 'NTPC.NS', 'POWERGRID.NS', 'COALINDIA.NS',
            'TATAPOWER.NS', 'ADANIPORTS.NS', 'ADANIENT.NS', 'ADANIPOWER.NS', 'OIL.NS',
            'MGL.NS', 'IGL.NS', 'PETRONET.NS', 'GSPL.NS', 'ATGL.NS',
            
            # FMCG & Consumer Goods (Active)
            'HINDUNILVR.NS', 'ITC.NS', 'NESTLEIND.NS', 'BRITANNIA.NS', 'MARICO.NS',
            'DABUR.NS', 'GODREJCP.NS', 'COLPAL.NS', 'UBL.NS', 'TATACONSUM.NS',
            'JUBLFOOD.NS', 'VBL.NS', 'EMAMILTD.NS', 'RADICO.NS', 'RELAXO.NS',
            'VGUARD.NS', 'HAVELLS.NS', 'CROMPTON.NS', 'POLYCAB.NS', 'KEI.NS',
            'VMART.NS', 'TRENT.NS', 'WESTLIFE.NS', 'DEVYANI.NS', 'CCL.NS',
            
            # Automobiles & Auto Components (Active)
            'MARUTI.NS', 'TATAMOTORS.NS', 'M&M.NS', 'BAJAJ-AUTO.NS', 'HEROMOTOCO.NS',
            'EICHERMOT.NS', 'ASHOKLEY.NS', 'BOSCHLTD.NS', 'MRF.NS', 'APOLLOTYRE.NS',
            'BALKRISIND.NS', 'EXIDEIND.NS', 'MOTHERSON.NS', 'BHARATFORG.NS', 'ESCORTS.NS',
            'MAHINDRA.NS', 'BAJAJHLDNG.NS', 'ENDURANCE.NS', 'GABRIEL.NS', 'SANDHAR.NS',
            
            # Metals & Mining (Active)
            'TATASTEEL.NS', 'JSWSTEEL.NS', 'HINDALCO.NS', 'VEDL.NS', 'NATIONALUM.NS',
            'JINDALSTEL.NS', 'NMDC.NS', 'MOIL.NS', 'HINDZINC.NS', 'WELCORP.NS',
            'JSWENERGY.NS', 'GMRINFRA.NS', 'ADANIENT.NS', 'APLAPOLLO.NS', 'GRAPHITE.NS',
            'CESC.NS', 'RPOWER.NS', 'SUZLON.NS', 'INOXWIND.NS', 'RITES.NS',
            
            # Cement & Construction (Active)
            'ULTRACEMCO.NS', 'SHREECEM.NS', 'GRASIM.NS', 'ACC.NS', 'JKCEMENT.NS',
            'RAMCOCEM.NS', 'HEIDELBERG.NS', 'DALMIACEMT.NS', 'ORIENTCEM.NS', 'INDIACEM.NS',
            'LT.NS', 'BHARTIARTL.NS', 'IRB.NS', 'NBCC.NS', 'NCC.NS',
            'KECL.NS', 'BEML.NS', 'HAL.NS', 'COCHINSHIP.NS', 'GRSE.NS',
            
            # Infrastructure & Utilities (Active)
            'BEL.NS', 'BHEL.NS', 'CUMMINSIND.NS', 'ABB.NS', 'SIEMENS.NS',
            'VOLTAS.NS', 'BLUESTAR.NS', 'THERMAX.NS', 'CONCOR.NS', 'GESHIP.NS',
            'SCI.NS', 'BLUEDART.NS', 'RAILTEL.NS', 'HFCL.NS', 'GTLINFRA.NS',
            'BHARTIARTL.NS', 'IDEA.NS', 'INDIGO.NS', 'IRCTC.NS', 'ZOMATO.NS',
            
            # Chemicals & Fertilizers (Active)
            'UPL.NS', 'PIDILITIND.NS', 'GHCL.NS', 'TATACHEM.NS', 'DEEPAKNTR.NS',
            'BALRAMCHIN.NS', 'ALKYLAMINE.NS', 'NOCIL.NS', 'SYMPHONY.NS', 'CLEAN.NS',
            'DCMSHRIRAM.NS', 'KANSAINER.NS', 'TTKPRESTIG.NS', 'BASF.NS', 'COROMANDEL.NS',
            'CHAMBAL.NS', 'GSFC.NS', 'RCF.NS', 'NFL.NS', 'FACT.NS',
            
            # Real Estate & Housing (Active)
            'DLF.NS', 'GODREJPROP.NS', 'OBEROIRLTY.NS', 'BRIGADE.NS', 'SOBHA.NS',
            'PHOENIXLTD.NS', 'PRESTIGE.NS', 'SUNTECK.NS', 'LODHA.NS', 'MACROTECH.NS',
            
            # Media & Entertainment (Active)
            'ZEEL.NS', 'SUNTV.NS', 'NETWORK18.NS', 'DISHTV.NS', 'JAGRAN.NS',
            'INDHOTEL.NS', 'LEMONTREE.NS', 'CHALET.NS', 'PVR.NS', 'INOXLEISUR.NS',
            
            # Textiles & Apparel (Active)
            'RAYMOND.NS', 'ARVIND.NS', 'GOKEX.NS', 'WELSPUNIND.NS', 'TRIDENT.NS',
            'VARDHMAN.NS', 'ADITYADG.NS', 'RUPA.NS', 'PAGEIND.NS', 'DOLLAR.NS',
            
            # Telecom (Active)
            'BHARTIARTL.NS', 'IDEA.NS', 'RAILTEL.NS', 'HFCL.NS', 'GTLINFRA.NS',
            
            # Others (Active)
            'DMART.NS', 'NYKAA.NS', 'PAYTM.NS', 'POLICYBZR.NS', 'DELTACORP.NS'
        ]
        
        return list(set(active_stocks))  # Remove duplicates
    
    def verify_stock_data(self, symbol: str) -> bool:
        """Verify if stock data is available and active"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="5d", interval="1d")
            return not data.empty and len(data) >= 3
        except:
            return False
    
    def calculate_technical_indicators(self, data: pd.DataFrame) -> Dict:
        """Calculate technical indicators with error handling"""
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
            
            # Bollinger Bands
            sma_20 = indicators['sma_20']
            std_20 = data['Close'].rolling(20).std()
            indicators['bb_upper'] = sma_20 + (std_20 * 2)
            indicators['bb_lower'] = sma_20 - (std_20 * 2)
            indicators['bb_middle'] = sma_20
            
            # Volume MA
            indicators['volume_ma'] = data['Volume'].rolling(20).mean()
            
        except Exception as e:
            print(f"⚠️ Error calculating indicators for {data.index[-1] if not data.empty else 'unknown'}: {e}")
        
        return indicators
    
    def analyze_stock_enhanced(self, symbol: str) -> Optional[Dict]:
        """Analyze a single stock with enhanced A+ grade criteria"""
        try:
            # Verify stock is active first
            if not self.verify_stock_data(symbol):
                return None
            
            # Download data
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="6mo", interval="1d")
            
            if data.empty or len(data) < 30:
                return None
            
            # Calculate indicators
            indicators = self.calculate_technical_indicators(data)
            if not indicators:
                return None
            
            current_price = data['Close'].iloc[-1]
            current_volume = data['Volume'].iloc[-1]
            
            # Enhanced signal calculation for A+ grade
            signals = []
            score = 0
            
            # RSI Analysis (More strict for A+ grade)
            rsi = indicators['rsi'].iloc[-1] if 'rsi' in indicators else 50
            if rsi <= self.rsi_oversold:  # 25 or below
                signals.append("RSI Extreme Oversold")
                score += 3
            elif rsi >= self.rsi_overbought:  # 75 or above
                signals.append("RSI Extreme Overbought")
                score -= 3
            elif 25 < rsi <= 35:
                signals.append("RSI Strong Bullish Zone")
                score += 2
            elif 65 <= rsi < 75:
                signals.append("RSI Strong Bearish Zone")
                score -= 2
            
            # MACD Analysis (Enhanced)
            if 'macd' in indicators and 'macd_signal' in indicators:
                macd = indicators['macd'].iloc[-1]
                macd_signal = indicators['macd_signal'].iloc[-1]
                macd_prev = indicators['macd'].iloc[-2] if len(indicators['macd']) > 1 else macd
                macd_signal_prev = indicators['macd_signal'].iloc[-2] if len(indicators['macd_signal']) > 1 else macd_signal
                
                # Fresh crossover detection
                if macd > macd_signal and macd_prev <= macd_signal_prev and macd > 0:
                    signals.append("MACD Fresh Bull Crossover")
                    score += 3
                elif macd < macd_signal and macd_prev >= macd_signal_prev and macd < 0:
                    signals.append("MACD Fresh Bear Crossover")
                    score -= 3
            
            # Moving Average Analysis (Enhanced)
            if 'sma_20' in indicators and 'sma_50' in indicators:
                sma_20 = indicators['sma_20'].iloc[-1]
                sma_50 = indicators['sma_50'].iloc[-1]
                price_above_20 = current_price > sma_20
                price_above_50 = current_price > sma_50
                ma_20_above_50 = sma_20 > sma_50
                
                if price_above_20 and price_above_50 and ma_20_above_50:
                    signals.append("Perfect MA Alignment")
                    score += 2.5
                elif not price_above_20 and not price_above_50 and not ma_20_above_50:
                    signals.append("Perfect MA Bearish")
                    score -= 2.5
            
            # Volume Analysis (Strict requirement for A+ grade)
            if 'volume_ma' in indicators:
                volume_ma = indicators['volume_ma'].iloc[-1]
                volume_ratio = current_volume / volume_ma if volume_ma > 0 else 1
                
                if volume_ratio >= self.volume_threshold:  # 1.8x or higher
                    signals.append(f"High Volume ({volume_ratio:.1f}x)")
                    score += 2
                elif volume_ratio < 0.5:
                    signals.append("Low Volume")
                    score -= 1
            
            # Price Action Analysis (Enhanced)
            price_change_1d = ((current_price / data['Close'].iloc[-2]) - 1) * 100 if len(data) >= 2 else 0
            price_change_5d = ((current_price / data['Close'].iloc[-6]) - 1) * 100 if len(data) >= 6 else 0
            price_change_20d = ((current_price / data['Close'].iloc[-21]) - 1) * 100 if len(data) >= 21 else 0
            
            if price_change_1d > 5:
                signals.append(f"Strong Breakout: +{price_change_1d:.1f}%")
                score += 2.5
            elif price_change_1d < -5:
                signals.append(f"Sharp Decline: {price_change_1d:.1f}%")
                score -= 2.5
            
            # Bollinger Bands Analysis (Enhanced)
            if 'bb_upper' in indicators and 'bb_lower' in indicators:
                bb_upper = indicators['bb_upper'].iloc[-1]
                bb_lower = indicators['bb_lower'].iloc[-1]
                bb_middle = indicators['bb_middle'].iloc[-1]
                
                bb_position = (current_price - bb_lower) / (bb_upper - bb_lower)
                
                if bb_position <= 0.1:  # Near lower band
                    signals.append("BB Extreme Oversold")
                    score += 2
                elif bb_position >= 0.9:  # Near upper band
                    signals.append("BB Extreme Overbought")
                    score -= 2
            
            # Calculate signal strength based on A+ criteria
            strength = min(100, max(0, int((score + 5) / 10 * 100)))
            
            # Apply minimum signal strength filter (75% for A+ grade)
            if strength < self.min_signal_strength:
                return None
            
            # Determine direction
            if score >= 4:
                direction = "STRONG BUY"
            elif score >= 2:
                direction = "BUY"
            elif score >= 1:
                direction = "WEAK BUY"
            elif score <= -4:
                direction = "STRONG SELL"
            elif score <= -2:
                direction = "SELL"
            elif score <= -1:
                direction = "WEAK SELL"
            else:
                direction = "HOLD"
            
            return {
                'symbol': symbol,
                'name': symbol.replace('.NS', ''),
                'direction': direction,
                'strength': strength,
                'signals': signals,
                'rsi': rsi,
                'current_price': current_price,
                'price_change_1d': price_change_1d,
                'price_change_5d': price_change_5d,
                'price_change_20d': price_change_20d,
                'volume_ratio': current_volume / indicators.get('volume_ma', pd.Series([current_volume])).iloc[-1] if 'volume_ma' in indicators else 1,
                'score': score
            }
            
        except Exception as e:
            print(f"⚠️ Error analyzing {symbol}: {str(e)}")
            return None
    
    def scan_aplus_stocks(self, max_stocks: int = 50) -> List[Dict]:
        """Scan for A+ grade stock opportunities"""
        print(f"🏆 A+ GRADE STOCK SCANNER - {len(self.liquid_stocks)} VERIFIED ACTIVE STOCKS")
        print("=" * 80)
        print(f"⭐ Min Signal Strength: {self.min_signal_strength}%")
        print(f"📊 Volume Threshold: {self.volume_threshold}x")
        print(f"🎯 RSI Levels: {self.rsi_oversold}/{self.rsi_overbought}")
        print("=" * 80)
        
        results = []
        processed = 0
        skipped = 0
        
        for i, symbol in enumerate(self.liquid_stocks, 1):
            try:
                if i % 25 == 0:
                    print(f"📊 Progress: {i}/{len(self.liquid_stocks)} stocks analyzed... Found: {len(results)} A+ opportunities")
                
                analysis = self.analyze_stock_enhanced(symbol)
                if analysis:
                    results.append(analysis)
                    processed += 1
                else:
                    skipped += 1
                    
            except Exception as e:
                skipped += 1
                if skipped <= 5:  # Show only first 5 errors
                    print(f"⚠️ Skipped {symbol}: {str(e)}")
        
        print(f"✅ Scan Complete: {processed} A+ stocks found, {skipped} stocks skipped")
        
        # Sort by strength
        results.sort(key=lambda x: x['strength'], reverse=True)
        return results[:max_stocks]
    
    def display_aplus_results(self, results: List[Dict]):
        """Display A+ grade results"""
        if not results:
            print("\n❌ NO A+ GRADE OPPORTUNITIES FOUND")
            print("💡 Consider lowering criteria or checking during market hours")
            return
        
        print(f"\n🏆 FOUND {len(results)} A+ GRADE OPPORTUNITIES")
        print("=" * 100)
        
        # Group by signal strength
        strong_buys = [r for r in results if r['direction'] == 'STRONG BUY']
        buys = [r for r in results if r['direction'] == 'BUY']
        weak_buys = [r for r in results if r['direction'] == 'WEAK BUY']
        
        print(f"🚀 STRONG BUY: {len(strong_buys)} stocks")
        print(f"📈 BUY: {len(buys)} stocks")
        print(f"📊 WEAK BUY: {len(weak_buys)} stocks")
        
        print(f"\n🎯 TOP A+ OPPORTUNITIES:")
        print("-" * 110)
        print(f"{'RANK':<6} {'SYMBOL':<15} {'SIGNAL':<12} {'STR%':<6} {'1D%':<8} {'5D%':<8} {'20D%':<8} {'RSI':<6} {'VOL':<6} {'KEY SIGNALS'}")
        print("-" * 110)
        
        for i, result in enumerate(results[:20], 1):  # Top 20
            symbol = result['symbol']
            direction = result['direction']
            strength = result['strength']
            price_1d = result['price_change_1d']
            price_5d = result['price_change_5d']
            price_20d = result['price_change_20d']
            rsi = result['rsi']
            vol_ratio = result['volume_ratio']
            signals = ', '.join(result['signals'][:2])
            
            # Direction icon
            if direction == 'STRONG BUY':
                icon = "🚀"
            elif direction == 'BUY':
                icon = "📈"
            else:
                icon = "📊"
            
            print(f"{i:<6} {symbol:<15} {icon}{direction:<11} {strength:<6} {price_1d:>+6.1f}% {price_5d:>+6.1f}% {price_20d:>+6.1f}% {rsi:<6.1f} {vol_ratio:<6.1f} {signals}")
        
        # Detailed analysis for top 5
        print(f"\n🔍 TOP 5 A+ DETAILED ANALYSIS:")
        print("=" * 100)
        
        for i, result in enumerate(results[:5], 1):
            print(f"\n{i}. {result['symbol']} - {result['direction']} (A+ Strength: {result['strength']}%)")
            print(f"   💰 Price: ₹{result['current_price']:.2f}")
            print(f"   📊 Performance: 1D: {result['price_change_1d']:+.1f}% | 5D: {result['price_change_5d']:+.1f}% | 20D: {result['price_change_20d']:+.1f}%")
            print(f"   📈 RSI: {result['rsi']:.1f} | Volume: {result['volume_ratio']:.1f}x average")
            print(f"   🎯 A+ Signals: {', '.join(result['signals'])}")
            
            # A+ Grade trading levels
            if result['direction'] in ['STRONG BUY', 'BUY', 'WEAK BUY']:
                entry = result['current_price']
                stop_loss = entry * 0.94  # 6% stop (A+ grade)
                take_profit = entry * 1.20  # 20% target (A+ grade)
                trailing_stop = entry * 0.965  # 3.5% trailing (A+ grade)
                
                print(f"   💡 A+ Entry: ₹{entry:.2f} | SL: ₹{stop_loss:.2f} | TP: ₹{take_profit:.2f} | Trailing: ₹{trailing_stop:.2f}")

def main():
    """Main execution"""
    picker = EnhancedStockPicker()
    
    print("🏆 A+ GRADE ENHANCED STOCK PICKER")
    print("=" * 80)
    print(f"📅 Scan Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 Market: NSE (Indian Stocks)")
    print(f"📊 Universe: {len(picker.liquid_stocks)} Verified Active Stocks")
    print(f"⏱️ Timeframe: Daily Swing Trading")
    print(f"🎖️ Grade Target: A+ EXCELLENT")
    print("=" * 80)
    
    # Scan for A+ opportunities
    aplus_opportunities = picker.scan_aplus_stocks(max_stocks=30)
    picker.display_aplus_results(aplus_opportunities)

if __name__ == "__main__":
    main()
