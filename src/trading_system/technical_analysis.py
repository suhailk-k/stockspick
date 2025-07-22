"""
Technical Analysis Engine
=========================

Comprehensive technical analysis for swing trading with multiple indicators.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, NamedTuple
import ta
from dataclasses import dataclass
from enum import Enum
import logging

from .config import TradingConfig
from .data_manager import StockData

logger = logging.getLogger(__name__)


class SignalType(Enum):
    """Signal types for trading decisions."""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
    STRONG_BUY = "STRONG_BUY"
    STRONG_SELL = "STRONG_SELL"


@dataclass
class TechnicalSignal:
    """Container for technical analysis signals."""
    signal_type: SignalType
    strength: float  # 0-1 scale
    indicator: str
    value: float
    message: str
    timestamp: pd.Timestamp


@dataclass
class TechnicalAnalysisResult:
    """Complete technical analysis results."""
    symbol: str
    overall_signal: SignalType
    confidence: float
    signals: List[TechnicalSignal]
    key_levels: Dict[str, float]
    risk_reward: Dict[str, float]
    indicators: Dict[str, any]


class TechnicalAnalyzer:
    """Advanced technical analysis engine for swing trading."""
    
    def __init__(self, config: TradingConfig):
        self.config = config
    
    def analyze_stock(self, stock_data: StockData) -> TechnicalAnalysisResult:
        """
        Perform comprehensive technical analysis on a stock.
        
        Args:
            stock_data: StockData object containing OHLCV data
        
        Returns:
            TechnicalAnalysisResult with signals and analysis
        """
        try:
            data = stock_data.data.copy()
            
            # Calculate all indicators
            indicators = self._calculate_all_indicators(data)
            
            # Generate signals from each indicator
            signals = self._generate_signals(data, indicators)
            
            # Calculate key levels
            key_levels = self._calculate_key_levels(data)
            
            # Calculate risk/reward ratios
            risk_reward = self._calculate_risk_reward(data, key_levels)
            
            # Determine overall signal
            overall_signal, confidence = self._determine_overall_signal(signals)
            
            return TechnicalAnalysisResult(
                symbol=stock_data.symbol,
                overall_signal=overall_signal,
                confidence=confidence,
                signals=signals,
                key_levels=key_levels,
                risk_reward=risk_reward,
                indicators=indicators
            )
            
        except Exception as e:
            logger.error(f"Error analyzing {stock_data.symbol}: {e}")
            raise
    
    def _calculate_all_indicators(self, data: pd.DataFrame) -> Dict[str, any]:
        """Calculate all technical indicators."""
        indicators = {}
        
        try:
            # Price data
            high = data['High']
            low = data['Low']
            close = data['Close']
            volume = data['Volume']
            
            # Moving Averages
            indicators['SMA_20'] = ta.trend.sma_indicator(close, window=20)
            indicators['SMA_50'] = ta.trend.sma_indicator(close, window=50)
            indicators['EMA_9'] = ta.trend.ema_indicator(close, window=self.config.technical.ema_short)
            indicators['EMA_21'] = ta.trend.ema_indicator(close, window=self.config.technical.ema_long)
            
            # RSI
            indicators['RSI'] = ta.momentum.rsi(close, window=self.config.technical.rsi_period)
            
            # MACD
            macd = ta.trend.MACD(close,
                               window_slow=self.config.technical.macd_slow,
                               window_fast=self.config.technical.macd_fast,
                               window_sign=self.config.technical.macd_signal)
            indicators['MACD'] = macd.macd()
            indicators['MACD_Signal'] = macd.macd_signal()
            indicators['MACD_Histogram'] = macd.macd_diff()
            
            # Bollinger Bands
            bb = ta.volatility.BollingerBands(close,
                                            window=self.config.technical.bb_period,
                                            window_dev=self.config.technical.bb_std)
            indicators['BB_Upper'] = bb.bollinger_hband()
            indicators['BB_Middle'] = bb.bollinger_mavg()
            indicators['BB_Lower'] = bb.bollinger_lband()
            indicators['BB_Width'] = bb.bollinger_wband()
            indicators['BB_Position'] = (close - indicators['BB_Lower']) / (indicators['BB_Upper'] - indicators['BB_Lower'])
            
            # Stochastic Oscillator
            stoch = ta.momentum.StochasticOscillator(high, low, close)
            indicators['Stoch_K'] = stoch.stoch()
            indicators['Stoch_D'] = stoch.stoch_signal()
            
            # Average True Range (Volatility)
            indicators['ATR'] = ta.volatility.average_true_range(high, low, close, window=14)
            
            # Volume indicators
            indicators['Volume_SMA'] = volume.rolling(window=self.config.technical.volume_ma_period).mean()
            indicators['Volume_Ratio'] = volume / indicators['Volume_SMA']
            
            # Support and Resistance using Pivot Points
            indicators['Pivot'] = (high + low + close) / 3
            indicators['R1'] = 2 * indicators['Pivot'] - low
            indicators['S1'] = 2 * indicators['Pivot'] - high
            indicators['R2'] = indicators['Pivot'] + (high - low)
            indicators['S2'] = indicators['Pivot'] - (high - low)
            
            # Williams %R
            indicators['Williams_R'] = ta.momentum.williams_r(high, low, close, lbp=14)
            
            # Commodity Channel Index
            indicators['CCI'] = ta.trend.cci(high, low, close, window=20)
            
            # Money Flow Index
            indicators['MFI'] = ta.volume.money_flow_index(high, low, close, volume, window=14)
            
            # ADX (Trend Strength)
            indicators['ADX'] = ta.trend.adx(high, low, close, window=14)
            
            # Price Rate of Change
            indicators['ROC'] = ta.momentum.roc(close, window=10)
            
            return indicators
            
        except Exception as e:
            logger.error(f"Error calculating indicators: {e}")
            return {}
    
    def _generate_signals(self, data: pd.DataFrame, indicators: Dict[str, any]) -> List[TechnicalSignal]:
        """Generate trading signals from indicators."""
        signals = []
        current_price = data['Close'].iloc[-1]
        timestamp = data.index[-1]
        
        try:
            # RSI Signals
            current_rsi = indicators['RSI'].iloc[-1]
            if current_rsi < self.config.technical.rsi_oversold:
                signals.append(TechnicalSignal(
                    signal_type=SignalType.BUY,
                    strength=min((self.config.technical.rsi_oversold - current_rsi) / 10, 1.0),
                    indicator="RSI",
                    value=current_rsi,
                    message=f"RSI oversold at {current_rsi:.2f}",
                    timestamp=timestamp
                ))
            elif current_rsi > self.config.technical.rsi_overbought:
                signals.append(TechnicalSignal(
                    signal_type=SignalType.SELL,
                    strength=min((current_rsi - self.config.technical.rsi_overbought) / 10, 1.0),
                    indicator="RSI",
                    value=current_rsi,
                    message=f"RSI overbought at {current_rsi:.2f}",
                    timestamp=timestamp
                ))
            
            # MACD Signals
            macd_current = indicators['MACD'].iloc[-1]
            macd_signal = indicators['MACD_Signal'].iloc[-1]
            macd_prev = indicators['MACD'].iloc[-2]
            macd_signal_prev = indicators['MACD_Signal'].iloc[-2]
            
            # MACD Crossover
            if macd_prev <= macd_signal_prev and macd_current > macd_signal:
                signals.append(TechnicalSignal(
                    signal_type=SignalType.BUY,
                    strength=0.7,
                    indicator="MACD",
                    value=macd_current - macd_signal,
                    message="MACD bullish crossover",
                    timestamp=timestamp
                ))
            elif macd_prev >= macd_signal_prev and macd_current < macd_signal:
                signals.append(TechnicalSignal(
                    signal_type=SignalType.SELL,
                    strength=0.7,
                    indicator="MACD",
                    value=macd_current - macd_signal,
                    message="MACD bearish crossover",
                    timestamp=timestamp
                ))
            
            # Moving Average Signals
            ema9 = indicators['EMA_9'].iloc[-1]
            ema21 = indicators['EMA_21'].iloc[-1]
            sma50 = indicators['SMA_50'].iloc[-1]
            
            # EMA Crossover
            ema9_prev = indicators['EMA_9'].iloc[-2]
            ema21_prev = indicators['EMA_21'].iloc[-2]
            
            if ema9_prev <= ema21_prev and ema9 > ema21:
                signals.append(TechnicalSignal(
                    signal_type=SignalType.BUY,
                    strength=0.6,
                    indicator="EMA_Crossover",
                    value=(ema9 - ema21) / current_price * 100,
                    message="EMA 9/21 bullish crossover",
                    timestamp=timestamp
                ))
            elif ema9_prev >= ema21_prev and ema9 < ema21:
                signals.append(TechnicalSignal(
                    signal_type=SignalType.SELL,
                    strength=0.6,
                    indicator="EMA_Crossover",
                    value=(ema9 - ema21) / current_price * 100,
                    message="EMA 9/21 bearish crossover",
                    timestamp=timestamp
                ))
            
            # Price vs SMA50 trend
            if current_price > sma50 * 1.02:  # 2% above SMA50
                signals.append(TechnicalSignal(
                    signal_type=SignalType.BUY,
                    strength=0.4,
                    indicator="SMA50_Trend",
                    value=(current_price - sma50) / sma50 * 100,
                    message="Price strong above SMA50",
                    timestamp=timestamp
                ))
            elif current_price < sma50 * 0.98:  # 2% below SMA50
                signals.append(TechnicalSignal(
                    signal_type=SignalType.SELL,
                    strength=0.4,
                    indicator="SMA50_Trend",
                    value=(current_price - sma50) / sma50 * 100,
                    message="Price weak below SMA50",
                    timestamp=timestamp
                ))
            
            # Bollinger Bands Signals
            bb_position = indicators['BB_Position'].iloc[-1]
            if bb_position < 0.1:  # Near lower band
                signals.append(TechnicalSignal(
                    signal_type=SignalType.BUY,
                    strength=0.5,
                    indicator="Bollinger_Bands",
                    value=bb_position,
                    message="Price near Bollinger lower band",
                    timestamp=timestamp
                ))
            elif bb_position > 0.9:  # Near upper band
                signals.append(TechnicalSignal(
                    signal_type=SignalType.SELL,
                    strength=0.5,
                    indicator="Bollinger_Bands",
                    value=bb_position,
                    message="Price near Bollinger upper band",
                    timestamp=timestamp
                ))
            
            # Volume Signals
            volume_ratio = indicators['Volume_Ratio'].iloc[-1]
            if volume_ratio > self.config.technical.volume_spike_threshold:
                # High volume can strengthen other signals
                for signal in signals:
                    signal.strength = min(signal.strength * 1.2, 1.0)
                
                signals.append(TechnicalSignal(
                    signal_type=SignalType.HOLD,
                    strength=0.3,
                    indicator="Volume",
                    value=volume_ratio,
                    message=f"High volume spike: {volume_ratio:.2f}x average",
                    timestamp=timestamp
                ))
            
            # Stochastic Signals
            stoch_k = indicators['Stoch_K'].iloc[-1]
            if stoch_k < 20:
                signals.append(TechnicalSignal(
                    signal_type=SignalType.BUY,
                    strength=0.4,
                    indicator="Stochastic",
                    value=stoch_k,
                    message="Stochastic oversold",
                    timestamp=timestamp
                ))
            elif stoch_k > 80:
                signals.append(TechnicalSignal(
                    signal_type=SignalType.SELL,
                    strength=0.4,
                    indicator="Stochastic",
                    value=stoch_k,
                    message="Stochastic overbought",
                    timestamp=timestamp
                ))
            
            return signals
            
        except Exception as e:
            logger.error(f"Error generating signals: {e}")
            return []
    
    def _calculate_key_levels(self, data: pd.DataFrame) -> Dict[str, float]:
        """Calculate key support and resistance levels."""
        try:
            current_price = data['Close'].iloc[-1]
            high_20 = data['High'].rolling(20).max().iloc[-1]
            low_20 = data['Low'].rolling(20).min().iloc[-1]
            
            # Recent highs and lows
            high_5 = data['High'].rolling(5).max().iloc[-1]
            low_5 = data['Low'].rolling(5).min().iloc[-1]
            
            # ATR for dynamic levels
            atr = (data['High'] - data['Low']).rolling(14).mean().iloc[-1]
            
            return {
                'current_price': current_price,
                'resistance_1': high_5,
                'resistance_2': high_20,
                'support_1': low_5,
                'support_2': low_20,
                'atr': atr,
                'dynamic_resistance': current_price + (atr * 2),
                'dynamic_support': current_price - (atr * 2)
            }
            
        except Exception as e:
            logger.error(f"Error calculating key levels: {e}")
            return {}
    
    def _calculate_risk_reward(self, data: pd.DataFrame, key_levels: Dict[str, float]) -> Dict[str, float]:
        """Calculate risk/reward ratios based on key levels."""
        try:
            current_price = key_levels.get('current_price', data['Close'].iloc[-1])
            atr = key_levels.get('atr', 0)
            
            # Standard stop loss and take profit based on configuration
            stop_loss_price = current_price * (1 - self.config.risk.stop_loss_pct)
            take_profit_price = current_price * (1 + self.config.risk.take_profit_pct)
            
            # Dynamic levels based on ATR
            atr_stop_loss = current_price - (atr * 2)
            atr_take_profit = current_price + (atr * 4)  # 2:1 ratio
            
            risk = current_price - max(stop_loss_price, atr_stop_loss)
            reward = min(take_profit_price, atr_take_profit) - current_price
            
            risk_reward_ratio = reward / risk if risk > 0 else 0
            
            return {
                'stop_loss': max(stop_loss_price, atr_stop_loss),
                'take_profit': min(take_profit_price, atr_take_profit),
                'risk_amount': risk,
                'reward_amount': reward,
                'risk_reward_ratio': risk_reward_ratio,
                'risk_percentage': (risk / current_price) * 100,
                'reward_percentage': (reward / current_price) * 100
            }
            
        except Exception as e:
            logger.error(f"Error calculating risk/reward: {e}")
            return {}
    
    def _determine_overall_signal(self, signals: List[TechnicalSignal]) -> Tuple[SignalType, float]:
        """Determine overall signal from individual signals."""
        if not signals:
            return SignalType.HOLD, 0.0
        
        # Weight signals by strength and type
        buy_score = sum(signal.strength for signal in signals if signal.signal_type == SignalType.BUY)
        sell_score = sum(signal.strength for signal in signals if signal.signal_type == SignalType.SELL)
        
        buy_count = len([s for s in signals if s.signal_type == SignalType.BUY])
        sell_count = len([s for s in signals if s.signal_type == SignalType.SELL])
        
        # Calculate final scores
        total_signals = len(signals)
        if total_signals == 0:
            return SignalType.HOLD, 0.0
        
        net_score = buy_score - sell_score
        max_possible_score = total_signals * 1.0  # Maximum strength is 1.0
        
        confidence = abs(net_score) / max_possible_score if max_possible_score > 0 else 0
        confidence = min(confidence, 1.0)
        
        # Determine signal type
        if net_score > 1.5:
            signal_type = SignalType.STRONG_BUY if confidence > 0.7 else SignalType.BUY
        elif net_score < -1.5:
            signal_type = SignalType.STRONG_SELL if confidence > 0.7 else SignalType.SELL
        else:
            signal_type = SignalType.HOLD
        
        return signal_type, confidence
    
    def get_trading_summary(self, analysis: TechnicalAnalysisResult) -> str:
        """Get a human-readable trading summary."""
        summary = f"Technical Analysis for {analysis.symbol}\n"
        summary += f"{'='*50}\n"
        summary += f"Overall Signal: {analysis.overall_signal.value} (Confidence: {analysis.confidence:.2f})\n\n"
        
        # Key levels
        levels = analysis.key_levels
        summary += f"Key Levels:\n"
        summary += f"  Current Price: ₹{levels.get('current_price', 0):.2f}\n"
        summary += f"  Support 1: ₹{levels.get('support_1', 0):.2f}\n"
        summary += f"  Resistance 1: ₹{levels.get('resistance_1', 0):.2f}\n\n"
        
        # Risk/Reward
        rr = analysis.risk_reward
        summary += f"Risk/Reward:\n"
        summary += f"  Stop Loss: ₹{rr.get('stop_loss', 0):.2f} (-{rr.get('risk_percentage', 0):.2f}%)\n"
        summary += f"  Take Profit: ₹{rr.get('take_profit', 0):.2f} (+{rr.get('reward_percentage', 0):.2f}%)\n"
        summary += f"  R:R Ratio: 1:{rr.get('risk_reward_ratio', 0):.2f}\n\n"
        
        # Top signals
        summary += f"Key Signals:\n"
        for signal in sorted(analysis.signals, key=lambda x: x.strength, reverse=True)[:5]:
            summary += f"  {signal.indicator}: {signal.signal_type.value} ({signal.strength:.2f}) - {signal.message}\n"
        
        return summary
