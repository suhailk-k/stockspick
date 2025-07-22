"""
Demo Script - Swing Trading System
===================================

This script demonstrates the key features of the trading system.
"""

import sys
from pathlib import Path
import logging

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def demo_data_fetching():
    """Demo data fetching capabilities."""
    print("\n" + "="*60)
    print("📊 DEMO: Data Fetching")
    print("="*60)
    
    try:
        from trading_system.config import TradingConfig
        from trading_system.data_manager import DataManager
        
        config = TradingConfig()
        data_manager = DataManager(config)
        
        # Get stock data
        print("Fetching data for RELIANCE.NS...")
        stock_data = data_manager.get_stock_data("RELIANCE.NS", period="10d")
        
        print(f"✅ Successfully fetched {len(stock_data.data)} days of data")
        print(f"Latest close price: ₹{stock_data.data['Close'].iloc[-1]:.2f}")
        print(f"Volume: {stock_data.data['Volume'].iloc[-1]:,}")
        
        # Market status
        market_status = data_manager.get_market_status()
        print(f"Market Status: {market_status['status']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in data fetching demo: {e}")
        return False


def demo_technical_analysis():
    """Demo technical analysis."""
    print("\n" + "="*60)
    print("📈 DEMO: Technical Analysis")
    print("="*60)
    
    try:
        from trading_system.config import TradingConfig
        from trading_system.data_manager import DataManager
        from trading_system.technical_analysis import TechnicalAnalyzer
        
        config = TradingConfig()
        data_manager = DataManager(config)
        analyzer = TechnicalAnalyzer(config)
        
        # Analyze RELIANCE
        print("Analyzing RELIANCE.NS...")
        stock_data = data_manager.get_stock_data("RELIANCE.NS")
        analysis = analyzer.analyze_stock(stock_data)
        
        print(f"✅ Analysis completed")
        print(f"Signal: {analysis.overall_signal.value}")
        print(f"Confidence: {analysis.confidence:.2f}")
        print(f"Current Price: ₹{analysis.key_levels.get('current_price', 0):.2f}")
        print(f"Support: ₹{analysis.key_levels.get('support_1', 0):.2f}")
        print(f"Resistance: ₹{analysis.key_levels.get('resistance_1', 0):.2f}")
        
        # Show top 3 signals
        print("\nTop Technical Signals:")
        for i, signal in enumerate(analysis.signals[:3], 1):
            print(f"{i}. {signal.indicator}: {signal.signal_type.value} (Strength: {signal.strength:.2f})")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in technical analysis demo: {e}")
        return False


def demo_risk_management():
    """Demo risk management."""
    print("\n" + "="*60)
    print("🛡️ DEMO: Risk Management")
    print("="*60)
    
    try:
        from trading_system.config import TradingConfig
        from trading_system.risk_manager import RiskManager, PositionType
        
        config = TradingConfig()
        risk_manager = RiskManager(config)
        
        # Calculate position size
        entry_price = 2500
        stop_loss = 2300
        
        print(f"Calculating position size for:")
        print(f"Entry Price: ₹{entry_price}")
        print(f"Stop Loss: ₹{stop_loss}")
        print(f"Available Capital: ₹{config.capital:,}")
        
        position_size = risk_manager.calculate_position_size(
            symbol="RELIANCE.NS",
            entry_price=entry_price,
            stop_loss=stop_loss,
            position_type=PositionType.LONG
        )
        
        print(f"\n✅ Position sizing calculated:")
        print(f"Recommended Quantity: {position_size.recommended_quantity}")
        print(f"Position Value: ₹{position_size.position_value:,.2f}")
        print(f"Risk Amount: ₹{position_size.risk_amount:.2f}")
        print(f"Risk Percentage: {position_size.risk_percentage:.2f}%")
        print(f"Viable: {'Yes' if position_size.is_viable else 'No'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in risk management demo: {e}")
        return False


