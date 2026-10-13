from __future__ import annotations

import numpy as np
import pandas as pd


def compute_drawdown(cumulative_returns: pd.Series) -> float:
    """
    Maximum drawdown: largest peak-to-trough decline.
    """
    if cumulative_returns.empty:
        return 0.0
    running_max = cumulative_returns.cummax()
    drawdown = (cumulative_returns - running_max) / running_max
    return float(drawdown.min())


def compute_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.04) -> float:
    """
    Sharpe Ratio: excess return per unit of risk.
    Annualized (252 trading days).
    """
    if returns.empty or returns.std() == 0:
        return 0.0
    excess_returns = returns - risk_free_rate / 252
    return float(excess_returns.mean() / excess_returns.std() * np.sqrt(252))


def compute_sortino_ratio(returns: pd.Series, risk_free_rate: float = 0.04, target_return: float = 0.0) -> float:
    """
    Sortino Ratio: excess return per unit of downside risk.
    Only penalizes volatility from losses.
    """
    if returns.empty:
        return 0.0
    
    excess = returns - risk_free_rate / 252
    downside_returns = excess[excess < target_return]
    
    if len(downside_returns) < 2:
        return 0.0
    
    downside_std = downside_returns.std()
    if downside_std == 0:
        return 0.0
    
    return float(excess.mean() / downside_std * np.sqrt(252))


def compute_calmar_ratio(returns: pd.Series, annual_return: float) -> float:
    """
    Calmar Ratio: annual return / max drawdown.
    Measures return per unit of drawdown risk.
    """
    cumulative = (1 + returns).cumprod()
    max_dd = compute_drawdown(cumulative)
    
    if max_dd == 0 or np.isnan(max_dd):
        return 0.0
    
    return float(annual_return / abs(max_dd))


def compute_kelly_fraction(win_rate: float, avg_win: float, avg_loss: float) -> float:
    """
    Kelly Criterion: optimal position size.
    f* = (bp - q) / b
    where b = avg_win / avg_loss, p = win_rate, q = 1 - p
    
    Returns fraction of capital to allocate (0-1).
    """
    if avg_loss == 0 or win_rate <= 0 or win_rate >= 1:
        return 0.0 if win_rate <= 0 else 0.25
    
    b = avg_win / avg_loss if avg_loss != 0 else 1.0
    p = win_rate
    q = 1 - p
    
    kelly = (b * p - q) / b
    
    # Use fractional Kelly for safety (half-Kelly or quarter-Kelly)
    kelly_fraction = max(0.0, min(kelly / 2, 0.25))  # Cap at 25% for safety
    
    return kelly_fraction


def compute_win_rate(returns: pd.Series) -> tuple[float, float, float]:
    """
    Calculate win rate, average win, average loss.
    
    Returns:
        (win_rate, avg_win, avg_loss)
    """
    positive_returns = returns[returns > 0]
    negative_returns = returns[returns < 0]
    
    win_rate = len(positive_returns) / len(returns) if len(returns) > 0 else 0.0
    avg_win = positive_returns.mean() if len(positive_returns) > 0 else 0.0
    avg_loss = abs(negative_returns.mean()) if len(negative_returns) > 0 else 0.0
    
    return win_rate, avg_win, avg_loss


def compute_volatility(returns: pd.Series, window: int = 20) -> pd.Series:
    """
    Rolling annualized volatility.
    """
    return returns.rolling(window=window, min_periods=1).std().fillna(0.0) * np.sqrt(252)


def allocate_positions_optimal(
    signals: pd.DataFrame,
    returns: pd.DataFrame,
    total_capital: float = 100000.0,
    target_leverage: float = 1.5,
    max_position_size: float = 0.10,
) -> pd.DataFrame:
    """
    Allocate positions using Kelly Criterion with risk limits.
    
    Args:
        signals: Multi-factor signals for each asset (-1 to 1)
        returns: Historical returns for each asset
        total_capital: Account capital
        target_leverage: Target leverage (1.5 = 150%)
        max_position_size: Max allocation per position (0.10 = 10%)
    
    Returns:
        DataFrame with position sizes (as % of capital) for each asset.
    """
    if not np.isfinite([target_leverage,max_position_size]).all() or target_leverage < 0 or not 0 < max_position_size <= 1:
        raise ValueError("Invalid leverage or position limit")
    if not signals.index.equals(returns.index) or not signals.columns.equals(returns.columns):
        raise ValueError("Signals and returns must have matching dates and symbols")
    positions = pd.DataFrame(0.0, index=signals.index, columns=signals.columns)
    for symbol in signals.columns:
        # Heuristic signal-conditioned historical payoffs, not optimal Kelly proof.
        ret = returns[symbol] * signals[symbol].shift(1).fillna(0)
        # Expanding statistics contain only observations available at this close.
        # The backtest executes these target weights on the following interval.
        count = ret.notna().cumsum()
        wins = (ret > 0).cumsum()
        losses = (ret < 0).cumsum()
        avg_win = ret.where(ret > 0, 0.0).cumsum() / wins.replace(0, np.nan)
        avg_loss = -ret.where(ret < 0, 0.0).cumsum() / losses.replace(0, np.nan)
        win_rate = wins / count.replace(0, np.nan)
        payoff = avg_win / avg_loss
        kelly = ((payoff * win_rate - (1 - win_rate)) / payoff / 2).clip(0, .25)
        kelly = kelly.where(losses > 0, .25).where(wins > 0, 0.0)
        kelly = kelly.where(count >= 20, 0.0).fillna(0.0)
        positions[symbol] = (signals[symbol] * kelly * target_leverage).clip(
            -max_position_size, max_position_size
        )
    # A leverage ceiling scales down only; weak signals may leave cash uninvested.
    exposure = positions.abs().sum(axis=1)
    scale = (target_leverage / exposure.replace(0, np.nan)).clip(upper=1).fillna(1)
    return positions.mul(scale, axis=0)

