# -*- coding: utf-8 -*-
"""
Created on Wed Nov 29 20:43:04 2023

@author: corentin
"""

import pandas as pd
import numpy as np
from numpy.polynomial.polynomial import polyfit

def hurst_dfa(data, min_window=10, max_window=20):
    """
    Calculate the Hurst exponent using Detrended Fluctuation Analysis (DFA).

    :param data: 1D array-like time series data.
    :param min_window: Minimum window size for analysis.
    :param max_window: Maximum window size for analysis.
    :return: Estimated Hurst exponent.
    """
    # Convert to a numpy array if it's a pandas series
    if isinstance(data, pd.Series):
        data = data.values

    # Step 1: Integrated time series
    integrated_ts = np.cumsum(data - np.mean(data))

    # Step 2-5: Calculate RMS for various window sizes
    window_sizes = np.arange(min_window, max_window + 1)
    rms_list = []

    for window in window_sizes:
        rms = 0
        # Partition time series, detrend, and calculate RMS
        for i in range(0, len(integrated_ts), window):
            if i + window < len(integrated_ts):
                segment = integrated_ts[i:i + window]
                # Detrending (linear fit subtraction)
                trend = polyfit(np.arange(window), segment, 1)
                detrended = segment - trend[0] - trend[1] * np.arange(window)
                rms += np.sqrt(np.mean(detrended ** 2))
        rms /= len(integrated_ts) / window
        rms_list.append(rms)

    # Step 6: Determine scaling behavior
    # Linear fit in log-log space
    coeffs = np.polyfit(np.log(window_sizes), np.log(rms_list), 1)
    hurst_exponent = coeffs[0]

    return hurst_exponent

from scipy.spatial.distance import hamming

def calculate_hamming_distance(series, windows=[2,5, 10, 15, 20, 30, 40, 50]):
    """
    Calculate and return the Hamming distance score between binary sequences of different moving average windows.

    :param data: Pandas DataFrame with 'Close' prices.
    :param windows: List of integers representing window sizes for moving averages.
    :return: Hamming distance score.
    """
    # Ensure input is a Pandas Series
    if not isinstance(series, pd.Series):
        raise ValueError("Input must be a Pandas Series.")

    # Initialize DataFrame to store moving averages and binary sequences
    data = pd.DataFrame()
    data['Close'] = series

    # Calculate moving averages and binary sequences
    for window in windows:
        ma_column = f'SMA_{window}'
        binary_column = f'Binary_{window}'
        data[ma_column] = series.rolling(window=window).mean()
        data[binary_column] = (series > data[ma_column]).astype(int)

    data=data.iloc[-1] #take only the last view    

# Calculate Hamming distances
    hamming_scores = []
    for i in range(len(windows)):
        for j in range(i+1, len(windows)):
            #score = hamming(data[f'Binary_{windows[i]}'], data[f'Binary_{windows[j]}'])
            score = np.abs(data[f'Binary_{windows[i]}']-data[f'Binary_{windows[j]}'])
            hamming_scores.append(score)

    # Aggregate Hamming scores
    if hamming_scores:
        average_score = sum(hamming_scores) / len(hamming_scores)
    else:
        average_score = 0

    return average_score






