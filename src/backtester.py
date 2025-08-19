"""
Backtesting Engine
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')


class Backtester:
    def __init__(self, initial_capital: float = 100000, commission: float = 0.001):
        self.initial_capital = initial_capital
        self.commission = commission
        self.reset()
    
    def reset(self):
        self.capital = self.initial_capital
        self.position = 0
        self.trades = []
        self.portfolio_values = []
        self.positions = []
    
    def run_backtest(self, data: pd.DataFrame, signals: pd.Series) -> Dict:
        self.reset()
        
        portfolio_values = []
        positions = []
        trades = []
        
        for i, (date, row) in enumerate(data.iterrows()):
            price = row['Close']
            signal = signals.iloc[i] if i < len(signals) else 0
            
            if signal >= 1 and self.position == 0:
                self._execute_buy(date, price, trades)
            elif signal <= -1 and self.position > 0:
                self._execute_sell(date, price, trades)
 
            current_value = self.capital + (self.position * price)
            portfolio_values.append(current_value)
            positions.append(self.position)
        
        results_df = pd.DataFrame({
            'date': data.index,
            'price': data['Close'],
            'signal': signals,
            'position': positions,
            'portfolio_value': portfolio_values
        })
        
        metrics = self._calculate_metrics(results_df, trades)
        
        return {
            'results': results_df,
            'metrics': metrics,
            'trades': trades
        }
    
    def _execute_buy(self, date, price, trades):
        """Execute buy order"""
        # Calculate shares accounting for commission
        shares = int(self.capital / (price * (1 + self.commission)))
        if shares > 0:
            cost = shares * price * (1 + self.commission)
            if cost <= self.capital:
                self.position = shares
                self.capital -= cost
                trades.append({
                    'date': date,
                    'action': 'BUY',
                    'price': price,
                    'shares': shares,
                    'cost': cost
                })
    
    def _execute_sell(self, date, price, trades):
        """Execute sell order"""
        if self.position > 0:
            proceeds = self.position * price * (1 - self.commission)
            trades.append({
                'date': date,
                'action': 'SELL',
                'price': price,
                'shares': self.position,
                'proceeds': proceeds
            })
            self.capital += proceeds
            self.position = 0
    
    def _calculate_metrics(self, results_df: pd.DataFrame, trades: List) -> Dict:

        # Calculate returns
        results_df['returns'] = results_df['portfolio_value'].pct_change()
        
        # Total return
        total_return = (results_df['portfolio_value'].iloc[-1] / self.initial_capital) - 1
        
        # Annualised return
        days = (results_df['date'].iloc[-1] - results_df['date'].iloc[0]).days
        annualised_return = ((1 + total_return) ** (365 / days)) - 1 if days > 0 else 0
        
        # Determine timeframe for proper annualisation
        # Check if data is hourly by looking at time differences
        if len(results_df) > 1:
            time_diff = results_df['date'].iloc[1] - results_df['date'].iloc[0]
            if time_diff.total_seconds() <= 3600:  # 1 hour or less
                # For hourly data: 252 trading days * 6.5 trading hours = 1638 hours per year
                annualisation_factor = 1638
            else:
                # For daily data: 252 trading days per year
                annualisation_factor = 252
        else:
            annualisation_factor = 252  # Default to daily
        
        # Volatility (annualised)
        volatility = results_df['returns'].std() * np.sqrt(annualisation_factor)
        
        # Sharpe ratio (using current US risk-free rate of 4.22%)
        risk_free_rate = 0.0422
        sharpe_ratio = (annualised_return - risk_free_rate) / volatility if volatility > 0 else 0
        
        # Maximum drawdown
        cumulative_returns = (1 + results_df['returns']).cumprod()
        running_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - running_max) / running_max
        max_drawdown = drawdown.min()
        
        # Win rate and average trade
        trades_df = pd.DataFrame(trades) if trades else pd.DataFrame()
        win_rate = 0
        avg_trade = 0
        
        if not trades_df.empty and len(trades_df) >= 2:
            # Calculate trade returns
            buy_trades = trades_df[trades_df['action'] == 'BUY']
            sell_trades = trades_df[trades_df['action'] == 'SELL']
            
            if len(buy_trades) > 0 and len(sell_trades) > 0:
                trade_returns = []
                for i in range(min(len(buy_trades), len(sell_trades))):
                    buy_price = buy_trades.iloc[i]['price']
                    sell_price = sell_trades.iloc[i]['price']
                    trade_return = (sell_price - buy_price) / buy_price
                    trade_returns.append(trade_return)
                
                if trade_returns:
                    win_rate = sum(1 for r in trade_returns if r > 0) / len(trade_returns)
                    avg_trade = np.mean(trade_returns)
        
        # Number of trades
        num_trades = len([t for t in trades if t['action'] == 'SELL'])
        
        return {
            'total_return': total_return,
            'annualized_return': annualized_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'avg_trade': avg_trade,
            'num_trades': num_trades,
            'final_value': results_df['portfolio_value'].iloc[-1]
        }


if __name__ == "__main__":
    pass 