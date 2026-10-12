from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from quant_engine.benchmark import (
    compare_with_benchmark,
    fetch_benchmark_data,
)
from quant_engine.engine import build_engine


if __name__ == "__main__":
    results = build_engine(initial_capital=100000.0)

    # Fetch benchmark
    try:
        benchmark_series = fetch_benchmark_data()
        benchmark_comparison = compare_with_benchmark(results["returns"], benchmark_series)
    except Exception:
        benchmark_comparison = None

    # Create comprehensive visualizations
    fig = plt.figure(figsize=(18, 12))
    gs = fig.add_gridspec(3, 3, hspace=0.35, wspace=0.3)

    fig.suptitle("Quantitative Trading Engine - Performance Analysis", fontsize=18, fontweight="bold")

    # Plot 1: Portfolio value vs S&P 500
    ax = fig.add_subplot(gs[0, :])
    strategy_cum = (1 + results["returns"].fillna(0.0)).cumprod() * 100000
    ax.plot(strategy_cum.index, strategy_cum.values, linewidth=2.5, label="Strategy", color="#1f77b4")
    if benchmark_comparison:
        benchmark_series_norm = benchmark_series / benchmark_series.iloc[0] * 100000
        ax.plot(
            benchmark_series_norm.index,
            benchmark_series_norm.values,
            linewidth=2.5,
            label="S&P 500 (Benchmark)",
            color="#ff7f0e",
            alpha=0.8,
        )
    ax.fill_between(strategy_cum.index, strategy_cum.values, alpha=0.2, color="#1f77b4")
    ax.set_title("Portfolio Value Over Time", fontweight="bold", fontsize=12)
    ax.set_ylabel("Value ($)", fontweight="bold")
    ax.legend(loc="upper left", fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"${x/1000:.0f}K"))

    # Plot 2: Drawdown
    ax = fig.add_subplot(gs[1, 0])
    cumsum = (1 + results["returns"].fillna(0.0)).cumprod()
    running_max = cumsum.cummax()
    drawdown_series = (cumsum - running_max) / running_max * 100
    ax.fill_between(drawdown_series.index, drawdown_series.values, alpha=0.6, color="#d62728")
    ax.set_title("Drawdown Over Time", fontweight="bold", fontsize=11)
    ax.set_ylabel("Drawdown (%)", fontweight="bold")
    ax.grid(True, alpha=0.3)
    ax.set_ylim([drawdown_series.min() * 1.1, 0])

    # Plot 3: Daily returns distribution
    ax = fig.add_subplot(gs[1, 1])
    returns_pct = results["returns"] * 100
    ax.hist(returns_pct, bins=60, alpha=0.7, color="#2ca02c", edgecolor="black")
    ax.axvline(returns_pct.mean(), color="red", linestyle="--", linewidth=2, label=f"Mean: {returns_pct.mean():.3f}%")
    ax.axvline(returns_pct.median(), color="orange", linestyle="--", linewidth=2, label=f"Median: {returns_pct.median():.3f}%")
    ax.set_title("Daily Returns Distribution", fontweight="bold", fontsize=11)
    ax.set_xlabel("Daily Return (%)", fontweight="bold")
    ax.set_ylabel("Frequency", fontweight="bold")
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3, axis="y")

    # Plot 4: Rolling Sharpe Ratio
    ax = fig.add_subplot(gs[1, 2])
    rolling_sharpe = (results["returns"].fillna(0.0).rolling(252).mean() / results["returns"].fillna(0.0).rolling(252).std()) * np.sqrt(252)
    ax.plot(rolling_sharpe.index, rolling_sharpe.values, linewidth=2, color="#9467bd")
    ax.axhline(y=0, color="black", linestyle="-", linewidth=0.8, alpha=0.5)
    ax.fill_between(rolling_sharpe.index, rolling_sharpe.values, alpha=0.3, color="#9467bd")
    ax.set_title("Rolling Sharpe Ratio (252-day)", fontweight="bold", fontsize=11)
    ax.set_ylabel("Sharpe Ratio", fontweight="bold")
    ax.grid(True, alpha=0.3)

    # Plot 5: Monthly returns heatmap
    ax = fig.add_subplot(gs[2, :])
    monthly_returns = results["returns"].fillna(0.0).resample("ME").apply(lambda x: (1 + x).prod() - 1) * 100
    years = monthly_returns.index.year.unique()
    months = np.arange(1, 13)
    heatmap_data = np.full((len(years), 12), np.nan)
    for i, year in enumerate(years):
        year_data = monthly_returns[monthly_returns.index.year == year]
        for month in year_data.index.month:
            heatmap_data[i, month - 1] = year_data[year_data.index.month == month].values[0]

    im = ax.imshow(heatmap_data, cmap="RdYlGn", aspect="auto", vmin=-5, vmax=5)
    ax.set_xticks(np.arange(12))
    ax.set_yticks(np.arange(len(years)))
    ax.set_xticklabels(["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
    ax.set_yticklabels(years)
    ax.set_title("Monthly Returns Heatmap (%)", fontweight="bold", fontsize=12)
    cbar = plt.colorbar(im, ax=ax, orientation="horizontal", pad=0.1)
    cbar.set_label("Return (%)", fontweight="bold")

    # Add text annotation for returns
    for i in range(len(years)):
        for j in range(12):
            if not np.isnan(heatmap_data[i, j]):
                text = ax.text(j, i, f"{heatmap_data[i, j]:.1f}", ha="center", va="center", color="black", fontsize=8)

    plt.savefig("backtest_comprehensive_analysis.png", dpi=300, bbox_inches="tight")
    print("\n✓ Comprehensive analysis chart saved to: backtest_comprehensive_analysis.png")
    plt.show()
