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
        """
        Run backtest simulation
        
        Args:
            data: DataFrame with price data
            signals: Series with trading signals (1: buy, -1: sell, 0: hold)
            
        Returns:
            Dictionary with backtest results and metrics
        """
        self.reset()
        
        # Initialise tracking arrays
        portfolio_values = []
        positions = []
        trades = []
        
        for i, (date, row) in enumerate(data.iterrows()):
            price = row['Close']
            signal = signals.iloc[i] if i < len(signals) else 0
            
            # Execute trades based on signals
            if signal == 1 and self.position == 0:  # Buy signal
                self._execute_buy(date, price, trades)
            elif signal == -1 and self.position > 0:  # Sell signal
                self._execute_sell(date, price, trades)
            
            # Calculate current portfolio value
            current_value = self.capital + (self.position * price)
            portfolio_values.append(current_value)
            positions.append(self.position)
        
        # Create results DataFrame
        results_df = pd.DataFrame({
            'date': data.index,
            'price': data['Close'],
            'signal': signals,
            'position': positions,
            'portfolio_value': portfolio_values
        })
        
        # Calculate performance metrics
        metrics = self._calculate_metrics(results_df, trades)
        
        return {
            'results': results_df,
            'metrics': metrics,
            'trades': trades
        }
    
    def _execute_buy(self, date, price, trades):
        """Execute buy order"""
        shares = int(self.capital / price)
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
        """
        Calculate performance metrics
        
        Args:
            results_df: DataFrame with backtest results
            
        Returns:
            Dictionary with performance metrics
        """
        # Calculate returns
        results_df['returns'] = results_df['portfolio_value'].pct_change()
        
        # Total return
        total_return = (results_df['portfolio_value'].iloc[-1] / self.initial_capital) - 1
        
        # Annualised return
        days = (results_df['date'].iloc[-1] - results_df['date'].iloc[0]).days
        annualized_return = ((1 + total_return) ** (365 / days)) - 1 if days > 0 else 0
        
        # Volatility
        volatility = results_df['returns'].std() * np.sqrt(252)  # Annualized
        
        # Sharpe ratio (assuming risk-free rate of 0)
        sharpe_ratio = annualized_return / volatility if volatility > 0 else 0
        
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
    # Test the backtester
    from data_fetcher import DataFetcher
    from strategy import MACDStrategy
    
    # Get sample data
    fetcher = DataFetcher()
    data = fetcher.get_sample_data()
    
    # Generate signals
    strategy = MACDStrategy()
    macd_data = strategy.calculate_macd(data['Close'])
    signals = strategy.generate_signals(macd_data)
    
    # Run backtest
    backtester = Backtester(initial_capital=100000)
    results = backtester.run_backtest(data, signals['signal'])
    
    print("Backtest Results:")
    print(f"Total Return: {results['metrics']['total_return']:.2%}")
    print(f"Annualised Return: {results['metrics']['annualized_return']:.2%}")
    print(f"Sharpe Ratio: {results['metrics']['sharpe_ratio']:.2f}")
    print(f"Max Drawdown: {results['metrics']['max_drawdown']:.2%}")
    print(f"Number of Trades: {results['metrics']['num_trades']}")
    print(f"Win Rate: {results['metrics']['win_rate']:.2%}")
    print(f"Final Portfolio Value: ${results['metrics']['final_value']:,.2f}") 