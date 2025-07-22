#!/usr/bin/env python3
"""
500+ High Liquidity Stock Picker
Professional swing trading analysis for Indian stocks
"""

import pandas as pd
import yfinance as yf
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import warnings
warnings.filterwarnings('ignore')

class StockPicker500:
    def __init__(self):
        """Initialize the stock picker"""
        self.liquid_stocks = self._get_top_500_liquid_stocks()
        
    def _get_top_500_liquid_stocks(self) -> List[str]:
        """Get 500+ most liquid Indian stocks across all sectors"""
        stocks = [
            # Top Banking & Financial Services (50 stocks)
            'HDFCBANK.NS', 'ICICIBANK.NS', 'KOTAKBANK.NS', 'AXISBANK.NS', 'SBIN.NS',
            'INDUSINDBK.NS', 'BANKBARODA.NS', 'PNB.NS', 'FEDERALBNK.NS', 'IDFCFIRSTB.NS',
            'BAJFINANCE.NS', 'BAJAJFINSV.NS', 'SBILIFE.NS', 'HDFCLIFE.NS', 'ICICIPRULI.NS',
            'SBICARD.NS', 'HDFCAMC.NS', 'MUTHOOTFIN.NS', 'LICHSGFIN.NS', 'PFC.NS',
            'REC.NS', 'CHOLAFIN.NS', 'M&MFIN.NS', 'SHRIRAMFIN.NS', 'L&TFH.NS',
            'CANFINHOME.NS', 'REPCO.NS', 'UJJIVAN.NS', 'EQUITAS.NS', 'CREDITACC.NS',
            'IIFL.NS', 'MOTILALOFS.NS', 'ANGELONE.NS', 'CDSL.NS', 'CAMS.NS',
            'POLICYBZR.NS', 'PAYTM.NS', 'NYKAA.NS', 'DMART.NS', 'ZOMATO.NS',
            'SWIGGY.NS', 'IRCTC.NS', 'RBLBANK.NS', 'YESBANK.NS', 'IDFC.NS',
            'AUBANK.NS', 'BANDHANBNK.NS', 'CSB.NS', 'DCB.NS', 'SOUTHBANK.NS',
            
            # IT & Technology (40 stocks)
            'TCS.NS', 'INFY.NS', 'HCLTECH.NS', 'WIPRO.NS', 'TECHM.NS',
            'LTI.NS', 'MINDTREE.NS', 'MPHASIS.NS', 'COFORGE.NS', 'PERSISTENT.NS',
            'LTTS.NS', 'CYIENT.NS', 'ZENSAR.NS', 'KPIT.NS', 'SONATSOFTW.NS',
            'HEXAWARE.NS', 'RAMSARUP.NS', 'NIITTECH.NS', 'FIRSTSOURCE.NS', 'INTELLECT.NS',
            'RAMCOCEM.NS', 'TATAELXSI.NS', 'ECLERX.NS', 'NEWGEN.NS', 'HINDWARE.NS',
            'BIRLASOFT.NS', 'MASTEK.NS', 'RATEGAIN.NS', 'ROUTE.NS', 'TANLA.NS',
            'HAPPSTMNDS.NS', 'DATAPATTNS.NS', 'CMSINFO.NS', 'IIFL.NS', 'GATEWAY.NS',
            'BSOFT.NS', 'MINDACORP.NS', 'NUCLEUS.NS', 'ONEPOINT.NS', 'REDINGTON.NS',
            
            # Pharmaceuticals & Healthcare (45 stocks)
            'SUNPHARMA.NS', 'DRREDDY.NS', 'CIPLA.NS', 'DIVISLAB.NS', 'BIOCON.NS',
            'CADILAHC.NS', 'LUPIN.NS', 'AUROBINDO.NS', 'TORNTPHARM.NS', 'GLENMARK.NS',
            'ALKEM.NS', 'LALPATHLAB.NS', 'APOLLOHOSP.NS', 'FORTIS.NS', 'MAXHEALTH.NS',
            'METROPOLIS.NS', 'THYROCARE.NS', 'NARAYANA.NS', 'SYNGENE.NS', 'STRIDES.NS',
            'GRANULES.NS', 'SUVEN.NS', 'DIVIS.NS', 'SOLARA.NS', 'CAPLIN.NS',
            'SEQUENT.NS', 'NATCO.NS', 'AJANTPHARM.NS', 'PFIZER.NS', 'ABBOTINDIA.NS',
            'GLAXO.NS', 'NOVARTIS.NS', 'SANOFI.NS', 'JBCHEPHARM.NS', 'ERIS.NS',
            'FDC.NS', 'IPCA.NS', 'IPCALAB.NS', 'MANKIND.NS', 'ZYDUSLIFE.NS',
            'WOCKPHARMA.NS', 'STARHEALTH.NS', 'CARERATING.NS', 'ASTER.NS', 'RAINBOW.NS',
            
            # Energy, Oil & Gas (35 stocks)
            'RELIANCE.NS', 'ONGC.NS', 'IOC.NS', 'BPCL.NS', 'HPCL.NS',
            'GAIL.NS', 'ADANIGREEN.NS', 'NTPC.NS', 'POWERGRID.NS', 'COALINDIA.NS',
            'TATAPOWER.NS', 'ADANITRANS.NS', 'ADANIPORTS.NS', 'ADANIENT.NS', 'ADANIPOWER.NS',
            'JSPL.NS', 'SAIL.NS', 'ONGC.NS', 'OIL.NS', 'MGL.NS',
            'IGL.NS', 'PETRONET.NS', 'GSPL.NS', 'AEGISCHEM.NS', 'DEEPAKFERT.NS',
            'NFL.NS', 'RCF.NS', 'CHAMBLFERT.NS', 'GNFC.NS', 'FACT.NS',
            'MANGALORE.NS', 'MRPL.NS', 'CPCL.NS', 'HINDPETRO.NS', 'CASTROLIND.NS',
            
            # FMCG & Consumer Goods (40 stocks)
            'HINDUNILVR.NS', 'ITC.NS', 'NESTLEIND.NS', 'BRITANNIA.NS', 'MARICO.NS',
            'DABUR.NS', 'GODREJCP.NS', 'COLPAL.NS', 'PGHH.NS', 'UBL.NS',
            'TATACONSUM.NS', 'JUBLFOOD.NS', 'VBL.NS', 'EMAMILTD.NS', 'RADICO.NS',
            'BATA.NS', 'RELAXO.NS', 'APLAPOLLO.NS', 'VGUARD.NS', 'HAVELLS.NS',
            'CROMPTON.NS', 'POLYCAB.NS', 'KEI.NS', 'FINOLEX.NS', 'VMART.NS',
            'TRENT.NS', 'SHOPRITE.NS', 'AVENUE.NS', 'SPENCERS.NS', 'WESTLIFE.NS',
            'DEVYANI.NS', 'SAPPHIRE.NS', 'CCL.NS', 'HONAUT.NS', 'BIKAJI.NS',
            'CLEAN.NS', 'PARAG.NS', 'HATSUN.NS', 'KWALITY.NS', 'HERITAGE.NS',
            
            # Automobiles & Auto Components (35 stocks)
            'MARUTI.NS', 'HYUNDAI.NS', 'TATAMOTORS.NS', 'M&M.NS', 'BAJAJ-AUTO.NS',
            'HEROMOTOCO.NS', 'TVSMOTORS.NS', 'EICHERMOT.NS', 'ASHOKLEY.NS', 'FORCE.NS',
            'BOSCHLTD.NS', 'MRF.NS', 'APOLLOTYRE.NS', 'CEAT.NS', 'JK.NS',
            'BALKRISIND.NS', 'EXIDEIND.NS', 'AMARA.NS', 'SUNDARAM.NS', 'WHEELS.NS',
            'MOTHERSON.NS', 'BHARATFORG.NS', 'RAMKRISHNA.NS', 'ESCORTS.NS', 'MAHINDRA.NS',
            'SWARAJ.NS', 'VST.NS', 'BAJAJHLDNG.NS', 'RAJRATAN.NS', 'SUPRAJIT.NS',
            'SUBROS.NS', 'SANDHAR.NS', 'GABRIEL.NS', 'ENDURANCE.NS', 'FIEM.NS',
            
            # Metals & Mining (30 stocks)
            'TATASTEEL.NS', 'JSWSTEEL.NS', 'HINDALCO.NS', 'VEDL.NS', 'NATIONALUM.NS',
            'JINDALSTEL.NS', 'NMDC.NS', 'MOIL.NS', 'HINDZINC.NS', 'RATNAMANI.NS',
            'WELCORP.NS', 'WELSPUNIND.NS', 'JSWENERGY.NS', 'GMRINFRA.NS', 'ADANIENT.NS',
            'APLAPOLLO.NS', 'JINDAL.NS', 'GRAPHITE.NS', 'ORIENTREF.NS', 'HINDUSTNZINC.NS',
            'CESC.NS', 'RPOWER.NS', 'JPPOWER.NS', 'SUZLON.NS', 'INOXWIND.NS',
            'RITES.NS', 'RVNL.NS', 'IRCON.NS', 'KALPATPOWR.NS', 'THERMAX.NS',
            
            # Cement & Construction (25 stocks)
            'ULTRACEMCO.NS', 'SHREECEM.NS', 'GRASIM.NS', 'ACC.NS', 'AMBUJACEMENT.NS',
            'JKCEMENT.NS', 'RAMCOCEM.NS', 'HEIDELBERG.NS', 'STARCEMENT.NS', 'PRISMCEM.NS',
            'DALMIACEMT.NS', 'ORIENTCEM.NS', 'INDIACEM.NS', 'BIRLACEM.NS', 'KANPUR.NS',
            'LT.NS', 'BHARTIARTL.NS', 'JSWINFRA.NS', 'IRB.NS', 'NBCC.NS',
            'NCC.NS', 'KECL.NS', 'BEML.NS', 'HAL.NS', 'COCHINSHIP.NS',
            
            # Infrastructure & Utilities (30 stocks)
            'BEL.NS', 'BHEL.NS', 'GRINDWELL.NS', 'CUMMINSIND.NS', 'ABB.NS',
            'SIEMENS.NS', 'SCHNEIDER.NS', 'HONEYWELL.NS', 'CRISIL.NS', 'INOXLEISUR.NS',
            'PVR.NS', 'SPICEJET.NS', 'INDIGO.NS', 'CONCOR.NS', 'GESHIP.NS',
            'SCI.NS', 'BLUEDART.NS', 'DELHIVERY.NS', 'RAILTEL.NS', 'HFCL.NS',
            'STERLTECH.NS', 'OPTIEMUS.NS', 'TEJAS.NS', 'ROUTE.NS', 'RCOM.NS',
            'IDEA.NS', 'BHARTIARTL.NS', 'GTLINFRA.NS', 'TTML.NS', 'ONMOBILE.NS',
            
            # Textiles & Apparel (20 stocks)
            'VARDHMAN.NS', 'TRIDENT.NS', 'WELSPUNIND.NS', 'RAYMOND.NS', 'ADITYADG.NS',
            'RUPA.NS', 'PAGEIND.NS', 'ARVIND.NS', 'GOKEX.NS', 'SPENTEX.NS',
            'BANSWRAS.NS', 'CENTEX.NS', 'SUTLEJ.NS', 'ALOKTEXT.NS', 'WELHOUS.NS',
            'DONEAR.NS', 'DOLLAR.NS', 'LAXJUTE.NS', 'JCHAC.NS', 'PREMCO.NS',
            
            # Chemicals & Fertilizers (35 stocks)
            'UPL.NS', 'PIDILITIND.NS', 'AARTI.NS', 'GHCL.NS', 'TATACHEM.NS',
            'DEEPAKNTR.NS', 'BALRAMCHIN.NS', 'ALKYLAMINE.NS', 'NOCIL.NS', 'JUBILANT.NS',
            'SYMPHONY.NS', 'CHEMCON.NS', 'CLEAN.NS', 'DCMSHRIRAM.NS', 'FCONSUMER.NS',
            'KANSAINER.NS', 'TTKPRESTIG.NS', 'ORIENTHOT.NS', 'MAHINDRA.NS', 'PANTALOONS.NS',
            'CHALET.NS', 'BASF.NS', 'COROMANDEL.NS', 'CHAMBAL.NS', 'MADRASFERT.NS',
            'ZUARI.NS', 'NAGARFERT.NS', 'GSFC.NS', 'KRISHANA.NS', 'MANGALAM.NS',
            'PARADEEP.NS', 'SMARTLINK.NS', 'FILATEX.NS', 'FLEXIBLE.NS', 'VIPIND.NS',
            
            # Real Estate & Housing (20 stocks)
            'DLF.NS', 'GODREJPROP.NS', 'OBEROIRLTY.NS', 'BRIGADE.NS', 'SOBHA.NS',
            'PHOENIXLTD.NS', 'MAHLIFE.NS', 'PRESTIGE.NS', 'KOLTEPATIL.NS', 'MAHINDCIE.NS',
            'SUNTECK.NS', 'LODHA.NS', 'MACROTECH.NS', 'SIGNATURE.NS', 'ROHAN.NS',
            'MAHSEAMLES.NS', 'UNITECH.NS', 'PURAVANKARA.NS', 'MRPL.NS', 'HOUSEWARE.NS',
            
            # Media, Entertainment & Tourism (15 stocks)
            'ZEEL.NS', 'SUNTV.NS', 'NETWORK18.NS', 'TVTODAY.NS', 'RWORLD.NS',
            'DISHTV.NS', 'JAGRAN.NS', 'INDHOTEL.NS', 'LEMONTREE.NS', 'EIHLTD.NS',
            'ORIENTHOT.NS', 'CHALET.NS', 'MAHINDRA.NS', 'PANTALOONS.NS', 'TREEHOUSE.NS',
            
            # Agriculture & Food Processing (15 stocks)
            'KRBL.NS', 'DAAWAT.NS', 'RELMITTAL.NS', 'USHAMART.NS', 'LT.NS',
            'HSIL.NS', 'RELAXO.NS', 'VMART.NS', 'SHOPRITE.NS', 'WESTLIFE.NS',
            'DEVYANI.NS', 'SAPPHIRE.NS', 'VARUN.NS', 'AGRITECH.NS', 'SUMICRO.NS',
            
            # Education & Services (10 stocks)
            'APTECH.NS', 'NIIT.NS', 'NAVNEET.NS', 'CAREEREDGE.NS', 'KPIT.NS',
            'ZENSAR.NS', 'RAMKY.NS', 'EDUCOMP.NS', 'EVERONN.NS', 'TREE.NS'
        ]
        
        # Remove duplicates and return unique stocks
        return list(set(stocks))
    
    def calculate_technical_indicators(self, data: pd.DataFrame) -> Dict:
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
            
            # Bollinger Bands
            sma_20 = indicators['sma_20']
            std_20 = data['Close'].rolling(20).std()
            indicators['bb_upper'] = sma_20 + (std_20 * 2)
            indicators['bb_lower'] = sma_20 - (std_20 * 2)
            indicators['bb_middle'] = sma_20
            
            # Volume MA
            indicators['volume_ma'] = data['Volume'].rolling(20).mean()
            
        except Exception as e:
            print(f"Error calculating indicators: {e}")
        
        return indicators
    
    def analyze_stock(self, symbol: str) -> Optional[Dict]:
        """Analyze a single stock"""
        try:
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
            
            # Calculate signals
            signals = []
            score = 0
            
            # RSI Analysis
            rsi = indicators['rsi'].iloc[-1] if 'rsi' in indicators else 50
            if rsi < 30:
                signals.append("RSI Oversold")
                score += 2
            elif rsi > 70:
                signals.append("RSI Overbought")
                score -= 2
            elif 30 <= rsi <= 45:
                signals.append("RSI Bullish Zone")
                score += 1
            
            # MACD Analysis
            if 'macd' in indicators and 'macd_signal' in indicators:
                macd = indicators['macd'].iloc[-1]
                macd_signal = indicators['macd_signal'].iloc[-1]
                if macd > macd_signal and macd > 0:
                    signals.append("MACD Bullish")
                    score += 2
                elif macd < macd_signal and macd < 0:
                    signals.append("MACD Bearish")
                    score -= 2
            
            # MA Analysis
            if 'sma_20' in indicators and 'sma_50' in indicators:
                sma_20 = indicators['sma_20'].iloc[-1]
                sma_50 = indicators['sma_50'].iloc[-1]
                if current_price > sma_20 > sma_50:
                    signals.append("Above MAs")
                    score += 1.5
                elif current_price < sma_20 < sma_50:
                    signals.append("Below MAs")
                    score -= 1.5
            
            # Volume Analysis
            if 'volume_ma' in indicators:
                volume_ma = indicators['volume_ma'].iloc[-1]
                if current_volume > volume_ma * 1.5:
                    signals.append("High Volume")
                    score += 1
            
            # Price Action
            price_change_1d = ((current_price / data['Close'].iloc[-2]) - 1) * 100 if len(data) >= 2 else 0
            price_change_5d = ((current_price / data['Close'].iloc[-6]) - 1) * 100 if len(data) >= 6 else 0
            
            if price_change_1d > 3:
                signals.append(f"Strong Gain: +{price_change_1d:.1f}%")
                score += 1.5
            elif price_change_1d < -3:
                signals.append(f"Sharp Drop: {price_change_1d:.1f}%")
                score -= 1.5
            
            # Bollinger Bands
            if 'bb_upper' in indicators and 'bb_lower' in indicators:
                bb_upper = indicators['bb_upper'].iloc[-1]
                bb_lower = indicators['bb_lower'].iloc[-1]
                bb_middle = indicators['bb_middle'].iloc[-1]
                
                if current_price <= bb_lower:
                    signals.append("BB Oversold")
                    score += 1.5
                elif current_price >= bb_upper:
                    signals.append("BB Overbought")
                    score -= 1.5
                elif current_price > bb_middle:
                    signals.append("Above BB Mid")
                    score += 0.5
            
            # Determine signal direction and strength
            if score >= 3:
                direction = "STRONG BUY"
                strength = min(95, int((score / 8) * 100))
            elif score >= 1.5:
                direction = "BUY"
                strength = min(80, int((score / 6) * 100))
            elif score >= 0.5:
                direction = "WEAK BUY"
                strength = min(65, int((score / 4) * 100))
            elif score <= -3:
                direction = "STRONG SELL"
                strength = min(95, int((abs(score) / 8) * 100))
            elif score <= -1.5:
                direction = "SELL"
                strength = min(80, int((abs(score) / 6) * 100))
            elif score <= -0.5:
                direction = "WEAK SELL"
                strength = min(65, int((abs(score) / 4) * 100))
            else:
                direction = "HOLD"
                strength = 40
            
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
                'volume_ratio': current_volume / indicators.get('volume_ma', {}).iloc[-1] if 'volume_ma' in indicators else 1,
                'score': score
            }
            
        except Exception as e:
            print(f"⚠️ Error analyzing {symbol}: {str(e)}")
            return None
    
    def scan_all_stocks(self, min_strength: int = 50) -> List[Dict]:
        """Scan all 500+ stocks"""
        print(f"🔍 SCANNING {len(self.liquid_stocks)} HIGH LIQUIDITY STOCKS")
        print("=" * 80)
        
        results = []
        processed = 0
        errors = 0
        
        for i, symbol in enumerate(self.liquid_stocks, 1):
            try:
                if i % 50 == 0:
                    print(f"📊 Progress: {i}/{len(self.liquid_stocks)} stocks analyzed...")
                
                analysis = self.analyze_stock(symbol)
                if analysis and analysis['strength'] >= min_strength:
                    results.append(analysis)
                    
                processed += 1
                
            except Exception as e:
                errors += 1
                if errors < 10:  # Show first 10 errors only
                    print(f"⚠️ Error with {symbol}: {str(e)}")
        
        print(f"✅ Analysis Complete: {processed} stocks analyzed, {errors} errors")
        
        # Sort by strength
        results.sort(key=lambda x: x['strength'], reverse=True)
        return results
    
    def display_results(self, results: List[Dict]):
        """Display scan results"""
        if not results:
            print("❌ NO STOCKS FOUND MEETING CRITERIA")
            print("💡 Try lowering the minimum strength threshold")
            return
        
        print(f"\n🎯 FOUND {len(results)} OPPORTUNITIES")
        print("=" * 100)
        
        # Summary by signal type
        strong_buys = [r for r in results if r['direction'] == 'STRONG BUY']
        buys = [r for r in results if r['direction'] == 'BUY']
        weak_buys = [r for r in results if r['direction'] == 'WEAK BUY']
        
        print(f"🚀 STRONG BUY: {len(strong_buys)} stocks")
        print(f"📈 BUY: {len(buys)} stocks")  
        print(f"📊 WEAK BUY: {len(weak_buys)} stocks")
        
        print(f"\n🏆 TOP OPPORTUNITIES:")
        print("-" * 100)
        print(f"{'RANK':<6} {'SYMBOL':<15} {'SIGNAL':<12} {'STR%':<6} {'1D%':<8} {'5D%':<8} {'RSI':<6} {'VOL':<6} {'SIGNALS'}")
        print("-" * 100)
        
        for i, result in enumerate(results[:25], 1):  # Top 25
            symbol = result['symbol']
            direction = result['direction']
            strength = result['strength']
            price_1d = result['price_change_1d']
            price_5d = result['price_change_5d']
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
            
            print(f"{i:<6} {symbol:<15} {icon}{direction:<11} {strength:<6} {price_1d:>+6.1f}% {price_5d:>+6.1f}% {rsi:<6.1f} {vol_ratio:<6.1f} {signals}")
        
        # Detailed analysis for top 5
        print(f"\n🔍 TOP 5 DETAILED ANALYSIS:")
        print("=" * 100)
        
        for i, result in enumerate(results[:5], 1):
            print(f"\n{i}. {result['symbol']} - {result['direction']} (Strength: {result['strength']}%)")
            print(f"   💰 Price: ₹{result['current_price']:.2f}")
            print(f"   📊 Changes: 1D: {result['price_change_1d']:+.1f}% | 5D: {result['price_change_5d']:+.1f}%")
            print(f"   📈 RSI: {result['rsi']:.1f} | Volume: {result['volume_ratio']:.1f}x average")
            print(f"   🎯 Signals: {', '.join(result['signals'])}")
            
            # Trading levels
            if result['direction'] in ['STRONG BUY', 'BUY', 'WEAK BUY']:
                entry = result['current_price']
                stop_loss = entry * 0.92  # 8% stop
                take_profit = entry * 1.16  # 16% target
                trailing_stop = entry * 0.96  # 4% trailing
                
                print(f"   💡 Entry: ₹{entry:.2f} | SL: ₹{stop_loss:.2f} | TP: ₹{take_profit:.2f} | Trailing: ₹{trailing_stop:.2f}")

