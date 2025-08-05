"""
Data Fetcher
"""

import yfinance as yf
import pandas as pd
import os


class DataFetcher:
    def __init__(self, data_dir: str = "./data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
    
    def fetch_data(self, symbol: str, start_date: str, end_date: str, 
                   interval: str = "1d") -> pd.DataFrame:
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(start=start_date, end=end_date, interval=interval)
            
            if data.empty:
                raise ValueError(f"No data found for {symbol}")
            
            data = self._clean_data(data)
            
            filename = f"{symbol}_{start_date}_{end_date}_{interval}.csv"
            filepath = os.path.join(self.data_dir, filename)
            data.to_csv(filepath)
            
            print(f"Data saved to {filepath}")
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
