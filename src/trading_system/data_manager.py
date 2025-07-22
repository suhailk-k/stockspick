"""
Data Manager
============

Handles data fetching, caching, and management for Indian stocks.
"""

import yfinance as yf
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
import sqlite3
from pathlib import Path
import requests
import json

from .config import TradingConfig

logger = logging.getLogger(__name__)


@dataclass
class StockData:
    """Container for stock data."""
    symbol: str
    data: pd.DataFrame
    last_updated: datetime
    
    def __post_init__(self):
        """Validate data after initialization."""
        if self.data.empty:
            raise ValueError(f"No data available for {self.symbol}")
        
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        missing_columns = [col for col in required_columns if col not in self.data.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns for {self.symbol}: {missing_columns}")


class DataManager:
    """Manages stock data fetching and caching."""
    
    def __init__(self, config: TradingConfig):
        self.config = config
        self.cache: Dict[str, StockData] = {}
        self.db_path = Path("data/stock_data.db")
        self.db_path.parent.mkdir(exist_ok=True)
        self._init_database()
    
    def _init_database(self) -> None:
        """Initialize SQLite database for caching."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS stock_data (
                    symbol TEXT,
                    date TEXT,
                    open REAL,
                    high REAL,
                    low REAL,
                    close REAL,
                    volume INTEGER,
                    PRIMARY KEY (symbol, date)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS market_status (
                    date TEXT PRIMARY KEY,
                    is_trading_day BOOLEAN,
                    session_start TEXT,
                    session_end TEXT
                )
            """)
    
    def get_stock_data(self, symbol: str, period: str = "200d") -> StockData:
        """
        Get stock data for a symbol.
        
        Args:
            symbol: Stock symbol (e.g., 'RELIANCE.NS')
            period: Data period ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max')
        
        Returns:
            StockData object with OHLCV data
        """
        try:
            # Check cache first
            if symbol in self.cache:
                cached_data = self.cache[symbol]
                if (datetime.now() - cached_data.last_updated).seconds < 300:  # 5 minutes cache
                    return cached_data
            
            logger.info(f"Fetching data for {symbol}")
            
            # Fetch from Yahoo Finance
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period)
            
            if data.empty:
                raise ValueError(f"No data available for {symbol}")
            
            # Clean and prepare data
            data = self._clean_data(data)
            
            # Cache the data
            stock_data = StockData(
                symbol=symbol,
                data=data,
                last_updated=datetime.now()
            )
            self.cache[symbol] = stock_data
            
            # Store in database
            self._store_data_to_db(symbol, data)
            
            return stock_data
            
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            # Try to get from database as fallback
            return self._get_data_from_db(symbol)
    
    def get_multiple_stocks_data(self, symbols: List[str], period: str = "200d") -> Dict[str, StockData]:
        """
        Get data for multiple stocks.
        
        Args:
            symbols: List of stock symbols
            period: Data period
        
        Returns:
            Dictionary mapping symbols to StockData objects
        """
        results = {}
        
        for symbol in symbols:
            try:
                results[symbol] = self.get_stock_data(symbol, period)
            except Exception as e:
                logger.error(f"Failed to get data for {symbol}: {e}")
                continue
        
        return results
    
    def _clean_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Clean and prepare stock data."""
        # Remove any rows with NaN values
        data = data.dropna()
        
        # Ensure proper column names
        data.columns = [col.title() for col in data.columns]
        
        # Add basic derived columns
        data['HL2'] = (data['High'] + data['Low']) / 2
        data['HLC3'] = (data['High'] + data['Low'] + data['Close']) / 3
        data['OHLC4'] = (data['Open'] + data['High'] + data['Low'] + data['Close']) / 4
        
        # Calculate returns
        data['Returns'] = data['Close'].pct_change()
        data['Log_Returns'] = np.log(data['Close'] / data['Close'].shift(1))
        
        return data
    
    def _store_data_to_db(self, symbol: str, data: pd.DataFrame) -> None:
        """Store data to SQLite database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Prepare data for insertion
                data_to_insert = data.reset_index()
                data_to_insert['Symbol'] = symbol
                data_to_insert = data_to_insert.rename(columns={
                    'Date': 'date',
                    'Symbol': 'symbol',
                    'Open': 'open',
                    'High': 'high', 
                    'Low': 'low',
                    'Close': 'close',
                    'Volume': 'volume',
                    'Adj Close': 'adj_close'
                })
                
                # Insert data (replace existing)
                data_to_insert[['symbol', 'date', 'open', 'high', 'low', 'close', 'volume']].to_sql(
                    'stock_data', conn, if_exists='replace', index=False
                )
                
        except Exception as e:
            logger.error(f"Error storing data to database for {symbol}: {e}")
    
    def _get_data_from_db(self, symbol: str) -> StockData:
        """Get data from SQLite database as fallback."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = "SELECT * FROM stock_data WHERE symbol = ? ORDER BY date"
                data = pd.read_sql(query, conn, params=[symbol], parse_dates=['date'], index_col='date')
                
                if data.empty:
                    raise ValueError(f"No cached data available for {symbol}")
                
                # Rename columns to match expected format
                data = data.rename(columns={
                    'open': 'Open',
                    'high': 'High',
                    'low': 'Low', 
                    'close': 'Close',
                    'volume': 'Volume'
                })
                
                data = self._clean_data(data)
                
                return StockData(
                    symbol=symbol,
                    data=data,
                    last_updated=datetime.now()
                )
                
        except Exception as e:
            logger.error(f"Error getting data from database for {symbol}: {e}")
            raise ValueError(f"Unable to get data for {symbol} from any source")
    
    def is_market_open(self) -> bool:
        """Check if Indian stock market is currently open."""
        now = datetime.now()
        
        # Check if it's a weekday (Monday=0, Sunday=6)
        if now.weekday() >= 5:  # Saturday or Sunday
            return False
        
        # Check market hours (9:15 AM to 3:30 PM IST)
        market_start = now.replace(hour=9, minute=15, second=0, microsecond=0)
        market_end = now.replace(hour=15, minute=30, second=0, microsecond=0)
        
        return market_start <= now <= market_end
    
    def get_market_status(self) -> Dict[str, any]:
        """Get detailed market status information."""
        now = datetime.now()
        
        status = {
            'is_open': self.is_market_open(),
            'current_time': now,
            'is_trading_day': now.weekday() < 5,
            'session_start': now.replace(hour=9, minute=15, second=0, microsecond=0),
            'session_end': now.replace(hour=15, minute=30, second=0, microsecond=0)
        }
        
        if status['is_open']:
            status['status'] = 'OPEN'
        elif status['is_trading_day']:
            if now < status['session_start']:
                status['status'] = 'PRE_MARKET'
                status['time_to_open'] = status['session_start'] - now
            else:
                status['status'] = 'CLOSED'
                next_open = (now + timedelta(days=1)).replace(hour=9, minute=15, second=0, microsecond=0)
                # Skip weekends
                while next_open.weekday() >= 5:
                    next_open += timedelta(days=1)
                status['next_open'] = next_open
        else:
            status['status'] = 'WEEKEND'
            # Find next Monday
            days_ahead = 7 - now.weekday()
            next_open = (now + timedelta(days=days_ahead)).replace(hour=9, minute=15, second=0, microsecond=0)
            status['next_open'] = next_open
        
        return status
    
    def get_top_gainers_losers(self, limit: int = 10) -> Dict[str, List[str]]:
        """Get top gainers and losers from NSE."""
        # This would typically connect to NSE API
        # For now, we'll use a subset of stocks and calculate from our data
        symbols = self.config.get_indian_stock_symbols()[:20]  # Use first 20 for performance
        
        gainers = []
        losers = []
        
        for symbol in symbols:
            try:
                data = self.get_stock_data(symbol, period="2d")
                if len(data.data) >= 2:
                    current_price = data.data['Close'].iloc[-1]
                    prev_price = data.data['Close'].iloc[-2]
                    change_pct = ((current_price - prev_price) / prev_price) * 100
                    
                    if change_pct > 0:
                        gainers.append((symbol, change_pct))
                    else:
                        losers.append((symbol, change_pct))
                        
            except Exception as e:
                logger.error(f"Error processing {symbol}: {e}")
                continue
        
        # Sort and limit
        gainers.sort(key=lambda x: x[1], reverse=True)
        losers.sort(key=lambda x: x[1])
        
        return {
            'gainers': [item[0] for item in gainers[:limit]],
            'losers': [item[0] for item in losers[:limit]]
        }
    
    def clear_cache(self) -> None:
        """Clear the data cache."""
        self.cache.clear()
        logger.info("Data cache cleared")
    
    def get_cache_info(self) -> Dict[str, any]:
        """Get information about cached data."""
        return {
            'cached_symbols': list(self.cache.keys()),
            'cache_size': len(self.cache),
            'last_updates': {symbol: data.last_updated for symbol, data in self.cache.items()}
        }
