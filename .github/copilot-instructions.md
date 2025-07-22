<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Swing Trading System - Copilot Instructions

This is a professional swing trading system for Indian stocks with the following characteristics:

## Project Context
- **Target Market**: Indian stocks (NSE/BSE)
- **Trading Style**: Swing trading with 1-day timeframe
- **Risk Management**: Comprehensive with stop-loss, take-profit, and trailing stops
- **AI Integration**: Uses Gemini API for trade analysis and recommendations

## Code Standards
- Follow PEP 8 for Python code style
- Use type hints for all function parameters and return values
- Implement proper error handling and logging
- Write comprehensive docstrings for all classes and methods
- Use dataclasses for configuration and data structures

## Architecture Patterns
- Use dependency injection for services
- Implement repository pattern for data access
- Use strategy pattern for different trading algorithms
- Apply observer pattern for real-time updates

## Trading System Components
1. **Technical Analysis**: RSI, MACD, Bollinger Bands, Moving Averages, Volume indicators
2. **Risk Management**: Position sizing, stop-loss, take-profit, trailing stops
3. **Data Management**: Stock data fetching, storage, and real-time updates
4. **AI Analysis**: Gemini API integration for trade recommendations
5. **Portfolio Management**: Position tracking, P&L calculation, risk metrics

## Key Considerations
- Always validate data before processing
- Implement proper logging for audit trails
- Use configuration files for trading parameters
- Ensure thread-safe operations for real-time data
- Implement proper exception handling for API failures
