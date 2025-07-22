"""
Trading System Configuration
============================

Central configuration management for the trading system.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
import os
from dotenv import load_dotenv

load_dotenv()


@dataclass
class RiskConfig:
    """Risk management configuration."""
    risk_per_trade: float = 0.02  # 2% risk per trade
    max_positions: int = 5
    max_portfolio_risk: float = 0.10  # 10% total portfolio risk
    stop_loss_pct: float = 0.08  # 8% stop loss
    take_profit_pct: float = 0.16  # 16% take profit (2:1 reward:risk)
    trailing_stop_pct: float = 0.04  # 4% trailing stop


@dataclass
class TechnicalConfig:
    """Technical analysis configuration."""
    rsi_period: int = 14
    rsi_oversold: int = 30
    rsi_overbought: int = 70
    
    macd_fast: int = 12
    macd_slow: int = 26
    macd_signal: int = 9
    
    bb_period: int = 20
    bb_std: float = 2.0
    
    volume_ma_period: int = 20
    volume_spike_threshold: float = 1.5
    
    ema_short: int = 9
    ema_long: int = 21
    sma_trend: int = 50


@dataclass
class AIConfig:
    """AI analysis configuration."""
    model_name: str = "gemini-1.5-flash"
    temperature: float = 0.1
    max_tokens: int = 1000
    confidence_threshold: float = 0.7


@dataclass
class DataConfig:
    """Data source configuration."""
    data_source: str = "yfinance"
    timeframe: str = "1d"
    lookback_days: int = 200
    market_hours_start: str = "09:15"
    market_hours_end: str = "15:30"
    timezone: str = "Asia/Kolkata"


@dataclass
class NotificationConfig:
    """Notification configuration."""
    telegram_enabled: bool = False
    discord_enabled: bool = False
    email_enabled: bool = False
    desktop_enabled: bool = True


class TradingConfig:
    """Main trading system configuration."""
    
    def __init__(self):
        self.risk = RiskConfig()
        self.technical = TechnicalConfig()
        self.ai = AIConfig()
        self.data = DataConfig()
        self.notifications = NotificationConfig()
        
        # Environment variables
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.capital = float(os.getenv("CAPITAL", "100000"))
        
        # Backtesting attributes
        self.max_positions = self.risk.max_positions
        self.risk_per_trade = self.risk.risk_per_trade
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///trading_system.db")
        
        # Telegram configuration
        self.telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")
        
        # Discord configuration
        self.discord_webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
        
        # Load from environment if available
        self._load_from_env()
    
    def _load_from_env(self) -> None:
        """Load configuration from environment variables."""
        if risk_per_trade := os.getenv("RISK_PER_TRADE"):
            self.risk.risk_per_trade = float(risk_per_trade)
        
        if max_positions := os.getenv("MAX_POSITIONS"):
            self.risk.max_positions = int(max_positions)
    
    def validate(self) -> bool:
        """Validate configuration."""
        errors = []
        
        if not self.gemini_api_key:
            errors.append("GEMINI_API_KEY is required")
        
        if self.capital <= 0:
            errors.append("Capital must be positive")
        
        if self.risk.risk_per_trade <= 0 or self.risk.risk_per_trade > 0.05:
            errors.append("Risk per trade should be between 0 and 5%")
        
        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")
        
        return True
    
    def get_indian_stock_symbols(self) -> List[str]:
        """Get list of popular Indian stock symbols for NSE."""
        return [
            # Nifty 50 major stocks
            "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "HINDUNILVR.NS",
            "ICICIBANK.NS", "KOTAKBANK.NS", "HDFC.NS", "ITC.NS", "LT.NS",
            "SBIN.NS", "BAJFINANCE.NS", "BHARTIARTL.NS", "ASIANPAINT.NS",
            "MARUTI.NS", "AXISBANK.NS", "NESTLEIND.NS", "WIPRO.NS", "ULTRACEMCO.NS",
            "TITAN.NS", "SUNPHARMA.NS", "POWERGRID.NS", "NTPC.NS", "TECHM.NS",
            "M&M.NS", "TATAMOTORS.NS", "HCLTECH.NS", "DIVISLAB.NS", "GRASIM.NS",
            "INDUSINDBK.NS", "CIPLA.NS", "COALINDIA.NS", "DRREDDY.NS", "EICHERMOT.NS",
            "JSWSTEEL.NS", "BRITANNIA.NS", "BPCL.NS", "ADANIENT.NS", "APOLLOHOSP.NS",
            "TATASTEEL.NS", "BAJAJFINSV.NS", "ONGC.NS", "HEROMOTOCO.NS", "HINDALCO.NS",
            "SHREECEM.NS", "UPL.NS", "SBILIFE.NS", "BAJAJ-AUTO.NS", "TATACONSUM.NS"
        ]
    
    def to_dict(self) -> Dict:
        """Convert configuration to dictionary."""
        return {
            "risk": self.risk.__dict__,
            "technical": self.technical.__dict__,
            "ai": self.ai.__dict__,
            "data": self.data.__dict__,
            "notifications": self.notifications.__dict__,
            "capital": self.capital
        }
