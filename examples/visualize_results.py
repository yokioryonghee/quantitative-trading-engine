from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from quant_engine.engine import build_engine


if __name__ == "__main__":
    results = build_engine(initial_capital=100000.0)
    
    # Create visualizations
    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    fig.suptitle("Quantitative Trading Engine Performance", fontsize=16, fontweight="bold")
    
    # Plot 1: Cumulative Returns
    ax = axes[0, 0]
    cumulative = results["cumulative_value"]
    ax.plot(cumulative.index, cumulative.values, linewidth=2, color="#1f77b4")
    ax.fill_between(cumulative.index, cumulative.values, alpha=0.3, color="#1f77b4")
    ax.set_title("Portfolio Value Over Time", fontweight="bold")
    ax.set_ylabel("Value ($)")
    ax.grid(True, alpha=0.3)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"${x/1000:.0f}K"))
    
    # Plot 2: Drawdown
    ax = axes[0, 1]
    cumsum = (1 + results["returns"]).cumprod()
    running_max = cumsum.cummax()
    drawdown_series = (cumsum - running_max) / running_max * 100
    ax.fill_between(drawdown_series.index, drawdown_series.values, alpha=0.5, color="#d62728")
    ax.set_title("Drawdown Over Time", fontweight="bold")
    ax.set_ylabel("Drawdown (%)")
    ax.grid(True, alpha=0.3)
    ax.set_ylim([drawdown_series.min() * 1.1, 0])
    
    # Plot 3: Daily Returns Distribution
    ax = axes[1, 0]
    returns = results["returns"] * 100
    ax.hist(returns, bins=50, alpha=0.7, color="#2ca02c", edgecolor="black")
    ax.axvline(returns.mean(), color="red", linestyle="--", linewidth=2, label=f"Mean: {returns.mean():.3f}%")
    ax.axvline(returns.median(), color="orange", linestyle="--", linewidth=2, label=f"Median: {returns.median():.3f}%")
    ax.set_title("Daily Returns Distribution", fontweight="bold")
    ax.set_xlabel("Daily Return (%)")
    ax.set_ylabel("Frequency")
    ax.legend()
    ax.grid(True, alpha=0.3, axis="y")
    
    # Plot 4: Key Metrics
    ax = axes[1, 1]
    ax.axis("off")
    
    metrics_text = f"""
    PERFORMANCE METRICS
    " + "="*40 + "
    Total Return:        {results['total_return']*100:>8.2f}%
    Annualized Return:   {results['annual_return']*100:>8.2f}%
    
    RISK METRICS
    " + "="*40 + "
    Sharpe Ratio:        {results['sharpe_ratio']:>8.4f}
    Sortino Ratio:       {results['sortino_ratio']:>8.4f}
    Max Drawdown:        {results['max_drawdown']*100:>8.2f}%
    Calmar Ratio:        {results['calmar_ratio']:>8.4f}
    
    TRADE METRICS
    " + "="*40 + "
    Win Rate:            {results['win_rate']*100:>8.2f}%
    Profit Factor:       {results['profit_factor']:>8.4f}
    Est. Trades:         {results['num_trades']:>8.0f}
    """
    
    ax.text(0.1, 0.95, metrics_text, transform=ax.transAxes, fontsize=11,
            verticalalignment="top", fontfamily="monospace",
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.8))
    
    plt.tight_layout()
    plt.savefig("backtest_results.png", dpi=300, bbox_inches="tight")
    print("\n✓ Chart saved to: backtest_results.png")
    plt.show()
