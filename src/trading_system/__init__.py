"""
Enterprise Swing Trading System for Indian Stocks
==================================================

A comprehensive trading system designed for swing trading Indian stocks with:
- Advanced technical analysis
- Risk management with stop-loss and take-profit
- AI-powered trade analysis using Gemini API
- Real-time monitoring and alerts
- Professional portfolio management

Author: Trading System
Version: 1.0.0
"""

from .config import TradingConfig
from .data_manager import DataManager
from .technical_analysis import TechnicalAnalyzer
from .risk_manager import RiskManager
from .ai_analyzer import AIAnalyzer
from .portfolio_manager import PortfolioManager
from .trading_engine import TradingEngine

__version__ = "1.0.0"
__author__ = "Trading System"

__all__ = [
    "TradingConfig",
    "DataManager", 
    "TechnicalAnalyzer",
    "RiskManager",
    "AIAnalyzer",
    "PortfolioManager",
    "TradingEngine"
]