def main():
    """Main execution"""
    picker = StockPicker500()
    
    print("🎯 HIGH LIQUIDITY STOCK SCANNER - 500+ STOCKS")
    print("=" * 80)
    print(f"📅 Scan Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 Market: NSE (Indian Stocks)")
    print(f"📊 Universe: {len(picker.liquid_stocks)} High Liquidity Stocks")
    print(f"⏱️ Timeframe: Daily Swing Trading")
    print("=" * 80)
    
    # Scan with different strength levels
    print("\n🔍 STARTING COMPREHENSIVE SCAN...")
    
    # High strength signals (70%+)
    high_strength = picker.scan_all_stocks(min_strength=70)
    if high_strength:
        print(f"\n🎯 HIGH STRENGTH SIGNALS (70%+):")
        picker.display_results(high_strength)
    
    # Medium strength signals (55%+) 
    elif not high_strength:
        medium_strength = picker.scan_all_stocks(min_strength=55)
        if medium_strength:
            print(f"\n📊 MEDIUM STRENGTH SIGNALS (55%+):")
            picker.display_results(medium_strength)
    
    # All signals (40%+)
        elif not medium_strength:
            all_signals = picker.scan_all_stocks(min_strength=40)
            if all_signals:
                print(f"\n📈 ALL SIGNALS (40%+):")
                picker.display_results(all_signals)
            else:
                print(f"\n❌ NO SIGNALS FOUND")
                print("💡 Market may be in consolidation phase")
                print("🔄 Consider checking again during market hours")

if __name__ == "__main__":
    main()
