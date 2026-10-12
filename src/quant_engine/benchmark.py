from __future__ import annotations

from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import yfinance as yf

from quant_engine.backtest import run_backtest
from quant_engine.data_loader import normalize_download


def fetch_benchmark_data(symbol: str = "SPY", start_date: str | None = None, end_date: str | None = None) -> pd.Series:
    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")
    if start_date is None:
        start_date = (datetime.now() - timedelta(days=10 * 365)).strftime("%Y-%m-%d")

    df = yf.download(symbol, start=start_date, end=end_date, progress=False, auto_adjust=True, multi_level_index=False, timeout=20)
    if df is None or df.empty:
        raise ValueError(f"No benchmark data found for {symbol}")

    return normalize_download(df, symbol)["close"].astype(float).rename(symbol)


def compare_with_benchmark(strategy_returns: pd.Series, benchmark_series: pd.Series) -> dict:
    if isinstance(benchmark_series, pd.DataFrame):
        if benchmark_series.shape[1] != 1:
            raise ValueError("Benchmark must contain one price series")
        benchmark_series = benchmark_series.iloc[:, 0]
    # Sample both wealth curves at common closes. Weekend crypto returns are
    # compounded into the next shared stock-market observation.
    strategy_cum = (1 + strategy_returns.fillna(0.0)).cumprod().rename("strategy")
    aligned = pd.concat([strategy_cum, benchmark_series.rename("benchmark")], axis=1, join="inner").dropna()
    if len(aligned) < 3:
        raise ValueError("At least three overlapping dates are required")
    aligned = aligned / aligned.iloc[0]
    paired_returns = aligned.pct_change().iloc[1:]
    periods = len(paired_returns)
    strategy_total = float(aligned["strategy"].iloc[-1] - 1)
    benchmark_total = float(aligned["benchmark"].iloc[-1] - 1)
    strategy_annual = float((1 + strategy_total) ** (252 / periods) - 1)
    benchmark_annual = float((1 + benchmark_total) ** (252 / periods) - 1)
    variance = paired_returns["benchmark"].var()
    beta = float(paired_returns["strategy"].cov(paired_returns["benchmark"]) / variance) if variance > 0 else 0.0
    return {
        "strategy_total_return": strategy_total,
        "benchmark_total_return": benchmark_total,
        "outperformance": strategy_total - benchmark_total,
        "strategy_annualized_return": strategy_annual,
        "benchmark_annualized_return": benchmark_annual,
        "alpha": strategy_annual - beta * benchmark_annual,
        "beta": beta,
        "benchmark_symbol": benchmark_series.name or "SPY",
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
            backtest = run_backtest(
                prices, volume, momentum_window=momentum_window,
                mean_reversion_window=mean_reversion_window,
            )
            total_return = backtest["total_return"]
            sharpe = backtest["sharpe_ratio"]
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
