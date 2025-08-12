"""
MACD Trading Strategy Backtesting
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_fetcher import DataFetcher
from strategy import MACDStrategy
from backtester import Backtester
from visualisation import MACDVisualiser
import argparse
import matplotlib.pyplot as plt


def main():

    # Command line arguments for running a backtest, default values also stated here (now includes stochastic oscillator params)
    parser = argparse.ArgumentParser(description='MACD Trading Strategy')
    parser.add_argument('--symbol', type=str, default='AAPL', help='Stock symbol')
    parser.add_argument('--start_date', type=str, default='2022-01-01', help='Start date')
    parser.add_argument('--end_date', type=str, default='2024-01-01', help='End date')
    parser.add_argument('--capital', type=float, default=100000, help='Initial capital')
    parser.add_argument('--commission', type=float, default=0.001, help='Commission rate')
    parser.add_argument('--fast_period', type=int, default=12, help='Fast EMA period')
    parser.add_argument('--slow_period', type=int, default=26, help='Slow EMA period')
    parser.add_argument('--signal_period', type=int, default=9, help='Signal EMA period')
    parser.add_argument('--k_period', type=int, default=14, help='Stochastic %K period')
    parser.add_argument('--d_period', type=int, default=3, help='Stochastic %D period')
    parser.add_argument('--save_plots', action='store_true', help='Save plots')
    
    args = parser.parse_args()
    
    print("MACD + Stochastic Trading Strategy Backtesting")
    print("=" * 50)
    
    # Fetch data
    fetcher = DataFetcher()
    data = fetcher.fetch_data(args.symbol, args.start_date, args.end_date)
    
    if data.empty:
        print("Error: No data retrieved.")
        return
    
    print(f"Data: {len(data)} points, {data.index[0].date()} to {data.index[-1].date()}")
    
    # Calculate MACD and Stochastic
    strategy = MACDStrategy(args.fast_period, args.slow_period, args.signal_period)
    macd_data = strategy.calculate_macd(data['Close'])
    stochastic_data = strategy.calculate_stochastic(data, args.k_period, args.d_period)
    
    # Generate enhanced signals
    enhanced_signals = strategy.generate_enhanced_signals(macd_data, stochastic_data)
    
    print(f"MACD params: {args.fast_period}, {args.slow_period}, {args.signal_period}")
    print(f"Stochastic params: {args.k_period}, {args.d_period}")
    print(f"Strong signals: {(enhanced_signals['enhanced_signal'] == 1).sum()} buy, {(enhanced_signals['enhanced_signal'] == -1).sum()} sell")
    print(f"Total signals: {(enhanced_signals['enhanced_signal'] != 0).sum()}")
    
    # Run backtest with enhanced signals
    backtester = Backtester(args.capital, args.commission)
    results = backtester.run_backtest(data, enhanced_signals['enhanced_signal'])
    metrics = results['metrics']
    
    # Results  
    print("\nPERFORMANCE RESULTS")
    print("=" * 50)
    print(f"Total Return:      {metrics['total_return']:>8.2%}")
    print(f"Annualized Return: {metrics['annualized_return']:>8.2%}")
    print(f"Sharpe Ratio:      {metrics['sharpe_ratio']:>8.2f}")
    print(f"Max Drawdown:      {metrics['max_drawdown']:>8.2%}")
    print(f"Trades:            {metrics['num_trades']:>8d}")
    print(f"Win Rate:          {metrics['win_rate']:>8.2%}")
    print(f"Final Value:       ${metrics['final_value']:>8,.0f}")
    
    # Create visualizations
    visualiser = MACDVisualiser()
    
    fig1 = visualiser.plot_macd_chart(data, macd_data, enhanced_signals, results['trades'], f"MACD - {args.symbol}")
    fig2 = visualiser.plot_performance(results['results'], f"Performance - {args.symbol}")
    
    if args.save_plots:
        visualiser.save_plots(fig1, f"macd_{args.symbol}.png")
        visualiser.save_plots(fig2, f"performance_{args.symbol}.png")
    
    plt.show()


if __name__ == "__main__":
    main()