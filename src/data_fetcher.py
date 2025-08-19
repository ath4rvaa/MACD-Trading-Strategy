"""
Data Fetcher using Alpaca Trade API
"""

import alpaca_trade_api as tradeapi
import pandas as pd
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv


class DataFetcher:
    def __init__(self, data_dir: str = "./data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        # Load environment variables from .env file
        load_dotenv()
        
        # Initialize Alpaca API (using paper trading for testing)
        self.api = tradeapi.REST(
            key_id=os.getenv('ALPACA_API_KEY'),
            secret_key=os.getenv('ALPACA_SECRET_KEY'),
            base_url='https://paper-api.alpaca.markets'  # paper trading for testing
        )
    
    def fetch_data(self, symbol: str, start_date: str, end_date: str, 
                   interval: str = "1Hour") -> pd.DataFrame:
        try:
            # Convert string dates to datetime objects
            start_dt = pd.to_datetime(start_date)
            end_dt = pd.to_datetime(end_date)
            
            # Alpaca time format
            start_str = start_dt.strftime('%Y-%m-%d')
            end_str = end_dt.strftime('%Y-%m-%d')
            
            # Fetch data from Alpaca
            bars = self.api.get_bars(
                symbol,
                start=start_str,
                end=end_str,
                timeframe=interval,
                adjustment='all'  # Adjust for splits and dividends
            )
            
            if not bars:
                raise ValueError(f"No data found for {symbol}")
            
            # Convert to df
            data = bars.df
            
            if data.empty:
                raise ValueError(f"No data found for {symbol}")
            
            # Rename columns to match expected format
            data = data.rename(columns={
                'open': 'Open',
                'high': 'High', 
                'low': 'Low',
                'close': 'Close',
                'volume': 'Volume'
            })
            
            # Select only the columns we need
            data = data[['Open', 'High', 'Low', 'Close', 'Volume']]
            
            data = self._clean_data(data)
            
            # Save to file
            filename = f"{symbol}_{start_date}_{end_date}_{interval}.csv"
            filepath = os.path.join(self.data_dir, filename)
            data.to_csv(filepath)
            
            print(f"Data saved to {filepath}")
            print(f"Fetched {len(data)} hourly bars for {symbol}")
            return data
            
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return pd.DataFrame()
    
    def _clean_data(self, data: pd.DataFrame) -> pd.DataFrame:
        data = data.dropna()
        
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        if not all(col in data.columns for col in required_columns):
            raise ValueError("Data missing required OHLCV columns")
        
        return data.sort_index()
