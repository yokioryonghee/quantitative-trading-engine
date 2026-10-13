from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from quant_engine.benchmark import (
    compare_with_benchmark,
    fetch_benchmark_data,
    parameter_sweep,
)
from quant_engine.data_loader import (
    fetch_market_data,
    get_optimal_universe,
    prepare_panel_data,
    convert_to_usd,
)
from quant_engine.engine import build_engine


if __name__ == "__main__":
    print("\n" + "="*70)
    print("QUANTITATIVE TRADING ENGINE - COMPREHENSIVE ANALYSIS")
    print("="*70)

    # Build base strategy
    results = build_engine(initial_capital=100000.0)

    # Fetch benchmark data
    print("\n[1/3] Fetching S&P 500 benchmark data...")
    try:
        benchmark_series = fetch_benchmark_data()
        strategy_returns = results["returns"]
        benchmark_comparison = compare_with_benchmark(strategy_returns, benchmark_series)
        print("✓ Benchmark comparison complete")
    except Exception as e:
        print(f"⚠ Benchmark comparison skipped: {str(e)[:50]}")
        benchmark_comparison = None

    # Parameter sweep
    print("\n[2/3] Running parameter optimization sweep...")
    try:
        symbols = get_optimal_universe()
        raw_data = fetch_market_data(symbols)
        prices, volume, openings = prepare_panel_data(convert_to_usd(raw_data))
        param_results = parameter_sweep(prices, volume, open_prices=openings)
        print(f"✓ Parameter sweep complete - Top 5 configurations identified")
    except Exception as e:
        print(f"⚠ Parameter sweep skipped: {str(e)[:50]}")
        param_results = None

    # Print benchmark comparison
    if benchmark_comparison:
        print("\n" + "="*70)
        print("BENCHMARK COMPARISON (vs S&P 500)")
        print("="*70)
        print(f"Strategy Total Return:    {benchmark_comparison['strategy_total_return']*100:>8.2f}%")
        print(f"Benchmark Total Return:   {benchmark_comparison['benchmark_total_return']*100:>8.2f}%")
        print(f"Outperformance:           {benchmark_comparison['outperformance']*100:>8.2f}%")
        print(f"\nStrategy Annualized:      {benchmark_comparison['strategy_annualized_return']*100:>8.2f}%")
        print(f"Benchmark Annualized:     {benchmark_comparison['benchmark_annualized_return']*100:>8.2f}%")
        print(f"Alpha:                    {benchmark_comparison['alpha']*100:>8.2f}%")
        print(f"Beta:                     {benchmark_comparison['beta']:>8.4f}")
        print("="*70 + "\n")

    # Print parameter sweep results
    if param_results:
        print("\n" + "="*70)
        print("PARAMETER OPTIMIZATION - TOP 5 CONFIGURATIONS")
        print("="*70)
        for i, config in enumerate(param_results, 1):
            print(
                f"\n#{i}: Momentum={config['momentum_window']}, "
                f"MeanReversion={config['mean_reversion_window']}"
            )
            print(
                f"    Return: {config['total_return']*100:6.2f}% | "
                f"Sharpe: {config['sharpe_ratio']:6.4f}"
            )
        print("\n" + "="*70 + "\n")

