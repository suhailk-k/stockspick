"""
Quick Market Screener - Find High-Probability Trades Fast
==========================================================

This script provides a quick screener for immediate trading opportunities.
"""

import sys
from pathlib import Path
import logging
from datetime import datetime
import pandas as pd

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Setup logging
logging.basicConfig(level=logging.ERROR)  # Minimal logging

def quick_screen():
    """Quick screen for immediate opportunities."""
    print("⚡ QUICK MARKET SCREENER")
    print(f"🕐 {datetime.now().strftime('%H:%M:%S')} | Looking for immediate opportunities...")
    print("="*60)
    
    try:
        from trading_system.config import TradingConfig
        from trading_system.trading_engine import TradingEngine
        from trading_system.technical_analysis import SignalType
        
        # Initialize system
        config = TradingConfig()
        engine = TradingEngine(config)
        engine.start_trading_session()
        
        # Quick scan of top liquid stocks
        top_stocks = [
            'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'HINDUNILVR.NS',
            'ICICIBANK.NS', 'SBIN.NS', 'BHARTIARTL.NS', 'ITC.NS', 'KOTAKBANK.NS',
            'LT.NS', 'ASIANPAINT.NS', 'AXISBANK.NS', 'MARUTI.NS', 'TITAN.NS'
        ]
        
        print(f"🔍 Scanning {len(top_stocks)} liquid stocks...")
        
        # Quick analysis
        opportunities = []
        
        for symbol in top_stocks:
            try:
                print(f"📊 {symbol.replace('.NS', '')}...", end=' ')
                
                # Quick technical analysis
                analyzer = engine.technical_analyzer
                data = engine.data_manager.get_stock_data(symbol, period='90d')
                
                if data is not None and len(data) >= 50:
                    # Calculate key indicators quickly
                    indicators = analyzer.calculate_indicators(data)
                    signals = analyzer.generate_signals(data, indicators)
                    
                    if signals:
                        overall_signal = analyzer.get_overall_signal(signals)
                        
                        if overall_signal in [SignalType.BUY, SignalType.STRONG_BUY]:
                            current_price = data['close'].iloc[-1]
                            
                            # Quick risk calculation
                            atr = indicators.get('atr', 0)
                            if atr > 0:
                                stop_loss = current_price - (2 * atr)
                                take_profit = current_price + (3 * atr)
                                rr_ratio = (take_profit - current_price) / (current_price - stop_loss)
                                
                                if rr_ratio >= 1.5:
                                    confidence = len([s for s in signals if s.signal_type in [SignalType.BUY, SignalType.STRONG_BUY]]) / len(signals)
                                    
                                    opportunities.append({
                                        'symbol': symbol.replace('.NS', ''),
                                        'price': current_price,
                                        'stop_loss': stop_loss,
                                        'take_profit': take_profit,
                                        'rr_ratio': rr_ratio,
                                        'confidence': confidence,
                                        'signal': overall_signal.value,
                                        'signals_count': len(signals)
                                    })
                                    print("✅")
                                else:
                                    print("⚠️")
                            else:
                                print("❌")
                        else:
                            print("➖")
                    else:
                        print("❓")
                else:
                    print("💤")
                    
            except Exception as e:
                print("❌")
                continue
        
        # Display results
        print(f"\n🎯 QUICK OPPORTUNITIES ({len(opportunities)} found)")
        print("="*60)
        
        if not opportunities:
            print("❌ No immediate opportunities found.")
            print("💡 Try running the full analysis with: python analyze_today.py")
            return
        
        # Sort by score
        opportunities.sort(key=lambda x: x['confidence'] * x['rr_ratio'], reverse=True)
        
        # Display top opportunities
        print(f"{'Stock':<8} {'Signal':<10} {'Price':<10} {'R:R':<6} {'Conf':<6} {'Signals':<8}")
        print("-"*60)
        
        for opp in opportunities[:10]:
            print(f"{opp['symbol']:<8} {opp['signal']:<10} ₹{opp['price']:<9.2f} "
                  f"{opp['rr_ratio']:<6.2f} {opp['confidence']:<6.2f} {opp['signals_count']:<8}")
        
        # Quick action items
        if opportunities:
            best_opp = opportunities[0]
            print(f"\n🏆 TOP PICK: {best_opp['symbol']}")
            print(f"💰 Entry: ₹{best_opp['price']:.2f}")
            print(f"🛡️  Stop: ₹{best_opp['stop_loss']:.2f}")
            print(f"🎯 Target: ₹{best_opp['take_profit']:.2f}")
            print(f"⚖️  R:R: 1:{best_opp['rr_ratio']:.2f}")
        
        print(f"\n💡 For detailed analysis run: python analyze_today.py")
        
        engine.cleanup()
        
    except Exception as e:
        print(f"❌ Screener error: {e}")


if __name__ == "__main__":
    quick_screen()
