from __future__ import annotations

import numpy as np
import pandas as pd


def compute_drawdown(series: pd.Series) -> float:
    if series.empty:
        return 0.0
    rolling_peak = series.cummax()
    drawdown = (series - rolling_peak) / rolling_peak
    return float(drawdown.min())


def compute_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.0) -> float:
    if returns.empty:
        return 0.0
    excess = returns - risk_free_rate
    std = excess.std()
    if np.isclose(std, 0.0):
        return 0.0
    return float(excess.mean() / std * np.sqrt(252))


def compute_position_size(account_equity: float, volatility: float, risk_per_trade: float = 0.01, max_exposure: float = 0.25) -> float:
    if volatility <= 0 or account_equity <= 0:
        return 0.0
    raw_size = (account_equity * risk_per_trade) / volatility
    return float(min(max(raw_size, 0.0), account_equity * max_exposure))


def allocate_positions(signal: pd.Series, volatility: pd.Series, equity: float, risk_per_trade: float = 0.01) -> pd.Series:
    position = pd.Series(0.0, index=signal.index)
    for idx in signal.index:
        direction = signal.loc[idx]
        vol = float(volatility.loc[idx])
        if direction == 0:
            position.loc[idx] = 0.0
        else:
            size = compute_position_size(equity, vol, risk_per_trade)
            position.loc[idx] = size * direction
    return position
