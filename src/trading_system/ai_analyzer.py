"""
AI Analyzer using Gemini API
=============================

Leverages Google's Gemini AI for advanced market analysis and trade recommendations.
"""

import google.generativeai as genai
from typing import Dict, List, Optional, Any
import json
import logging
from dataclasses import dataclass
from datetime import datetime
import pandas as pd

from .config import TradingConfig
from .technical_analysis import TechnicalAnalysisResult, SignalType
from .data_manager import StockData

logger = logging.getLogger(__name__)


@dataclass
class AIAnalysisResult:
    """AI analysis result container."""
    symbol: str
    recommendation: SignalType
    confidence: float
    reasoning: str
    key_factors: List[str]
    price_targets: Dict[str, float]
    risk_assessment: str
    market_sentiment: str
    trade_setup: Optional[Dict[str, Any]] = None


class AIAnalyzer:
    """AI-powered market analysis using Gemini."""
    
    def __init__(self, config: TradingConfig):
        self.config = config
        
        if not config.gemini_api_key:
            raise ValueError("Gemini API key is required")
        
        # Configure Gemini
        genai.configure(api_key=config.gemini_api_key)
        self.model = genai.GenerativeModel(config.ai.model_name)
        
        # Generation config
        self.generation_config = {
            "temperature": config.ai.temperature,
            "top_p": 0.8,
            "top_k": 40,
            "max_output_tokens": config.ai.max_tokens,
        }
    
    def analyze_stock_with_ai(self, 
                             stock_data: StockData, 
                             technical_analysis: TechnicalAnalysisResult,
                             market_context: Optional[Dict] = None) -> AIAnalysisResult:
        """
        Perform comprehensive AI analysis of a stock.
        
        Args:
            stock_data: Stock price data
            technical_analysis: Technical analysis results
            market_context: Additional market context
        
        Returns:
            AIAnalysisResult with AI-generated insights
        """
        try:
            # Prepare data for AI analysis
            analysis_data = self._prepare_analysis_data(stock_data, technical_analysis, market_context)
            
            # Generate AI analysis
            prompt = self._create_analysis_prompt(analysis_data)
            
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )
            
            # Parse AI response
            ai_result = self._parse_ai_response(stock_data.symbol, response.text)
            
            return ai_result
            
        except Exception as e:
            logger.error(f"Error in AI analysis for {stock_data.symbol}: {e}")
            return self._create_fallback_result(stock_data.symbol, technical_analysis)
    
    def get_daily_market_analysis(self, symbols: List[str]) -> str:
        """Get daily market analysis and trading opportunities."""
        try:
            current_date = datetime.now().strftime("%Y-%m-%d")
            
            prompt = f"""
            You are an expert Indian stock market analyst. Provide a comprehensive daily market analysis for {current_date}.

            Focus on:
            1. Overall market sentiment (Nifty 50, Bank Nifty trends)
            2. Key market drivers today (economic data, global factors, sector rotation)
            3. Top sectors to watch
            4. Key levels for major indices
            5. Risk factors and opportunities

            Also analyze these specific stocks for swing trading opportunities: {', '.join(symbols[:10])}

            For each stock, consider:
            - Recent price action and volume
            - Technical setup for swing trading (1-3 day holding period)
            - Risk/reward potential
            - Entry and exit levels

            Provide actionable insights for swing traders with proper risk management perspective.
            Keep analysis concise but comprehensive.
            """
            
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )
            
            return response.text
            
        except Exception as e:
            logger.error(f"Error generating daily market analysis: {e}")
            return "Unable to generate market analysis at this time."
    
    def get_trade_recommendations(self, 
                                 analysis_results: List[TechnicalAnalysisResult],
                                 max_recommendations: int = 5) -> List[Dict[str, Any]]:
        """Get AI-powered trade recommendations from analysis results."""
        try:
            # Filter for high-confidence signals
            potential_trades = []
            
            for analysis in analysis_results:
                if analysis.confidence >= self.config.ai.confidence_threshold:
                    if analysis.overall_signal in [SignalType.BUY, SignalType.STRONG_BUY]:
                        potential_trades.append({
                            'symbol': analysis.symbol,
                            'signal': analysis.overall_signal.value,
                            'confidence': analysis.confidence,
                            'technical_analysis': analysis
                        })
            
            # Sort by confidence
            potential_trades.sort(key=lambda x: x['confidence'], reverse=True)
            
            # Generate AI recommendations for top candidates
            recommendations = []
            
            for trade in potential_trades[:max_recommendations]:
                try:
                    ai_analysis = self._analyze_trade_opportunity(trade)
                    if ai_analysis:
                        recommendations.append({
                            'symbol': trade['symbol'],
                            'recommendation': ai_analysis,
                            'technical_confidence': trade['confidence'],
                            'ai_confidence': ai_analysis.confidence,
                            'combined_score': (trade['confidence'] + ai_analysis.confidence) / 2
                        })
                except Exception as e:
                    logger.error(f"Error analyzing {trade['symbol']}: {e}")
                    continue
            
            # Sort by combined score
            recommendations.sort(key=lambda x: x['combined_score'], reverse=True)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating trade recommendations: {e}")
            return []
    
    def _prepare_analysis_data(self, 
                              stock_data: StockData, 
                              technical_analysis: TechnicalAnalysisResult,
                              market_context: Optional[Dict]) -> Dict[str, Any]:
        """Prepare data for AI analysis."""
        # Get recent price data
        recent_data = stock_data.data.tail(20)
        
        # Calculate key metrics
        current_price = recent_data['Close'].iloc[-1]
        price_change = ((current_price - recent_data['Close'].iloc[-2]) / recent_data['Close'].iloc[-2]) * 100
        volume_avg = recent_data['Volume'].mean()
        current_volume = recent_data['Volume'].iloc[-1]
        volume_ratio = current_volume / volume_avg
        
        # Price levels
        high_20 = recent_data['High'].max()
        low_20 = recent_data['Low'].min()
        
        return {
            'symbol': stock_data.symbol,
            'current_price': current_price,
            'price_change_1d': price_change,
            'volume_ratio': volume_ratio,
            'high_20d': high_20,
            'low_20d': low_20,
            'technical_signal': technical_analysis.overall_signal.value,
            'technical_confidence': technical_analysis.confidence,
            'key_indicators': {
                'rsi': technical_analysis.indicators.get('RSI', pd.Series()).iloc[-1] if 'RSI' in technical_analysis.indicators else None,
                'macd': technical_analysis.indicators.get('MACD', pd.Series()).iloc[-1] if 'MACD' in technical_analysis.indicators else None,
                'bb_position': technical_analysis.indicators.get('BB_Position', pd.Series()).iloc[-1] if 'BB_Position' in technical_analysis.indicators else None
            },
            'key_levels': technical_analysis.key_levels,
            'risk_reward': technical_analysis.risk_reward,
            'market_context': market_context or {}
        }
    
    def _create_analysis_prompt(self, data: Dict[str, Any]) -> str:
        """Create detailed analysis prompt for Gemini."""
        return f"""
        You are an expert swing trader and technical analyst specializing in Indian stock markets. 
        Analyze the following stock data and provide a comprehensive trading recommendation.

        Stock: {data['symbol']}
        Current Price: ₹{data['current_price']:.2f}
        1-Day Change: {data['price_change_1d']:.2f}%
        Volume Ratio: {data['volume_ratio']:.2f}x average
        20-Day Range: ₹{data['low_20d']:.2f} - ₹{data['high_20d']:.2f}

        Technical Analysis Summary:
        - Overall Signal: {data['technical_signal']}
        - Confidence: {data['technical_confidence']:.2f}
        - RSI: {data['key_indicators'].get('rsi', 'N/A')}
        - MACD: {data['key_indicators'].get('macd', 'N/A')}
        - Bollinger Position: {data['key_indicators'].get('bb_position', 'N/A')}

        Key Levels:
        - Support: ₹{data['key_levels'].get('support_1', 0):.2f}
        - Resistance: ₹{data['key_levels'].get('resistance_1', 0):.2f}
        - Stop Loss: ₹{data['risk_reward'].get('stop_loss', 0):.2f}
        - Take Profit: ₹{data['risk_reward'].get('take_profit', 0):.2f}
        - Risk/Reward Ratio: 1:{data['risk_reward'].get('risk_reward_ratio', 0):.2f}

        Please provide your analysis in the following JSON format:
        {{
            "recommendation": "BUY/SELL/HOLD",
            "confidence": 0.85,
            "reasoning": "Detailed explanation of your recommendation",
            "key_factors": ["Factor 1", "Factor 2", "Factor 3"],
            "price_targets": {{
                "entry": 1250.00,
                "stop_loss": 1200.00,
                "target_1": 1300.00,
                "target_2": 1350.00
            }},
            "risk_assessment": "Low/Medium/High risk assessment",
            "market_sentiment": "Bullish/Bearish/Neutral sentiment",
            "trade_setup": {{
                "timeframe": "1-3 days",
                "setup_type": "Breakout/Pullback/Reversal",
                "confidence_level": "High/Medium/Low"
            }}
        }}

        Consider:
        1. Current market conditions in Indian markets
        2. Sector-specific factors
        3. Technical setup quality
        4. Risk management principles
        5. Swing trading timeframe (1-3 days typical hold)

        Be specific with price levels and provide clear reasoning for your recommendation.
        """
    
    def _parse_ai_response(self, symbol: str, response_text: str) -> AIAnalysisResult:
        """Parse AI response and create structured result."""
        try:
            # Try to extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start != -1 and json_end != -1:
                json_text = response_text[json_start:json_end]
                parsed_data = json.loads(json_text)
                
                # Map recommendation to SignalType
                rec_map = {
                    'BUY': SignalType.BUY,
                    'STRONG_BUY': SignalType.STRONG_BUY,
                    'SELL': SignalType.SELL,
                    'STRONG_SELL': SignalType.STRONG_SELL,
                    'HOLD': SignalType.HOLD
                }
                
                recommendation = rec_map.get(parsed_data.get('recommendation', 'HOLD'), SignalType.HOLD)
                
                return AIAnalysisResult(
                    symbol=symbol,
                    recommendation=recommendation,
                    confidence=float(parsed_data.get('confidence', 0.5)),
                    reasoning=parsed_data.get('reasoning', ''),
                    key_factors=parsed_data.get('key_factors', []),
                    price_targets=parsed_data.get('price_targets', {}),
                    risk_assessment=parsed_data.get('risk_assessment', 'Medium'),
                    market_sentiment=parsed_data.get('market_sentiment', 'Neutral'),
                    trade_setup=parsed_data.get('trade_setup', {})
                )
            else:
                # Fallback parsing if JSON is malformed
                return self._parse_text_response(symbol, response_text)
                
        except Exception as e:
            logger.error(f"Error parsing AI response for {symbol}: {e}")
            return self._parse_text_response(symbol, response_text)
    
    def _parse_text_response(self, symbol: str, response_text: str) -> AIAnalysisResult:
        """Fallback text parsing when JSON parsing fails."""
        # Simple keyword-based parsing
        response_lower = response_text.lower()
        
        if 'strong buy' in response_lower or 'strongly recommend buying' in response_lower:
            recommendation = SignalType.STRONG_BUY
            confidence = 0.8
        elif 'buy' in response_lower or 'bullish' in response_lower:
            recommendation = SignalType.BUY
            confidence = 0.6
        elif 'strong sell' in response_lower or 'strongly recommend selling' in response_lower:
            recommendation = SignalType.STRONG_SELL
            confidence = 0.8
        elif 'sell' in response_lower or 'bearish' in response_lower:
            recommendation = SignalType.SELL
            confidence = 0.6
        else:
            recommendation = SignalType.HOLD
            confidence = 0.5
        
        return AIAnalysisResult(
            symbol=symbol,
            recommendation=recommendation,
            confidence=confidence,
            reasoning=response_text[:500],  # First 500 chars
            key_factors=['AI analysis completed'],
            price_targets={},
            risk_assessment='Medium',
            market_sentiment='Neutral'
        )
    
    def _analyze_trade_opportunity(self, trade_data: Dict[str, Any]) -> Optional[AIAnalysisResult]:
        """Analyze a specific trade opportunity with AI."""
        try:
            technical_analysis = trade_data['technical_analysis']
            
            prompt = f"""
            Analyze this swing trading opportunity for {trade_data['symbol']}:
            
            Technical Signal: {trade_data['signal']} (Confidence: {trade_data['confidence']:.2f})
            Current Price: ₹{technical_analysis.key_levels.get('current_price', 0):.2f}
            Support: ₹{technical_analysis.key_levels.get('support_1', 0):.2f}
            Resistance: ₹{technical_analysis.key_levels.get('resistance_1', 0):.2f}
            R:R Ratio: 1:{technical_analysis.risk_reward.get('risk_reward_ratio', 0):.2f}
            
            Key Technical Signals:
            {'; '.join([f"{s.indicator}: {s.signal_type.value}" for s in technical_analysis.signals[:3]])}
            
            Provide a concise analysis focusing on:
            1. Trade viability for swing trading
            2. Key risk factors
            3. Optimal entry strategy
            4. Expected holding period
            
            Rate confidence 0-1 and provide specific price levels.
            """
            
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )
            
            return self._parse_ai_response(trade_data['symbol'], response.text)
            
        except Exception as e:
            logger.error(f"Error analyzing trade opportunity: {e}")
            return None
    
    def _create_fallback_result(self, symbol: str, technical_analysis: TechnicalAnalysisResult) -> AIAnalysisResult:
        """Create fallback result when AI analysis fails."""
        return AIAnalysisResult(
            symbol=symbol,
            recommendation=technical_analysis.overall_signal,
            confidence=max(technical_analysis.confidence * 0.8, 0.3),  # Reduce confidence for fallback
            reasoning="Technical analysis based recommendation (AI analysis unavailable)",
            key_factors=["Technical indicators", "Price action", "Volume analysis"],
            price_targets={
                'stop_loss': technical_analysis.risk_reward.get('stop_loss', 0),
                'take_profit': technical_analysis.risk_reward.get('take_profit', 0)
            },
            risk_assessment="Medium",
            market_sentiment="Neutral"
        )
    
    def format_ai_analysis(self, analysis: AIAnalysisResult) -> str:
        """Format AI analysis for display."""
        formatted = f"AI Analysis for {analysis.symbol}\n"
        formatted += f"{'='*50}\n"
        formatted += f"Recommendation: {analysis.recommendation.value} (Confidence: {analysis.confidence:.2f})\n"
        formatted += f"Market Sentiment: {analysis.market_sentiment}\n"
        formatted += f"Risk Assessment: {analysis.risk_assessment}\n\n"
        
        formatted += f"Reasoning:\n{analysis.reasoning}\n\n"
        
        if analysis.key_factors:
            formatted += f"Key Factors:\n"
            for factor in analysis.key_factors:
                formatted += f"• {factor}\n"
            formatted += "\n"
        
        if analysis.price_targets:
            formatted += f"Price Targets:\n"
            for target, price in analysis.price_targets.items():
                formatted += f"  {target.replace('_', ' ').title()}: ₹{price:.2f}\n"
        
        if analysis.trade_setup:
            formatted += f"\nTrade Setup:\n"
            for key, value in analysis.trade_setup.items():
                formatted += f"  {key.replace('_', ' ').title()}: {value}\n"
        
        return formatted
