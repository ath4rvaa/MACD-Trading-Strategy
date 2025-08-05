# MACD Trading Strategy Backtesting Project

## Overview
This project implements a MACD (Moving Average Convergence Divergence) trading strategy with backtesting capabilities

## Project Structure

```
MACD/
├── data/                   # Store CSV data files. Using just 2y AAPL data for now from 2022-2024 for intiial testing
├── src/                    # Source code
│   ├── data_fetcher.py    # Fetch and preprocess market data
│   ├── strategy.py        # MACD calculations and signal generation
│   ├── backtester.py      # Backtesting engine and performance metrics
│   ├── visualization.py   # Chart plotting and analysis
│   └── main.py           # Main execution script
├── requirements.txt       # Python dependencies
└── README.md             # This

```

## My Thoughts


## Files Used

### data_fetcher.py
- Fetches historical market data from Yahoo Finance. Used AAPL data from 2022-2023 for initial backtesting. Data is saved in the ../data folder.


### strategy.py
- Implements MACD calculations and generate trading signals. 
- MACD strategy consists of using the difference between short-term and long-term EMAs (Exponential Moving Averages) to generate a MACD line (by deducting long EMA from short EMA), and a signal line (e.g., 9-period EMA), with a histogram showing their divergence for momentum insights. Traders buy on bullish crossovers (MACD above signal) or positive divergences (price is trending down but MACD is trending up), and sell on bearish crossovers (vice versa) or negative shifts.


### backtester.py
-  Simulates trading strategy and calculate performance metrics. It executes trades, track position and calculate returns, Sharpe ratio and drawdown.


### visualization.py
- Used for creating charts and visualisations for analysis of performance. 
- 2 charts are created. Fig 1 shows the buy and sell signals and the MACD chart. Fig 2 shows buy-and-hold strategy compared against the MACD strategy, and a comparison in portfolio value over time.


### main.py
- Runs the program, latches onto the other helper files. Entry point into program



## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python src/main.py
```

- Note: default values for MACD parameters are as such: 
    Fast period: 10
    Slow period: 20
    Signal time: 7
- These are definitely more aggresive comapred to the standard 12, 26, 9 respectively. I used this because I tested this strategy across a shorter and more volatile two year period from 2022-2024.
- The reduced parameters generate signals faster, potentially capturing more short-term opportunities in trending phases. However, this also increases the risk of over-sensitivity and a greater chance of false signals.
- Compared to the buy and hold strategy, the MACD strategy with aggressive parameters was able to outperform it over the testing period.


Data: 501 points, 2022-01-03 to 2023-12-29 (2y)
MACD params: 10, 20, 7
Signals: 38 buy, 36 sell

PERFORMANCE RESULTS
=============================
Total Return:        16.44%
Annualized Return:    7.96%
Sharpe Ratio:          0.79
Max Drawdown:       -10.40%
Trades:                   8
Win Rate:            62.50%
Final Value:       $ 116,435
