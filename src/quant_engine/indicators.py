from __future__ import annotations

import numpy as np
import pandas as pd


def compute_sma(series: pd.Series, window: int) -> pd.Series:
    """Simple moving average."""
    return series.rolling(window=window, min_periods=1).mean()


def compute_ema(series: pd.Series, span: int) -> pd.Series:
    """Exponential moving average."""
    return series.ewm(span=span, adjust=False).mean()


def compute_rsi(series: pd.Series, window: int = 14) -> pd.Series:
    """Relative Strength Index (0-100)."""
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window, min_periods=1).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window, min_periods=1).mean()
    rs = gain / loss.replace(0, 1e-10)
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(50)


def compute_macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> tuple[pd.Series, pd.Series, pd.Series]:
    """MACD: Moving Average Convergence Divergence."""
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def compute_bollinger_bands(series: pd.Series, window: int = 20, num_std: float = 2.0) -> tuple[pd.Series, pd.Series, pd.Series]:
    """Bollinger Bands."""
    sma = series.rolling(window=window, min_periods=1).mean()
    std = series.rolling(window=window, min_periods=1).std()
    upper = sma + (std * num_std)
    lower = sma - (std * num_std)
    return upper, sma, lower


def compute_volatility(series: pd.Series, window: int = 20) -> pd.Series:
    """Annualized volatility."""
    returns = series.pct_change().fillna(0.0)
    rolling_std = returns.rolling(window=window, min_periods=1).std().fillna(0.0)
    return rolling_std * np.sqrt(252)


def compute_momentum(series: pd.Series, window: int = 20) -> pd.Series:
    """Price momentum (% change over window)."""
    return series.pct_change(periods=window).fillna(0.0)


def compute_mean_reversion_score(series: pd.Series, window: int = 30) -> pd.Series:
    """
    Mean reversion score: how far price is from its moving average.
    Positive = above average (potential reversal down)
    Negative = below average (potential reversal up)
    """
    sma = series.rolling(window=window, min_periods=1).mean()
    std = series.rolling(window=window, min_periods=1).std().fillna(1e-10)
    z_score = (series - sma) / std
    return z_score.fillna(0.0)


def generate_multifactor_signal(
    prices: pd.DataFrame,
    rsi_threshold: tuple[float, float] = (30, 70),
    momentum_window: int = 20,
    mean_reversion_window: int = 30,
) -> pd.DataFrame:
    """
    Generate multi-factor signals combining:
    - Momentum (trend following)
    - Mean reversion (contrarian)
    - RSI (overbought/oversold)
    - Price above/below moving average
    
    Returns DataFrame with signal values (-1, 0, 1) for each asset.
    """
    signals = pd.DataFrame(index=prices.index, columns=prices.columns, dtype=float)
    
    for symbol in prices.columns:
        series = prices[symbol]
        
        # Momentum signal (trend following)
        momentum = compute_momentum(series, window=momentum_window)
        momentum_signal = pd.Series(0.0, index=series.index)
        momentum_signal[momentum > 0.02] = 1.0  # Strong uptrend
        momentum_signal[momentum < -0.02] = -1.0  # Strong downtrend
        
        # Mean reversion signal (contrarian)
        mr_score = compute_mean_reversion_score(series, window=mean_reversion_window)
        mr_signal = pd.Series(0.0, index=series.index)
        mr_signal[mr_score < -2] = 1.0  # Oversold, buy
        mr_signal[mr_score > 2] = -1.0  # Overbought, sell
        
        # RSI signal
        rsi = compute_rsi(series, window=14)
        rsi_signal = pd.Series(0.0, index=series.index)
        rsi_signal[rsi < rsi_threshold[0]] = 1.0  # Oversold
        rsi_signal[rsi > rsi_threshold[1]] = -1.0  # Overbought
        
        # Price position signal
        sma = compute_sma(series, window=50)
        price_signal = pd.Series(0.0, index=series.index)
        price_signal[series > sma] = 0.5  # Above MA (bullish)
        price_signal[series < sma] = -0.5  # Below MA (bearish)
        
        # Combine signals (weighted)
        combined = (
            momentum_signal * 0.35 +
            mr_signal * 0.25 +
            rsi_signal * 0.20 +
            price_signal * 0.20
        )
        
        # Clip to [-1, 1]
        signals[symbol] = np.clip(combined, -1, 1)
    
    return signals
