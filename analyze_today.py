"""
Today's High-Probability Trades Analysis
=========================================

This script analyzes Indian stocks and provides high-probability swing trading opportunities for today.
"""

import sys
from pathlib import Path
import logging
from datetime import datetime
import pandas as pd

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Setup logging
logging.basicConfig(level=logging.WARNING)  # Reduce log noise

def analyze_todays_opportunities():
    """Analyze today's high-probability trading opportunities."""
    print("🎯 High-Probability Swing Trading Analysis")
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    try:
        from trading_system.config import TradingConfig
        from trading_system.trading_engine import TradingEngine
        from trading_system.technical_analysis import SignalType
        
        # Initialize system
        config = TradingConfig()
        engine = TradingEngine(config)
        
        print("🔧 Initializing trading system...")
        engine.start_trading_session()
        
        # Get market status
        market_status = engine.data_manager.get_market_status()
        print(f"📊 Market Status: {market_status['status']}")
        
        if market_status['status'] == 'OPEN':
            print(f"⏰ Session ends: {market_status['session_end'].strftime('%H:%M')}")
        elif 'next_open' in market_status:
            print(f"⏰ Next session: {market_status['next_open'].strftime('%Y-%m-%d %H:%M')}")
        
        # Analyze top stocks
        print("\n🔍 Analyzing top Indian stocks...")
        symbols = config.get_indian_stock_symbols()[:25]  # Top 25 for comprehensive analysis
        
        print(f"📈 Scanning {len(symbols)} stocks for opportunities...")
        
        # Run analysis
        analysis_results = engine.analyze_multiple_stocks(symbols)
        
        if not analysis_results:
            print("❌ No analysis results available. Please check your internet connection.")
            return
        
        print(f"✅ Successfully analyzed {len(analysis_results)} stocks")
        
        # Filter high-probability opportunities
        high_prob_trades = []
        
        for symbol, analysis in analysis_results.items():
            # Only consider BUY signals with reasonable confidence
            if analysis.overall_signal in [SignalType.BUY, SignalType.STRONG_BUY]:
                if analysis.confidence >= 0.5:  # At least 50% confidence
                    
                    # Get current price and levels
                    current_price = analysis.key_levels.get('current_price', 0)
                    stop_loss = analysis.risk_reward.get('stop_loss', 0)
                    take_profit = analysis.risk_reward.get('take_profit', 0)
                    rr_ratio = analysis.risk_reward.get('risk_reward_ratio', 0)
                    
                    # Only consider trades with good risk/reward (> 1.5)
                    if rr_ratio >= 1.5 and current_price > 0:
                        
                        # Calculate position size
                        position_size = engine.risk_manager.calculate_position_size(
                            symbol, current_price, stop_loss
                        )
                        
                        if position_size.is_viable:
                            high_prob_trades.append({
                                'symbol': symbol,
                                'signal': analysis.overall_signal.value,
                                'confidence': analysis.confidence,
                                'current_price': current_price,
                                'stop_loss': stop_loss,
                                'take_profit': take_profit,
                                'rr_ratio': rr_ratio,
                                'risk_pct': position_size.risk_percentage,
                                'position_value': position_size.position_value,
                                'key_signals': analysis.signals[:3],  # Top 3 signals
                                'analysis': analysis
                            })
        
        # Sort by combined score (confidence * risk_reward)
        high_prob_trades.sort(
            key=lambda x: x['confidence'] * x['rr_ratio'], 
            reverse=True
        )
        
        # Display results
        print(f"\n🎯 HIGH-PROBABILITY SWING TRADES ({len(high_prob_trades)} found)")
        print("="*80)
        
        if not high_prob_trades:
            print("❌ No high-probability trades found at this time.")
            print("\nThis could be due to:")
            print("• Current market conditions")
            print("• All stocks are in HOLD or SELL signals")
            print("• Risk/reward ratios are not favorable")
            print("• Try again later or adjust confidence thresholds")
            return
        
        # Display top 5 opportunities
        for i, trade in enumerate(high_prob_trades[:5], 1):
            print(f"\n🏆 TRADE #{i}: {trade['symbol']}")
            print("-" * 50)
            print(f"📊 Signal: {trade['signal']} (Confidence: {trade['confidence']:.2f})")
            print(f"💰 Entry Price: ₹{trade['current_price']:.2f}")
            print(f"🛡️  Stop Loss: ₹{trade['stop_loss']:.2f} (-{((trade['current_price'] - trade['stop_loss']) / trade['current_price'] * 100):.1f}%)")
            print(f"🎯 Take Profit: ₹{trade['take_profit']:.2f} (+{((trade['take_profit'] - trade['current_price']) / trade['current_price'] * 100):.1f}%)")
            print(f"📈 Trailing Stop: 4% below highest price (activates when profitable)")
            print(f"⚖️  Risk:Reward: 1:{trade['rr_ratio']:.2f}")
            print(f"📈 Position Value: ₹{trade['position_value']:,.0f}")
            print(f"🔥 Risk: {trade['risk_pct']:.2f}% of capital")
            
            # Key technical signals
            print(f"🔍 Key Signals:")
            for signal in trade['key_signals']:
                print(f"   • {signal.indicator}: {signal.signal_type.value} (Strength: {signal.strength:.2f})")
        
        # Summary table
        if len(high_prob_trades) > 5:
            print(f"\n📋 ADDITIONAL OPPORTUNITIES ({len(high_prob_trades) - 5} more)")
            print("-" * 80)
            print(f"{'Symbol':<12} {'Signal':<10} {'Conf':<6} {'Price':<10} {'R:R':<6} {'Risk%':<7}")
            print("-" * 80)
            
            for trade in high_prob_trades[5:15]:  # Show next 10
                print(f"{trade['symbol']:<12} {trade['signal']:<10} {trade['confidence']:<6.2f} "
                      f"₹{trade['current_price']:<9.2f} {trade['rr_ratio']:<6.2f} {trade['risk_pct']:<7.2f}")
        
        # Market overview
        print(f"\n📊 MARKET OVERVIEW")
        print("-" * 50)
        
        # Signal distribution
        signal_counts = {}
        total_analyzed = len(analysis_results)
        
        for analysis in analysis_results.values():
            signal = analysis.overall_signal.value
            signal_counts[signal] = signal_counts.get(signal, 0) + 1
        
        print(f"Total Stocks Analyzed: {total_analyzed}")
        for signal, count in signal_counts.items():
            pct = (count / total_analyzed) * 100
            print(f"{signal}: {count} stocks ({pct:.1f}%)")
        
        # Risk summary
        portfolio_summary = engine.portfolio_manager.get_portfolio_summary()
        print(f"\n💼 Portfolio: ₹{portfolio_summary.get('portfolio_value', 0):,.0f}")
        print(f"💵 Available Capital: ₹{portfolio_summary.get('current_capital', 0):,.0f}")
        print(f"📍 Active Positions: {portfolio_summary.get('positions_count', 0)}")
        
        # Trading tips
        print(f"\n💡 TRADING TIPS")
        print("-" * 50)
        print("• Start with paper trading to test strategies")
        print("• Never risk more than 2% per trade")
        print("• Always use stop losses")
        print("• Consider market conditions and news")
        print("• This is educational content, not financial advice")
        
        print(f"\n⚠️  DISCLAIMER")
        print("-" * 50)
        print("This analysis is for educational purposes only.")
        print("Past performance does not guarantee future results.")
        print("Always do your own research and consider consulting a financial advisor.")
        
        # Cleanup
        engine.cleanup()
        
    except Exception as e:
        print(f"❌ Error in analysis: {e}")
        print("Please check your internet connection and try again.")


def main():
    """Main function."""
    try:
        analyze_todays_opportunities()
    except KeyboardInterrupt:
        print("\n\n⏹️  Analysis interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")


if __name__ == "__main__":
    main()
