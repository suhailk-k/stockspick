"""
Streamlit Dashboard
===================

Interactive web dashboard for the swing trading system.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import sys
from pathlib import Path
import logging

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from trading_system import TradingConfig, TradingEngine
from trading_system.technical_analysis import SignalType

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page config
st.set_page_config(
    page_title="Swing Trading Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .signal-buy {
        background-color: #d4edda;
        color: #155724;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-weight: bold;
    }
    .signal-sell {
        background-color: #f8d7da;
        color: #721c24;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-weight: bold;
    }
    .signal-hold {
        background-color: #fff3cd;
        color: #856404;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=300)  # Cache for 5 minutes
def initialize_system():
    """Initialize the trading system."""
    try:
        config = TradingConfig()
        engine = TradingEngine(config)
        return engine
    except Exception as e:
        st.error(f"Error initializing system: {e}")
        return None


@st.cache_data(ttl=600)  # Cache for 10 minutes
def get_market_data(engine, symbols):
    """Get market data for symbols."""
    if not engine:
        return {}
    
    try:
        return engine.data_manager.get_multiple_stocks_data(symbols, period="200d")
    except Exception as e:
        st.error(f"Error fetching market data: {e}")
        return {}


@st.cache_data(ttl=300)  # Cache for 5 minutes
def run_analysis(engine, symbols):
    """Run technical analysis."""
    if not engine:
        return {}
    
    try:
        return engine.analyze_multiple_stocks(symbols)
    except Exception as e:
        st.error(f"Error running analysis: {e}")
        return {}


def main():
    """Main dashboard function."""
    st.title("📈 Swing Trading Dashboard")
    st.markdown("**Professional Swing Trading System for Indian Stocks**")
    
    # Initialize system
    with st.spinner("Initializing trading system..."):
        engine = initialize_system()
    
    if not engine:
        st.error("Failed to initialize trading system. Please check your configuration.")
        return
    
    # Sidebar
    st.sidebar.title("🎛️ Control Panel")
    
    # Market status
    market_status = engine.data_manager.get_market_status()
    status_color = "🟢" if market_status['is_open'] else "🔴"
    st.sidebar.markdown(f"**Market Status:** {status_color} {market_status['status']}")
    
    # Configuration
    st.sidebar.subheader("Configuration")
    
    # Stock selection
    all_symbols = engine.config.get_indian_stock_symbols()
    selected_symbols = st.sidebar.multiselect(
        "Select Stocks to Analyze",
        options=all_symbols,
        default=all_symbols[:10],  # Default to first 10
        help="Select stocks for analysis (max 20 recommended for performance)"
    )
    
    if len(selected_symbols) > 20:
        st.sidebar.warning("⚠️ Too many stocks selected. Performance may be slow.")
    
    # Analysis settings
    confidence_threshold = st.sidebar.slider(
        "Confidence Threshold",
        min_value=0.0,
        max_value=1.0,
        value=0.6,
        step=0.1,
        help="Minimum confidence for trade signals"
    )
    
    # Main content tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Market Overview", 
        "🎯 Trade Signals", 
        "💼 Portfolio", 
        "📈 Stock Analysis",
        "🤖 AI Insights"
    ])
    
    # Tab 1: Market Overview
    with tab1:
        st.header("Market Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Market Status",
                value=market_status['status'],
                delta=market_status.get('current_time', datetime.now()).strftime("%H:%M:%S")
            )
        
        with col2:
            portfolio_summary = engine.portfolio_manager.get_portfolio_summary()
            st.metric(
                label="Portfolio Value",
                value=f"₹{portfolio_summary.get('portfolio_value', 0):,.0f}",
                delta=f"{portfolio_summary.get('total_return_pct', 0):.2f}%"
            )
        
        with col3:
            st.metric(
                label="Active Positions",
                value=portfolio_summary.get('positions_count', 0),
                delta=f"Max: {engine.config.risk.max_positions}"
            )
        
        with col4:
            st.metric(
                label="Cash Available",
                value=f"₹{portfolio_summary.get('current_capital', 0):,.0f}",
                delta=f"{portfolio_summary.get('cash_pct', 0):.1f}%"
            )
        
        # Market analysis
        if st.button("🔄 Run Market Analysis", type="primary"):
            with st.spinner("Running comprehensive market analysis..."):
                try:
                    analysis_results = run_analysis(engine, selected_symbols)
                    
                    if analysis_results:
                        # Signal distribution
                        signal_counts = {}
                        for analysis in analysis_results.values():
                            signal = analysis.overall_signal.value
                            signal_counts[signal] = signal_counts.get(signal, 0) + 1
                        
                        # Create signal distribution chart
                        fig = px.pie(
                            values=list(signal_counts.values()),
                            names=list(signal_counts.keys()),
                            title="Signal Distribution",
                            color_discrete_map={
                                'BUY': '#28a745',
                                'STRONG_BUY': '#155724',
                                'SELL': '#dc3545',
                                'STRONG_SELL': '#721c24',
                                'HOLD': '#ffc107'
                            }
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        st.success(f"✅ Analyzed {len(analysis_results)} stocks successfully!")
                    else:
                        st.warning("No analysis results available.")
                        
                except Exception as e:
                    st.error(f"Error running analysis: {e}")
    
    # Tab 2: Trade Signals
    with tab2:
        st.header("Trade Signals")
        
        if st.button("🎯 Get Trade Recommendations", type="primary"):
            with st.spinner("Generating trade recommendations..."):
                try:
                    recommendations = engine.get_trade_recommendations(limit=10)
                    
                    if recommendations:
                        # Create recommendations table
                        rec_data = []
                        for rec in recommendations:
                            rec_data.append({
                                'Symbol': rec['symbol'],
                                'Signal': rec['signal'],
                                'Confidence': f"{rec['confidence']:.2f}",
                                'Current Price': f"₹{rec['current_price']:.2f}",
                                'Stop Loss': f"₹{rec['stop_loss']:.2f}",
                                'Take Profit': f"₹{rec['take_profit']:.2f}",
                                'R:R Ratio': f"1:{rec['risk_reward_ratio']:.2f}",
                                'Position Size': rec['position_size'],
                                'Risk Amount': f"₹{rec['risk_amount']:.0f}"
                            })
                        
                        df = pd.DataFrame(rec_data)
                        
                        # Style the dataframe
                        def style_signal(val):
                            if 'BUY' in val:
                                return 'background-color: #d4edda; color: #155724'
                            elif 'SELL' in val:
                                return 'background-color: #f8d7da; color: #721c24'
                            else:
                                return 'background-color: #fff3cd; color: #856404'
                        
                        styled_df = df.style.applymap(style_signal, subset=['Signal'])
                        st.dataframe(styled_df, use_container_width=True)
                        
                        # Action buttons
                        st.subheader("Execute Trades")
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            selected_trade = st.selectbox(
                                "Select trade to execute:",
                                options=[f"{rec['symbol']} - {rec['signal']}" for rec in recommendations]
                            )
                        
                        with col2:
                            if st.button("Execute Trade", type="primary"):
                                symbol = selected_trade.split(' - ')[0]
                                if engine.execute_trade(symbol):
                                    st.success(f"✅ Trade executed for {symbol}")
                                else:
                                    st.error(f"❌ Failed to execute trade for {symbol}")
                    else:
                        st.info("No trade recommendations at this time.")
                        
                except Exception as e:
                    st.error(f"Error getting recommendations: {e}")
    
    # Tab 3: Portfolio
    with tab3:
        st.header("Portfolio Management")
        
        # Portfolio summary
        portfolio_summary = engine.portfolio_manager.get_portfolio_summary()
        performance = engine.portfolio_manager.get_performance_metrics()
        
        # Performance metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Total Return",
                f"₹{portfolio_summary.get('total_return', 0):,.0f}",
                f"{portfolio_summary.get('total_return_pct', 0):.2f}%"
            )
            
            st.metric(
                "Win Rate",
                f"{performance.win_rate:.1f}%",
                f"{performance.winning_trades}W/{performance.losing_trades}L"
            )
        
        with col2:
            st.metric(
                "Profit Factor",
                f"{performance.profit_factor:.2f}",
                "Higher is better"
            )
            
            st.metric(
                "Max Drawdown",
                f"{performance.max_drawdown:.2f}%",
                "Lower is better"
            )
        
        with col3:
            st.metric(
                "Avg Trade Duration",
                f"{performance.avg_trade_duration:.1f} days",
                f"Total: {performance.total_trades} trades"
            )
            
            st.metric(
                "Sharpe Ratio",
                f"{performance.sharpe_ratio:.2f}",
                "Risk-adjusted returns"
            )
        
        # Current positions
        if engine.portfolio_manager.positions:
            st.subheader("Current Positions")
            
            positions_data = []
            for position in engine.portfolio_manager.positions.values():
                positions_data.append({
                    'Symbol': position.symbol,
                    'Type': position.position_type.value,
                    'Quantity': position.quantity,
                    'Entry Price': f"₹{position.entry_price:.2f}",
                    'Current Price': f"₹{position.current_price:.2f}",
                    'P&L': f"₹{position.unrealized_pnl:.2f}",
                    'P&L%': f"{position.get_return_percentage():.2f}%",
                    'Stop Loss': f"₹{position.stop_loss:.2f}",
                    'Take Profit': f"₹{position.take_profit:.2f}"
                })
            
            positions_df = pd.DataFrame(positions_data)
            st.dataframe(positions_df, use_container_width=True)
        else:
            st.info("No active positions")
        
        # Portfolio report
        if st.button("📊 Generate Portfolio Report"):
            with st.spinner("Generating report..."):
                report = engine.portfolio_manager.generate_portfolio_report()
                st.text(report)
    
    # Tab 4: Stock Analysis
    with tab4:
        st.header("Individual Stock Analysis")
        
        # Stock selection for detailed analysis
        analysis_symbol = st.selectbox(
            "Select stock for detailed analysis:",
            options=selected_symbols if selected_symbols else all_symbols[:10]
        )
        
        if st.button("📈 Analyze Stock", type="primary"):
            with st.spinner(f"Analyzing {analysis_symbol}..."):
                try:
                    # Get stock data
                    stock_data = engine.data_manager.get_stock_data(analysis_symbol)
                    
                    # Technical analysis
                    tech_analysis = engine.technical_analyzer.analyze_stock(stock_data)
                    
                    # Display price chart
                    fig = go.Figure()
                    
                    # Candlestick chart
                    fig.add_trace(go.Candlestick(
                        x=stock_data.data.index,
                        open=stock_data.data['Open'],
                        high=stock_data.data['High'],
                        low=stock_data.data['Low'],
                        close=stock_data.data['Close'],
                        name=analysis_symbol
                    ))
                    
                    # Add technical indicators if available
                    if 'EMA_9' in tech_analysis.indicators:
                        fig.add_trace(go.Scatter(
                            x=stock_data.data.index,
                            y=tech_analysis.indicators['EMA_9'],
                            name='EMA 9',
                            line=dict(color='orange')
                        ))
                    
                    if 'EMA_21' in tech_analysis.indicators:
                        fig.add_trace(go.Scatter(
                            x=stock_data.data.index,
                            y=tech_analysis.indicators['EMA_21'],
                            name='EMA 21',
                            line=dict(color='blue')
                        ))
                    
                    fig.update_layout(
                        title=f"{analysis_symbol} - Price Chart with Technical Indicators",
                        xaxis_title="Date",
                        yaxis_title="Price (₹)",
                        height=500
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Analysis summary
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("Technical Analysis")
                        st.markdown(f"**Signal:** {tech_analysis.overall_signal.value}")
                        st.markdown(f"**Confidence:** {tech_analysis.confidence:.2f}")
                        st.markdown(f"**Current Price:** ₹{tech_analysis.key_levels.get('current_price', 0):.2f}")
                        st.markdown(f"**Support:** ₹{tech_analysis.key_levels.get('support_1', 0):.2f}")
                        st.markdown(f"**Resistance:** ₹{tech_analysis.key_levels.get('resistance_1', 0):.2f}")
                    
                    with col2:
                        st.subheader("Risk/Reward")
                        st.markdown(f"**Stop Loss:** ₹{tech_analysis.risk_reward.get('stop_loss', 0):.2f}")
                        st.markdown(f"**Take Profit:** ₹{tech_analysis.risk_reward.get('take_profit', 0):.2f}")
                        st.markdown(f"**R:R Ratio:** 1:{tech_analysis.risk_reward.get('risk_reward_ratio', 0):.2f}")
                        st.markdown(f"**Risk %:** {tech_analysis.risk_reward.get('risk_percentage', 0):.2f}%")
                        st.markdown(f"**Reward %:** {tech_analysis.risk_reward.get('reward_percentage', 0):.2f}%")
                    
                    # Key signals
                    st.subheader("Key Technical Signals")
                    for signal in tech_analysis.signals[:5]:  # Top 5 signals
                        signal_class = "signal-buy" if "BUY" in signal.signal_type.value else \
                                     "signal-sell" if "SELL" in signal.signal_type.value else "signal-hold"
                        
                        st.markdown(
                            f'<div class="{signal_class}">'
                            f'{signal.indicator}: {signal.signal_type.value} '
                            f'(Strength: {signal.strength:.2f}) - {signal.message}'
                            f'</div>',
                            unsafe_allow_html=True
                        )
                    
                except Exception as e:
                    st.error(f"Error analyzing {analysis_symbol}: {e}")
    
    # Tab 5: AI Insights
    with tab5:
        st.header("AI-Powered Market Insights")
        
        if st.button("🤖 Generate AI Market Analysis", type="primary"):
            with st.spinner("Generating AI analysis..."):
                try:
                    ai_analysis = engine.ai_analyzer.get_daily_market_analysis(selected_symbols[:10])
                    
                    st.subheader("Daily Market Analysis")
                    st.markdown(ai_analysis)
                    
                except Exception as e:
                    st.error(f"Error generating AI analysis: {e}")
        
        # AI-powered stock recommendations
        st.subheader("AI Stock Recommendations")
        
        if selected_symbols and st.button("Get AI Recommendations"):
            with st.spinner("Getting AI recommendations..."):
                try:
                    # Run analysis first
                    analysis_results = run_analysis(engine, selected_symbols[:5])  # Limit for speed
                    
                    if analysis_results:
                        ai_recommendations = engine.ai_analyzer.get_trade_recommendations(
                            list(analysis_results.values()),
                            max_recommendations=3
                        )
                        
                        if ai_recommendations:
                            for i, rec in enumerate(ai_recommendations, 1):
                                with st.expander(f"Recommendation {i}: {rec['symbol']}"):
                                    ai_result = rec['recommendation']
                                    
                                    col1, col2 = st.columns(2)
                                    
                                    with col1:
                                        st.markdown(f"**Recommendation:** {ai_result.recommendation.value}")
                                        st.markdown(f"**Confidence:** {ai_result.confidence:.2f}")
                                        st.markdown(f"**Risk Assessment:** {ai_result.risk_assessment}")
                                        st.markdown(f"**Market Sentiment:** {ai_result.market_sentiment}")
                                    
                                    with col2:
                                        if ai_result.price_targets:
                                            st.markdown("**Price Targets:**")
                                            for target, price in ai_result.price_targets.items():
                                                st.markdown(f"- {target.replace('_', ' ').title()}: ₹{price:.2f}")
                                    
                                    st.markdown(f"**Reasoning:** {ai_result.reasoning}")
                                    
                                    if ai_result.key_factors:
                                        st.markdown("**Key Factors:**")
                                        for factor in ai_result.key_factors:
                                            st.markdown(f"• {factor}")
                        else:
                            st.info("No AI recommendations available at this time.")
                    else:
                        st.warning("Please run technical analysis first.")
                        
                except Exception as e:
                    st.error(f"Error getting AI recommendations: {e}")
    
    # Footer
    st.markdown("---")
    st.markdown(
        f"<div style='text-align: center; color: #666;'>"
        f"Swing Trading System v1.0 | Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
        f"Market: {'🟢 Open' if market_status['is_open'] else '🔴 Closed'}"
        f"</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
