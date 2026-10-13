from __future__ import annotations

import numpy as np
import pandas as pd

from quant_engine.indicators import generate_multifactor_signal
from quant_engine.accounting import simulate
from quant_engine.risk import (
    compute_calmar_ratio,
    compute_drawdown,
    compute_sharpe_ratio,
    compute_sortino_ratio,
    compute_win_rate,
    allocate_positions_optimal,
)


def run_backtest(
    prices: pd.DataFrame,
    volume: pd.DataFrame,
    initial_capital: float = 100000.0,
    target_leverage: float = 1.5,
    momentum_window: int = 20,
    mean_reversion_window: int = 30,
    rebalance_freq: int = 20,
    open_prices: pd.DataFrame | None = None,
    cost_bps: float = 10.0,
    borrow_rate: float = 0.03,
    cash_rate: float = 0.0,
) -> dict:
    """
    Run multi-asset backtest with optimal position sizing and rebalancing.
    
    Args:
        prices: DataFrame with close prices (Date x Symbol)
        volume: DataFrame with volumes (Date x Symbol)
        initial_capital: Starting capital
        target_leverage: Target leverage (1.5 = 150%)
        rebalance_freq: Days between rebalancing
    
    Returns:
        Dictionary with backtest results and metrics.
    """
    
    if not prices.index.is_unique or not prices.index.is_monotonic_increasing or prices.index.hasnans:
        raise ValueError("Price dates must be unique, valid and increasing")
    if prices.empty or prices.shape[1] == 0:
        raise ValueError("Prices must not be empty")
    if not isinstance(rebalance_freq,int) or initial_capital <= 0 or rebalance_freq < 1:
        raise ValueError("Capital and rebalance frequency must be positive")
    # Ensure no NaN values in prices
    prices = prices.ffill()
    if prices.isna().any().any() or not np.isfinite(prices.to_numpy()).all() or (prices <= 0).any().any():
        raise ValueError("Prices must be finite and positive, with no leading missing values")
    volume = volume.fillna(0)
    
    # Calculate returns
    returns = prices.pct_change().fillna(0.0)
    
    # Generate signals
    signals = generate_multifactor_signal(prices, momentum_window=momentum_window, mean_reversion_window=mean_reversion_window)
    
    # Allocate positions
    positions = allocate_positions_optimal(
        signals,
        returns,
        total_capital=initial_capital,
        target_leverage=target_leverage,
    )
    
    # Rebalance periodically
    for i in range(len(positions)):
        if i % rebalance_freq != 0:
            positions.iloc[i] = positions.iloc[i - 1]
    
    cumulative, strategy_returns, realized_weights, ledger = simulate(
        prices,positions,volume,initial_capital,open_prices,cost_bps,borrow_rate,cash_rate,rebalance_freq)

    # Compute metrics
    total_return = (cumulative.iloc[-1] / initial_capital) - 1
    elapsed=(prices.index[-1]-prices.index[0]).total_seconds()/86400 if isinstance(prices.index,pd.DatetimeIndex) and len(prices)>1 else len(prices)*365.25/252
    annual_return = (cumulative.iloc[-1] / initial_capital) ** (365.25/max(elapsed,1.)) - 1
    sharpe = compute_sharpe_ratio(strategy_returns)
    sortino = compute_sortino_ratio(strategy_returns)
    drawdown = compute_drawdown((1 + strategy_returns).cumprod())
    calmar = compute_calmar_ratio(strategy_returns, annual_return)
    win_rate, avg_win, avg_loss = compute_win_rate(strategy_returns)
    
    # Win/loss ratio
    profit_factor = (avg_win * sum(strategy_returns > 0)) / (avg_loss * sum(strategy_returns < 0)) if avg_loss > 0 else 0.0
    
    result = {
        "cumulative_value": cumulative,
        "returns": strategy_returns,
        "positions": positions,
        "signals": signals,
        "total_return": float(total_return),
        "annual_return": float(annual_return),
        "sharpe_ratio": float(sharpe),
        "sortino_ratio": float(sortino),
        "max_drawdown": float(drawdown),
        "calmar_ratio": float(calmar),
        "win_rate": float(win_rate),
        "profit_factor": float(profit_factor),
        "final_value": float(cumulative.iloc[-1]),
        "num_trades": len(ledger),
        "trade_ledger": ledger,
        "realized_weights": realized_weights,
        "execution": "next observed open" if open_prices is not None else "next observed close",
        "cost_bps": cost_bps,
    }
    
    return result

