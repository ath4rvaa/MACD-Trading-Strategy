"""
MACD Strategy
"""

import pandas as pd


class MACDStrategy:
    def __init__(self, fast_period: int = 12, slow_period: int = 26, 
                 signal_period: int = 9):
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period
    
    def calculate_macd(self, prices: pd.Series) -> pd.DataFrame:
        ema_fast = prices.ewm(span=self.fast_period).mean()
        ema_slow = prices.ewm(span=self.slow_period).mean()
        
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=self.signal_period).mean()
        histogram = macd_line - signal_line
        
        return pd.DataFrame({
            'macd_line': macd_line,
            'signal_line': signal_line,
            'histogram': histogram
        })
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        signals = pd.DataFrame(index=data.index)
        signals['signal'] = 0
        
        signals['macd_crossover'] = self._detect_crossovers(
            data['macd_line'], data['signal_line']
        )
        signals['zero_crossover'] = self._detect_zero_crossovers(data['macd_line'])
        signals['signal'] = self._combine_signals(signals)
        
        return signals
    
    def _detect_crossovers(self, line1: pd.Series, line2: pd.Series) -> pd.Series:
        crossovers = pd.Series(0, index=line1.index)
        
        bullish = (line1 > line2) & (line1.shift(1) <= line2.shift(1))
        crossovers[bullish] = 1
        
        bearish = (line1 < line2) & (line1.shift(1) >= line2.shift(1))
        crossovers[bearish] = -1
        
        return crossovers
    
    def _detect_zero_crossovers(self, macd_line: pd.Series) -> pd.Series:
        zero_crossovers = pd.Series(0, index=macd_line.index)
        
        bullish_zero = (macd_line > 0) & (macd_line.shift(1) <= 0)
        zero_crossovers[bullish_zero] = 1
        
        bearish_zero = (macd_line < 0) & (macd_line.shift(1) >= 0)
        zero_crossovers[bearish_zero] = -1
        
        return zero_crossovers
    
    def _combine_signals(self, signals: pd.DataFrame) -> pd.Series:
        combined = pd.Series(0, index=signals.index)
        
        combined[signals['macd_crossover'] == 1] = 1
        combined[signals['macd_crossover'] == -1] = -1
        
        zero_buy = (signals['zero_crossover'] == 1) & (signals['macd_crossover'] == 0)
        zero_sell = (signals['zero_crossover'] == -1) & (signals['macd_crossover'] == 0)
        
        combined[zero_buy] = 1
        combined[zero_sell] = -1
        
        return combined
