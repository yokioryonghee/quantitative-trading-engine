from __future__ import annotations

import pandas as pd

from quant_engine.backtest import run_backtest
from quant_engine.data_loader import (
    fetch_market_data,
    get_optimal_universe,
    prepare_panel_data,
)


def build_engine(
    symbols: list[str] | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    initial_capital: float = 100000.0,
    target_leverage: float = 1.5,
) -> dict:
    """
    Complete pipeline: fetch data → prepare → backtest → results.
    
    Args:
        symbols: List of tickers. If None, uses optimal universe.
        start_date: Start date (YYYY-MM-DD). Defaults to 10 years ago.
        end_date: End date (YYYY-MM-DD). Defaults to today.
        initial_capital: Starting capital.
        target_leverage: Target leverage.
    
    Returns:
        Dictionary with backtest results.
    """
    
    if symbols is None:
        symbols = get_optimal_universe()
    
    print("\n" + "="*70)
    print("QUANTITATIVE TRADING ENGINE")
    print("="*70)
    
    # Fetch data
    print(f"\n[1/4] Fetching market data for {len(symbols)} assets...")
    raw_data = fetch_market_data(symbols, start_date, end_date)
    print(f"✓ Data fetched: {len(raw_data)} rows")
    
    from quant_engine.data_loader import convert_to_usd
    raw_data = convert_to_usd(raw_data)

    # Prepare panel data
    print(f"\n[2/4] Preparing panel data...")
    prices, volume, open_prices = prepare_panel_data(raw_data)
    print(f"✓ Assets: {prices.shape[1]}, Trading days: {prices.shape[0]}")
    
    # Run backtest
    print(f"\n[3/4] Running backtest...")
    results = run_backtest(
        prices,
        volume,
        initial_capital=initial_capital,
        target_leverage=target_leverage,
        open_prices=open_prices,
    )
    print(f"✓ Backtest complete")
    
    # Print summary
    print(f"\n[4/4] Results Summary")
    print("="*70)
    print(f"Initial Capital:        {initial_capital:,.0f} USD")
    print(f"Final Value:            USD {results['final_value']:,.0f}")
    print(f"Total Return:           {results['total_return']*100:,.2f}%")
    print(f"Annualized Return:      {results['annual_return']*100:,.2f}%")
    print(f"\nRisk Metrics:")
    print(f"Sharpe Ratio:           {results['sharpe_ratio']:.4f}")
    print(f"Sortino Ratio:          {results['sortino_ratio']:.4f}")
    print(f"Max Drawdown:           {results['max_drawdown']*100:,.2f}%")
    print(f"Calmar Ratio:           {results['calmar_ratio']:.4f}")
    print(f"\nTrade Metrics:")
    print(f"Win Rate:               {results['win_rate']*100:.2f}%")
    print(f"Profit Factor:          {results['profit_factor']:.4f}")
    print(f"Estimated Trades:       {results['num_trades']}")
    print("="*70 + "\n")
    
    return results

