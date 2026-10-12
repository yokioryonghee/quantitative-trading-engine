from __future__ import annotations

from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import yfinance as yf

from quant_engine.indicators import generate_multifactor_signal
from quant_engine.risk import allocate_positions_optimal, compute_sharpe_ratio


def fetch_benchmark_data(symbol: str = "SPY", start_date: str | None = None, end_date: str | None = None) -> pd.Series:
    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")
    if start_date is None:
        start_date = (datetime.now() - timedelta(days=10 * 365)).strftime("%Y-%m-%d")

    df = yf.download(symbol, start=start_date, end=end_date, progress=False)
    if df.empty:
        raise ValueError(f"No benchmark data found for {symbol}")

    return df["Close"].astype(float)


def compare_with_benchmark(strategy_returns: pd.Series, benchmark_series: pd.Series) -> dict:
    benchmark_returns = benchmark_series.pct_change().fillna(0.0)
    strategy_cum = (1 + strategy_returns.fillna(0.0)).cumprod()
    benchmark_cum = (1 + benchmark_returns.fillna(0.0)).cumprod()

    strategy_total = float(strategy_cum.iloc[-1] - 1)
    benchmark_total = float(benchmark_cum.iloc[-1] - 1)
    outperformance = strategy_total - benchmark_total

    strategy_annual = float((strategy_cum.iloc[-1] ** (252 / len(strategy_cum))) - 1) if len(strategy_cum) > 1 else 0.0
    benchmark_annual = float((benchmark_cum.iloc[-1] ** (252 / len(benchmark_cum))) - 1) if len(benchmark_cum) > 1 else 0.0

    covariance = np.cov(strategy_returns.fillna(0.0), benchmark_returns.fillna(0.0))[0][1]
    variance = np.var(benchmark_returns.fillna(0.0))
    beta = covariance / variance if variance != 0 else 0.0

    alpha = strategy_annual - (beta * benchmark_annual)

    return {
        "strategy_total_return": strategy_total,
        "benchmark_total_return": benchmark_total,
        "outperformance": outperformance,
        "strategy_annualized_return": strategy_annual,
        "benchmark_annualized_return": benchmark_annual,
        "alpha": alpha,
        "beta": beta,
        "benchmark_symbol": "SPY",
    }


def parameter_sweep(
    prices: pd.DataFrame,
    volume: pd.DataFrame,
    momentum_windows: list[int] | None = None,
    mean_reversion_windows: list[int] | None = None,
) -> list[dict]:
    if momentum_windows is None:
        momentum_windows = [10, 20, 30]
    if mean_reversion_windows is None:
        mean_reversion_windows = [20, 30, 40, 50]

    results = []
    for momentum_window in momentum_windows:
        for mean_reversion_window in mean_reversion_windows:
            # Use a simple scoring function and risk-based sizing
            signals = generate_multifactor_signal(
                prices,
                momentum_window=momentum_window,
                mean_reversion_window=mean_reversion_window,
            )
            positions = allocate_positions_optimal(
                signals,
                prices.pct_change().fillna(0.0),
                total_capital=100000.0,
                target_leverage=1.5,
            )
            lagged_positions = positions.shift(1).fillna(0.0)
            strategy_returns = (prices.pct_change().fillna(0.0) * lagged_positions).sum(axis=1)
            cum = (1 + strategy_returns).cumprod()
            total_return = float(cum.iloc[-1] - 1)
            sharpe = float(compute_sharpe_ratio(strategy_returns))
            results.append(
                {
                    "momentum_window": momentum_window,
                    "mean_reversion_window": mean_reversion_window,
                    "total_return": total_return,
                    "sharpe_ratio": sharpe,
                }
            )

    results.sort(key=lambda x: x["sharpe_ratio"], reverse=True)
    return results[:5]
