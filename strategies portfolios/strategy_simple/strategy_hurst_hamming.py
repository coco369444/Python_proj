# -*- coding: utf-8 -*-
"""
Created on Wed Nov 29 21:25:27 2023

@author: corentin
"""



def trading_strategy(data, hurst_threshold=0.55, hamming_threshold=0.3, stop_loss=0.02):
    """
    Trading strategy based on Hurst exponent and Hamming distance.

    :param data: DataFrame with stock price data.
    :param hurst_threshold: Threshold for Hurst exponent to indicate momentum.
    :param hamming_threshold: Threshold for Hamming distance to indicate buy signal.
    :param stop_loss: Stop loss percentage.
    :return: DataFrame with trade signals and performance.
    """
    # Calculate Hurst exponent and Hamming distance

    in_position = False
    entry_price = 0
    max_price_since_entry = 0

    data['Signal'] = 0  # 1 for Buy, -1 for Sell

    for i in range(len(data)):
        if not in_position:
            # Check for buy signal
            if data['Hurst'][i] > hurst_threshold and data['Hamming'][i] < hamming_threshold:
                in_position = True
                entry_price = data['Close'][i]
                max_price_since_entry = entry_price
                data['Signal'][i] = 1  # Buy
        else:
            # Update max price since entry
            if data['Close'][i] > max_price_since_entry:
                max_price_since_entry = data['Close'][i]

            # Check for stop loss
            if data['Close'][i] < max_price_since_entry * (1 - stop_loss) and not (data['Hurst'][i] > hurst_threshold and data['Hamming'][i] < hamming_threshold):
                in_position = False
                data['Signal'][i] = -1  # Sell

    return data


def evaluate_strategy_performance(data, benchmark_col='Close'):
    """
    Evaluate the performance of a trading strategy and compare it with a benchmark.

    :param data: Pandas DataFrame with 'Close' prices and 'Signal' for trading signals.
    :param benchmark_col: Column name for the benchmark data.
    :return: Dictionary with strategy and benchmark performance.
    """
    # Ensure data contains necessary columns
    if 'Signal' not in data.columns or benchmark_col not in data.columns:
        raise ValueError("Data must contain 'Signal' and benchmark columns.")

    # Initialize a column to track the position (1 for in the market, 0 for out)
    data['Position'] = 0
    # Update the position based on the signal
    for i in range(1, len(data)):
        if data['Signal'].iloc[i] == 1:
            data['Position'].iloc[i] = 1
        elif data['Signal'].iloc[i] == -1:
            data['Position'].iloc[i] = 0
        else:  # Signal is 0
            data['Position'].iloc[i] = data['Position'].iloc[i-1]

    # Calculate strategy returns
    data['Strategy'] = data['Position'].shift(1) * data[benchmark_col].pct_change()
    strategy_returns = (1 + data['Strategy'].fillna(0)).cumprod() - 1
    data['Strategy']=strategy_returns
    # Calculate benchmark returns
    benchmark_returns = (data[benchmark_col] / data[benchmark_col].iloc[0]) - 1

    # Performance summary
    performance = {
        'Strategy Cumulative Returns': strategy_returns.iloc[-1],
        'Benchmark Cumulative Returns': benchmark_returns.iloc[-1]
    }

    return data,performance


def evaluate_strategy_performance_fees(data, benchmark_col='Close', fee=0.001):
    """
    Evaluate the performance of a trading strategy, accounting for trading fees, and compare it with a benchmark.

    :param data: Pandas DataFrame with 'Close' prices and 'Signal' for trading signals.
    :param benchmark_col: Column name for the benchmark data.
    :param fee: Trading fee as a percentage of the trade amount.
    :return: Dictionary with strategy and benchmark performance.
    """
    if 'Signal' not in data.columns or benchmark_col not in data.columns:
        raise ValueError("Data must contain 'Signal' and benchmark columns.")

    data['Position'] = 0
    data['Strategy'] = 0.0
    data["Strategy_without_fee"]=0
    data["return_next"] = data[benchmark_col].pct_change().shift(-1)

    for i in range(0, len(data)):
        if data['Signal'].iloc[i] == 1:
            data['Position'].iloc[i] = 1
            # Apply fee for entering the position
            data['Strategy'].iloc[i] = -fee
        elif data['Signal'].iloc[i] == -1:
            data['Position'].iloc[i] = 0
            # Apply fee for exiting the position
            data['Strategy'].iloc[i] = -fee
        else:
            if i!=0:
                data['Position'].iloc[i] = data['Position'].iloc[i-1]

        # Calculate returns only if in position
        if data['Position'].iloc[i] == 1:
            data['Strategy'].iloc[i] += data["return_next"].iloc[i]
            data["Strategy_without_fee"].iloc[i] += data["return_next"].iloc[i]

    # Calculate cumulative returns
    data['Strategy'] = (1 + data['Strategy']).cumprod() - 1
    data['Strategy_without_fee'] = (1 + data['Strategy_without_fee']).cumprod() - 1
    data["Strat_bench"] = (1 + data['return_next']).cumprod() - 1
    data=data.iloc[:-1] #last in nan because of the shift from above
    
    strategy_returns = data['Strategy'].iloc[-1]

    # Calculate benchmark returns
    benchmark_returns = (data[benchmark_col] / data[benchmark_col].iloc[0]) - 1

    performance = {
        'Strategy Cumulative Returns': strategy_returns,
        'Benchmark Cumulative Returns': benchmark_returns.iloc[-1]
    }

    return data,performance



