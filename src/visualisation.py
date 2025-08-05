"""
Visualization Module
Creates charts and plots for MACD strategy analysis
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
from typing import Dict, List
import seaborn as sns

# Set style for better-looking plots
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")


class MACDVisualiser:
    """Handles all visualisation for MACD strategy analysis"""
    
    def __init__(self, figsize: tuple = (15, 10)):
        """
        Initialize visualiser
        
        Args:
            figsize: Figure size for plots
        """
        self.figsize = figsize
    
    def plot_macd_chart(self, data: pd.DataFrame, macd_data: pd.DataFrame, 
                       signals: pd.DataFrame, title: str = "MACD Strategy Analysis"):
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=self.figsize, 
                                      gridspec_kw={'height_ratios': [2, 1]})
        
        # Plot 1: Price and signals
        ax1.plot(data.index, data['Close'], label='Close Price', linewidth=1.5, color='black')
        
        # Add buy/sell signals
        buy_signals = signals[signals['signal'] == 1]
        sell_signals = signals[signals['signal'] == -1]
        
        ax1.scatter(buy_signals.index, data.loc[buy_signals.index, 'Close'], 
                   marker='^', color='green', s=100, label='Buy Signal', zorder=5)
        ax1.scatter(sell_signals.index, data.loc[sell_signals.index, 'Close'], 
                   marker='v', color='red', s=100, label='Sell Signal', zorder=5)
        
        ax1.set_title(f'{title} - Price Chart with Signals', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Price ($)', fontsize=12)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: MACD Line and Signal Line
        ax2.plot(macd_data.index, macd_data['macd_line'], label='MACD Line', linewidth=1.5)
        ax2.plot(macd_data.index, macd_data['signal_line'], label='Signal Line', linewidth=1.5)
        ax2.axhline(y=0, color='black', linestyle='--', alpha=0.5)
        ax2.set_ylabel('MACD', fontsize=12)
        ax2.set_xlabel('Date', fontsize=12)
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Format x-axis
        for ax in [ax1, ax2]:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
            ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        plt.tight_layout()
        return fig
    
    def plot_performance(self, results_df: pd.DataFrame, title: str = "Strategy Performance"):
        """
        Plot portfolio performance over time
        
        Args:
            results_df: Backtest results DataFrame
            title: Chart title
        """
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=self.figsize, 
                                      gridspec_kw={'height_ratios': [2, 1]})
        
        # Plot 1: Portfolio Value
        ax1.plot(results_df['date'], results_df['portfolio_value'], 
                label='Strategy Portfolio', linewidth=2, color='blue')
        
        # Add buy-and-hold comparison
        initial_value = results_df['portfolio_value'].iloc[0]
        buy_hold = initial_value * (results_df['price'] / results_df['price'].iloc[0])
        ax1.plot(results_df['date'], buy_hold, label='Buy & Hold', 
                linewidth=2, color='red', alpha=0.7)
        
        ax1.set_title(f'{title} - Portfolio Value', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Portfolio Value ($)', fontsize=12)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Drawdown
        cumulative_returns = (1 + results_df['returns']).cumprod()
        running_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - running_max) / running_max
        
        ax2.fill_between(results_df['date'], drawdown, 0, alpha=0.3, color='red')
        ax2.plot(results_df['date'], drawdown, color='red', linewidth=1)
        ax2.set_ylabel('Drawdown', fontsize=12)
        ax2.set_xlabel('Date', fontsize=12)
        ax2.grid(True, alpha=0.3)
        
        # Format x-axis
        for ax in [ax1, ax2]:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
            ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        plt.tight_layout()
        return fig
    
    def plot_metrics_summary(self, metrics: Dict, title: str = "Performance Metrics"):
        """
        Create a summary chart of key performance metrics
        
        Args:
            metrics: Dictionary of performance metrics
            title: Chart title
        """
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 8))
        
        # Metric 1: Returns
        returns_data = [metrics['total_return'], metrics['annualized_return']]
        returns_labels = ['Total Return', 'Annualized Return']
        colors = ['lightblue', 'lightgreen']
        
        bars1 = ax1.bar(returns_labels, returns_data, color=colors)
        ax1.set_title('Returns', fontweight='bold')
        ax1.set_ylabel('Return (%)')
        ax1.tick_params(axis='x', rotation=45)
        
        # Add value labels on bars
        for bar, value in zip(bars1, returns_data):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{value:.2%}', ha='center', va='bottom')
        
        # Metric 2: Risk Metrics
        risk_data = [metrics['volatility'], abs(metrics['max_drawdown'])]
        risk_labels = ['Volatility', 'Max Drawdown']
        colors = ['orange', 'red']
        
        bars2 = ax2.bar(risk_labels, risk_data, color=colors)
        ax2.set_title('Risk Metrics', fontweight='bold')
        ax2.set_ylabel('Risk (%)')
        ax2.tick_params(axis='x', rotation=45)
        
        for bar, value in zip(bars2, risk_data):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{value:.2%}', ha='center', va='bottom')
        
        # Metric 3: Sharpe Ratio
        ax3.bar(['Sharpe Ratio'], [metrics['sharpe_ratio']], color='purple')
        ax3.set_title('Risk-Adjusted Return', fontweight='bold')
        ax3.set_ylabel('Sharpe Ratio')
        ax3.text(0, metrics['sharpe_ratio'], f'{metrics["sharpe_ratio"]:.2f}', 
                ha='center', va='bottom')
        
        # Metric 4: Trading Statistics
        trading_data = [metrics['num_trades'], metrics['win_rate'] * 100]
        trading_labels = ['Number of Trades', 'Win Rate (%)']
        colors = ['lightcoral', 'lightsteelblue']
        
        bars4 = ax4.bar(trading_labels, trading_data, color=colors)
        ax4.set_title('Trading Statistics', fontweight='bold')
        ax4.set_ylabel('Count / Percentage')
        ax4.tick_params(axis='x', rotation=45)
        
        for bar, value in zip(bars4, trading_data):
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height,
                    f'{value:.1f}', ha='center', va='bottom')
        
        plt.suptitle(title, fontsize=16, fontweight='bold')
        plt.tight_layout()
        return fig
    
    def save_plots(self, fig, filename: str, dpi: int = 300):
        """
        Save plot to file
        
        Args:
            fig: Matplotlib figure object
            filename: Output filename
            dpi: Resolution for saving
        """
        fig.savefig(filename, dpi=dpi, bbox_inches='tight')
        print(f"Plot saved as {filename}")


if __name__ == "__main__":
    # Test the visualiser
    from data_fetcher import DataFetcher
    from strategy import MACDStrategy
    
    # Get sample data
    fetcher = DataFetcher()
    data = fetcher.get_sample_data()
    
    # Generate MACD data and signals
    strategy = MACDStrategy()
    macd_data = strategy.calculate_macd(data['Close'])
    signals = strategy.generate_signals(macd_data)
    
    # Create visualisations
    visualiser = MACDVisualiser()
    
    # Plot MACD chart
    fig1 = visualiser.plot_macd_chart(data, macd_data, signals)
    plt.show()
    
    print("Visualization module test completed!") 