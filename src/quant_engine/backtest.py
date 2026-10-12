from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats

from quant_engine.indicators import generate_multifactor_signal
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
    rebalance_freq: int = 20,  # Rebalance every 20 days
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
    
    # Calculate returns
    returns = prices.pct_change().fillna(0.0)
    
    # Generate signals
    signals = generate_multifactor_signal(prices)
    
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
    
    # Calculate strategy returns (lag positions by 1 day for realistic entry)
    lagged_positions = positions.shift(1).fillna(0.0)
    strategy_returns = (returns * lagged_positions).sum(axis=1)
    
    # Cumulative returns
    cumulative = (1 + strategy_returns).cumprod() * initial_capital
    
    # Compute metrics
    total_return = (cumulative.iloc[-1] / initial_capital) - 1
    annual_return = (cumulative.iloc[-1] / initial_capital) ** (252 / len(cumulative)) - 1
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
        "num_trades": int(((positions != 0).sum().sum() - (positions.shift(1) != 0).sum().sum()) / 2),
    }
    
    return result
