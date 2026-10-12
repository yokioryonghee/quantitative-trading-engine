from __future__ import annotations

import numpy as np
import pandas as pd

from quant_engine.indicators import generate_signal
from quant_engine.risk import compute_drawdown, compute_sharpe_ratio


def run_backtest(df: pd.DataFrame, short_window: int = 10, long_window: int = 30, risk_per_trade: float = 0.01) -> dict:
    if "Close" not in df.columns:
        raise ValueError("Market dataframe must contain 'Close'.")

    price = df["Close"].astype(float)
    returns = price.pct_change().fillna(0.0)
    signal = generate_signal(df, short_window=short_window, long_window=long_window)
    position = signal.shift(1).fillna(0.0)
    strategy_returns = returns * position

    cumulative = (1 + strategy_returns).cumprod()
    cum_return = cumulative.iloc[-1] - 1
    annualized = (cumulative.iloc[-1] ** (252 / len(cumulative))) - 1 if len(cumulative) > 1 else 0.0
    sharpe = compute_sharpe_ratio(strategy_returns)
    drawdown = compute_drawdown((1 + strategy_returns).cumprod())

    result = {
        "signal": signal,
        "position": position,
        "returns": strategy_returns,
        "cumulative_return": float(cum_return),
        "annualized_return": float(annualized),
        "sharpe_ratio": float(sharpe),
        "max_drawdown": float(drawdown),
        "final_value": float(cumulative.iloc[-1]),
    }
    return result
