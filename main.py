"""
Main Application Script
=======================

Command-line interface for the swing trading system.
"""

import argparse
import sys
import logging
from datetime import datetime, timedelta
from pathlib import Path
import time

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from trading_system import TradingConfig, TradingEngine
from trading_system.data_manager import DataManager
from trading_system.technical_analysis import TechnicalAnalyzer
from trading_system.ai_analyzer import AIAnalyzer

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/trading_system.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Create logs directory
Path('logs').mkdir(exist_ok=True)

logger = logging.getLogger(__name__)


def run_daily_analysis():
    """Run daily market analysis."""
    try:
        logger.info("Starting daily analysis...")
        
        # Initialize system
        config = TradingConfig()
        engine = TradingEngine(config)
        
        # Start trading session
        engine.start_trading_session()
        
        # Run analysis
        results = engine.run_daily_analysis()
        
        # Print results
        print("\n" + "="*60)
        print("DAILY MARKET ANALYSIS RESULTS")
        print("="*60)
        print(f"Analysis Time: {results.get('analysis_time', 'N/A')}")
        print(f"Stocks Analyzed: {results.get('total_stocks_analyzed', 0)}")
        print(f"High Confidence Signals: {results.get('high_confidence_signals', 0)}")
        
        # Print trade recommendations
        recommendations = results.get('trade_recommendations', [])
        if recommendations:
            print(f"\nTOP TRADE RECOMMENDATIONS:")
            print("-" * 40)
            for i, rec in enumerate(recommendations, 1):
                rec_data = rec.get('recommendation', {})
                symbol = rec.get('symbol', 'N/A')
                ai_conf = rec.get('ai_confidence', 0)
                tech_conf = rec.get('technical_confidence', 0)
                
                print(f"{i}. {symbol}")
                print(f"   Signal: {getattr(rec_data, 'recommendation', 'N/A').value if hasattr(rec_data, 'recommendation') else 'N/A'}")
                print(f"   AI Confidence: {ai_conf:.2f}")
                print(f"   Technical Confidence: {tech_conf:.2f}")
                print(f"   Combined Score: {rec.get('combined_score', 0):.2f}")
                print()
        
        # Print market analysis
        market_analysis = results.get('market_analysis', '')
        if market_analysis:
            print(f"\nMARKET ANALYSIS:")
            print("-" * 40)
            print(market_analysis[:500] + "..." if len(market_analysis) > 500 else market_analysis)
        
        # Print portfolio summary
        portfolio = results.get('portfolio_summary', {})
        if portfolio:
            print(f"\nPORTFOLIO SUMMARY:")
            print("-" * 40)
            print(f"Portfolio Value: ₹{portfolio.get('portfolio_value', 0):,.2f}")
            print(f"Total Return: {portfolio.get('total_return_pct', 0):.2f}%")
            print(f"Active Positions: {portfolio.get('positions_count', 0)}")
            print(f"Cash: {portfolio.get('cash_pct', 0):.1f}%")
        
        # Cleanup
        engine.cleanup()
        
        print(f"\nAnalysis completed successfully!")
        
    except Exception as e:
        logger.error(f"Error in daily analysis: {e}")
        print(f"Error: {e}")
        sys.exit(1)


def analyze_stock(symbol: str):
    """Analyze a specific stock."""
    try:
        logger.info(f"Analyzing {symbol}...")
        
        # Initialize components
        config = TradingConfig()
        data_manager = DataManager(config)
        technical_analyzer = TechnicalAnalyzer(config)
        ai_analyzer = AIAnalyzer(config)
        
        # Get stock data
        stock_data = data_manager.get_stock_data(symbol)
        
        # Technical analysis
        tech_analysis = technical_analyzer.analyze_stock(stock_data)
        
        # AI analysis
        ai_analysis = ai_analyzer.analyze_stock_with_ai(stock_data, tech_analysis)
        
        # Print results
        print(f"\n{'='*60}")
        print(f"ANALYSIS RESULTS FOR {symbol}")
        print(f"{'='*60}")
        
        # Technical analysis summary
        print(technical_analyzer.get_trading_summary(tech_analysis))
        
        print(f"\n")
        
        # AI analysis summary
        print(ai_analyzer.format_ai_analysis(ai_analysis))
        
        logger.info(f"Analysis for {symbol} completed")
        
    except Exception as e:
        logger.error(f"Error analyzing {symbol}: {e}")
        print(f"Error: {e}")
        sys.exit(1)


def monitor_portfolio():
    """Monitor portfolio in real-time."""
    try:
        logger.info("Starting portfolio monitoring...")
        
        config = TradingConfig()
        engine = TradingEngine(config)
        
        engine.start_trading_session()
        
        print("Portfolio Monitoring Started (Press Ctrl+C to stop)")
        print("="*60)
        
        while True:
            try:
                # Get market summary
                summary = engine.get_market_summary()
                
                # Clear screen and print summary
                print("\033[2J\033[H")  # Clear screen
                print(summary)
                print(f"\nLast updated: {datetime.now().strftime('%H:%M:%S')}")
                print("Press Ctrl+C to stop monitoring...")
                
                # Wait 30 seconds before next update
                time.sleep(30)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(5)
        
        engine.cleanup()
        print("Portfolio monitoring stopped.")
        
    except Exception as e:
        logger.error(f"Error in portfolio monitoring: {e}")
        print(f"Error: {e}")
        sys.exit(1)