def demo_portfolio_management():
    """Demo portfolio management."""
    print("\n" + "="*60)
    print("💼 DEMO: Portfolio Management")
    print("="*60)
    
    try:
        from trading_system.config import TradingConfig
        from trading_system.data_manager import DataManager
        from trading_system.portfolio_manager import PortfolioManager
        
        config = TradingConfig()
        data_manager = DataManager(config)
        portfolio_manager = PortfolioManager(config, data_manager)
        
        # Get portfolio summary
        summary = portfolio_manager.get_portfolio_summary()
        performance = portfolio_manager.get_performance_metrics()
        
        print(f"Portfolio Value: ₹{summary.get('portfolio_value', 0):,.2f}")
        print(f"Available Capital: ₹{summary.get('current_capital', 0):,.2f}")
        print(f"Active Positions: {summary.get('positions_count', 0)}")
        print(f"Total Return: {summary.get('total_return_pct', 0):.2f}%")
        
        print(f"\nPerformance Metrics:")
        print(f"Total Trades: {performance.total_trades}")
        print(f"Win Rate: {performance.win_rate:.1f}%")
        print(f"Profit Factor: {performance.profit_factor:.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in portfolio management demo: {e}")
        return False


def demo_without_ai():
    """Demo system without AI (in case API key is missing)."""
    print("\n" + "="*60)
    print("🚀 DEMO: Complete System (Without AI)")
    print("="*60)
    
    try:
        from trading_system.config import TradingConfig
        from trading_system.trading_engine import TradingEngine
        
        # Create config without AI
        config = TradingConfig()
        
        # Initialize engine
        engine = TradingEngine(config)
        print("✅ Trading engine initialized")
        
        # Get trade recommendations (without AI)
        print("\nGetting trade recommendations...")
        
        # Analyze a few stocks
        test_symbols = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS"]
        analysis_results = engine.analyze_multiple_stocks(test_symbols)
        
        print(f"✅ Analyzed {len(analysis_results)} stocks")
        
        # Get recommendations
        recommendations = engine.get_trade_recommendations(3)
        
        if recommendations:
            print(f"\n🎯 Top Trade Recommendations:")
            for i, rec in enumerate(recommendations, 1):
                print(f"\n{i}. {rec['symbol']}")
                print(f"   Signal: {rec['signal']}")
                print(f"   Confidence: {rec['confidence']:.2f}")
                print(f"   Entry: ₹{rec['current_price']:.2f}")
                print(f"   Stop Loss: ₹{rec['stop_loss']:.2f}")
                print(f"   Take Profit: ₹{rec['take_profit']:.2f}")
                print(f"   R:R Ratio: 1:{rec['risk_reward_ratio']:.2f}")
        else:
            print("No trade recommendations at this time")
        
        # Portfolio summary
        print(f"\n💼 Portfolio Summary:")
        summary = engine.portfolio_manager.get_portfolio_summary()
        print(f"Portfolio Value: ₹{summary.get('portfolio_value', 0):,.2f}")
        print(f"Cash: ₹{summary.get('current_capital', 0):,.2f}")
        print(f"Positions: {summary.get('positions_count', 0)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in complete system demo: {e}")
        print(f"Details: {str(e)}")
        return False


def main():
    """Run all demos."""
    print("🎯 Swing Trading System - Demo")
    print("Enterprise-grade trading system for Indian stocks")
    print("="*60)
    
    # Track success
    demos = [
        ("Data Fetching", demo_data_fetching),
        ("Technical Analysis", demo_technical_analysis), 
        ("Risk Management", demo_risk_management),
        ("Portfolio Management", demo_portfolio_management),
        ("Complete System", demo_without_ai)
    ]
    
    results = []
    
    for demo_name, demo_func in demos:
        try:
            success = demo_func()
            results.append((demo_name, success))
        except Exception as e:
            print(f"❌ Failed to run {demo_name} demo: {e}")
            results.append((demo_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("📊 DEMO RESULTS SUMMARY")
    print("="*60)
    
    for demo_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{demo_name:<20} {status}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"\nOverall: {passed}/{total} demos passed")
    
    if passed == total:
        print("🎉 All demos completed successfully!")
        print("\nNext steps:")
        print("1. Set your Gemini API key in .env file")
        print("2. Run: python main.py analyze")
        print("3. Launch dashboard: python main.py dashboard")
    else:
        print("⚠️ Some demos failed. Check the error messages above.")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    main()
