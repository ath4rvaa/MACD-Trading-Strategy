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
│   ├── visualisation.py   # Chart plotting and analysis
│   └── main.py           # Main execution script
├── requirements.txt       # Python dependencies
└── README.md             # This

```

## My Thoughts
### **1st commit**
- Note: default values for MACD parameters are as such for now: 
    Fast period: 10
    Slow period: 20
    Signal time: 7
- These are definitely more aggresive comapred to the standard 12, 26, 9 respectively. I used this because I tested this strategy across a shorter and more volatile two year period from 2022-2024.
- The reduced parameters generate signals faster, potentially capturing more short-term opportunities in trending phases. However, this also increases the risk of over-sensitivity and a greater chance of false signals.
- Compared to the buy and hold strategy, the MACD strategy with aggressive parameters was able to outperform it over the testing period.
- RFR was taken as 0% here

Data: 501 points, 2022-01-03 to 2023-12-29 (2y)
MACD params: 10, 20, 7
Signals: 38 buy, 36 sell

Total Return:        16.44%
Annualized Return:    7.96%
Sharpe Ratio:          0.79
Max Drawdown:       -10.40%
Trades:                   8
Win Rate:            62.50%
Final Value:       $ 116,435

### **2nd commit - stochastic oscillators filtering addition**
Added in stochastic oscillator to help filter out false MACD signals. Parameters were set to default, so 12 26 9 for MACD and 14 3 for stochastic oscillator. Tested this combined strategy using AAPL stock data from yfinance, from 2019-2024. Using US Risk free Rate 4.22% as well, for sharpe ratio calculation.

**Testing Results:**
- **1-year (2023)**: +5.55% return, 6 trades, 33.33% win rate, Sharpe: 0.18
- **2-year (2022-2024)**: -3.07% return, 11 trades, 36.36% win rate, Sharpe: -0.50
- **5-year (2019-2024)**: +13.66% return, 7 trades, 57.14% win rate, Sharpe: -0.18

**Insights:**
- Strategy underperformed buy & hold across all time periods tested
- In strong trending markets (2019-2024), buy & hold (+408%) significantly outperformed the strategy (+13.66%)
- The combination likely works better in volatile/sideways markets but struggles in trending markets
- Risk-adjusted performance: Only the 1-year period (2023) showed positive Sharpe ratio (0.18), while 2-year and 5-year periods had negative Sharpe ratios due to underperformance vs 4.22% risk-free rate
- Trading frequency: 2-year period had the most trades (11), suggesting higher volatility and more signal generation
- Drawdown analysis: 1-year period had lowest max drawdown (-6.59%), while 2-year period had highest (-16.69%)

### **3rd commit - removal of weak signals**
Removed weak signals (0.5 and -0.5) from the strategy to focus only on strong, confirmed signals. This change simplifies the signal system to only execute trades when both MACD and Stochastic oscillator are in agreement, potentially reducing false signals and improving trade quality.

**Updated Signal System:**
- **Strong Buy (1)**: MACD bullish + Stochastic oversold confirmation within 3 days
- **Strong Sell (-1)**: MACD bearish + Stochastic overbought confirmation within 3 days  
- **No Signal (0)**: When indicators disagree or no clear direction

This modification aimed to improve the strategy's performance by eliminating potentially low-quality trades that occur when only one indicator is signaling while the other remains neutral, and it was successful. Fewer trades were executed due to stricter requirements.

**Parameter Adjustment:**
After the 2nd commit, MACD parameters were changed from the standard 12,26,9 to more aggressive 8,21,5. This adjustment was made to:
- Generate signals more frequently in the current market environment
- Better capture short-term momentum shifts
- Adapt to the more volatile market conditions post-2020
- The faster parameters (8,21,5) are more responsive compared to traditional (12,26,9)

**Results after weak signal removal (with 8,21,5 parameters):**
- **1-year (2023)**: +16.78% return, 2 trades, 100.00% win rate, Sharpe: 1.00
- **2-year (2022-2024)**: +27.12% return, 3 trades, 100.00% win rate, Sharpe: 0.38
- **5-year (2019-2024)**: +50.69% return, 5 trades, 100.00% win rate, Sharpe: 0.28

**Key improvements:**
- **Reduced trading frequency**: Fewer trades executed due to stricter signal requirements
- **Improved signal quality**: Only trades with strong confirmation from both indicators
- **Better risk-adjusted returns**: All periods now show positive Sharpe ratios
- **Strategy refinement**: More conservative approach prioritizing quality over quantity

The combination of removing weak signals and using more aggressive MACD parameters (8,21,5) created a more selective yet responsive trading strategy that waits for stronger confirmation before entering positions, leading to improved risk-adjusted returns across all time periods tested.


## Files Used

### data_fetcher.py
- Fetches historical market data from Yahoo Finance. Used AAPL data from 2022-2023 for initial backtesting. Data is saved in the ../data folder.


### strategy.py
- Implements MACD calculations and generate trading signals. 
- MACD strategy consists of using the difference between short-term and long-term EMAs (Exponential Moving Averages) to generate a MACD line (by deducting long EMA from short EMA), and a signal line (e.g., 9-period EMA), with a histogram showing their divergence for momentum insights. Traders buy on bullish crossovers (MACD above signal) or positive divergences (price is trending down but MACD is trending up), and sell on bearish crossovers (vice versa) or negative shifts.
- added a stochastic oscillator filter in order to help to filter out false MACD signals that occur in choppy markets, to ensure better entry/exit timings

### backtester.py
-  Simulates trading strategy and calculate performance metrics. It executes trades, track position and calculate returns, Sharpe ratio and drawdown.


### visualisation.py
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