def run_quick_backtest(period: str = "3m", capital: float = 100000):
    """Run quick backtesting."""
    try:
        logger.info(f"Running quick backtest for {period} with ₹{capital:,.0f}")
        
        print(f"🧪 QUICK BACKTEST ANALYSIS")
        print("=" * 50)
        print(f"💰 Capital: ₹{capital:,.0f}")
        print(f"📅 Period: {period}")
        print("🔄 Testing your trading system...")
        
        # Initialize components
        config = TradingConfig()
        data_manager = DataManager(config)
        technical_analyzer = TechnicalAnalyzer(config)
        
        # Import and initialize risk manager
        from trading_system.risk_manager import RiskManager
        risk_manager = RiskManager(config)
        
        # Import backtester
        from trading_system.backtester import Backtester
        backtester = Backtester(config, data_manager, technical_analyzer, risk_manager)
        
        # Set date range based on period
        end_date = datetime.now().strftime('%Y-%m-%d')
        if period == '3m':
            start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
        elif period == '6m':
            start_date = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')
        elif period == '1y':
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        else:
            start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
        
        # Get top liquid stocks for quick test
        test_stocks = config.get_indian_stock_symbols()[:100]  # Top 100 for quick test
        
        print(f"📊 Testing {len(test_stocks)} stocks from {start_date} to {end_date}")
        
        # Run backtest
        metrics = backtester.run_backtest(
            symbols=test_stocks,
            start_date=start_date,
            end_date=end_date,
            initial_capital=capital
        )
        
        # Display results
        print(f"\n📊 QUICK BACKTEST RESULTS")
        print("-" * 50)
        print(f"💰 Starting Capital: ₹{metrics.initial_capital:,.0f}")
        print(f"💰 Ending Capital: ₹{metrics.final_capital:,.0f}")
        print(f"📈 Total Return: ₹{metrics.total_return:,.0f} ({metrics.total_return_pct:+.2f}%)")
        print(f"📊 Total Trades: {metrics.total_trades}")
        print(f"🏆 Win Rate: {metrics.win_rate:.1f}%")
        print(f"⚖️ Profit Factor: {metrics.profit_factor:.2f}")
        print(f"📉 Max Drawdown: {metrics.max_drawdown_pct:.2f}%")
        
        # Quick assessment
        if metrics.win_rate >= 50 and metrics.profit_factor >= 1.2:
            print(f"\n✅ SYSTEM LOOKS PROFITABLE!")
            print("🚀 Consider running full backtest: python run_backtest.py")
        elif metrics.profit_factor >= 1.0:
            print(f"\n⚠️ SYSTEM SHOWS POTENTIAL")
            print("🔧 May need optimization for better performance")
        else:
            print(f"\n❌ SYSTEM NEEDS IMPROVEMENT")
            print("🔄 Consider revising strategy parameters")
        
        print(f"\n💡 For comprehensive analysis run: python run_backtest.py")
        
    except Exception as e:
        logger.error(f"Error in quick backtest: {e}")
        print(f"Error: {e}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="High-Probability Swing Trading System for Indian Stocks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
🎯 TODAY'S HIGH-PROBABILITY ANALYSIS:
  python main.py analyze                     # Full market analysis
  python analyze_today.py                   # Detailed today's opportunities  
  python quick_screen.py                    # Quick 5-minute screener
  
📊 BACKTESTING & VALIDATION:
  python main.py backtest                    # Quick 3-month backtest
  python run_backtest.py                    # Comprehensive 1000+ stocks test
  
🔧 OTHER COMMANDS:
  python main.py stock RELIANCE.NS          # Analyze specific stock
  python main.py monitor                    # Monitor portfolio
  python main.py dashboard                  # Launch web dashboard

💡 For immediate trading opportunities, run: python analyze_today.py
🧪 To validate your system, run: python run_backtest.py
        """
    )
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Daily analysis command
    subparsers.add_parser('analyze', help='Run comprehensive market analysis')
    
    # Stock analysis command
    stock_parser = subparsers.add_parser('stock', help='Analyze specific stock')
    stock_parser.add_argument('symbol', help='Stock symbol (e.g., RELIANCE.NS)')
    
    # Portfolio monitoring command
    subparsers.add_parser('monitor', help='Monitor portfolio in real-time')
    
    # Dashboard command
    subparsers.add_parser('dashboard', help='Launch Streamlit dashboard')
    
    # Backtesting command
    backtest_parser = subparsers.add_parser('backtest', help='Run quick backtesting')
    backtest_parser.add_argument('--period', default='3m', help='Backtest period (3m, 6m, 1y)')
    backtest_parser.add_argument('--capital', type=float, default=100000, help='Starting capital in INR')
    
    args = parser.parse_args()
    
    if args.command == 'analyze':
        run_daily_analysis()
    elif args.command == 'stock':
        analyze_stock(args.symbol)
    elif args.command == 'monitor':
        monitor_portfolio()
    elif args.command == 'dashboard':
        import subprocess
        subprocess.run(['streamlit', 'run', 'dashboard.py'])
    elif args.command == 'backtest':
        run_quick_backtest(args.period, args.capital)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
