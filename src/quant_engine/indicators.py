from __future__ import annotations

__all__ = [
    "compute_sma",
    "compute_ema",
    "compute_volatility",
    "generate_signal",
]

import numpy as np
import pandas as pd


def compute_sma(series: pd.Series, window: int) -> pd.Series:
    return series.rolling(window=window, min_periods=1).mean()


def compute_ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False).mean()


def compute_volatility(series: pd.Series, window: int = 20) -> pd.Series:
    returns = series.pct_change().fillna(0.0)
    return returns.rolling(window=window, min_periods=1).std().fillna(0.0)


def generate_signal(df: pd.DataFrame, short_window: int = 10, long_window: int = 30) -> pd.Series:
    if "Close" not in df.columns:
        raise ValueError("Input dataframe must contain a 'Close' column.")

    short_ma = compute_sma(df["Close"], short_window)
    long_ma = compute_sma(df["Close"], long_window)
    signal = pd.Series(0.0, index=df.index)
    signal[short_ma > long_ma] = 1.0
    signal[short_ma < long_ma] = -1.0
    return signal
