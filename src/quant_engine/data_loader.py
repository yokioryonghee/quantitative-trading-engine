from __future__ import annotations

import warnings
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import yfinance as yf

warnings.filterwarnings("ignore")

# Multi-asset universe: US stocks, Korean stocks, crypto, commodities
ASSET_UNIVERSE = {
    "us_stocks": ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META"],
    "korean_stocks": ["005930.KS", "051910.KS", "000660.KS", "207940.KS"],
    "crypto": ["BTC-USD", "ETH-USD"],
    "commodities": ["GLD", "USO", "DBC"],  # Gold, Oil, Commodities
    "indices": ["SPY", "QQQ"],  # Market indices for hedging
}


def fetch_market_data(
    symbols: list[str],
    start_date: str | None = None,
    end_date: str | None = None,
) -> pd.DataFrame:
    """
    Fetch real market data from yfinance with robust error handling.
    
    Args:
        symbols: List of ticker symbols
        start_date: Start date (YYYY-MM-DD). Defaults to 10 years ago.
        end_date: End date (YYYY-MM-DD). Defaults to today.
    
    Returns:
        DataFrame with columns: Date, Open, High, Low, Close, Volume, Symbol
    """
    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")
    if start_date is None:
        start_date = (datetime.now() - timedelta(days=10*365)).strftime("%Y-%m-%d")
    
    print(f"Fetching data for {len(symbols)} symbols from {start_date} to {end_date}...")
    
    data_list = []
    successful_symbols = []
    
    for symbol in symbols:
        try:
            df = yf.download(symbol, start=start_date, end=end_date, progress=False)
            if df.empty:
                print(f"✗ {symbol}: No data")
                continue
            
            # Reset index to convert Date from index to column
            df = df.reset_index()
            
            # Standardize column names to lowercase
            df.columns = [col.lower() for col in df.columns]
            
            # Create normalized dataframe with required columns only
            normalized = pd.DataFrame({
                'Date': pd.to_datetime(df['date']),
                'Open': pd.to_numeric(df.get('open', np.nan), errors='coerce'),
                'High': pd.to_numeric(df.get('high', np.nan), errors='coerce'),
                'Low': pd.to_numeric(df.get('low', np.nan), errors='coerce'),
                'Close': pd.to_numeric(df.get('close', np.nan), errors='coerce'),
                'Volume': pd.to_numeric(df.get('volume', 0), errors='coerce').fillna(0),
                'Symbol': symbol
            })
            
            # Drop any rows with missing price data
            normalized = normalized.dropna(subset=['Close'])
            
            if len(normalized) > 0:
                data_list.append(normalized)
                successful_symbols.append(symbol)
                print(f"✓ {symbol}")
            else:
                print(f"✗ {symbol}: No valid price data")
                
        except Exception as e:
            print(f"✗ {symbol}: {str(e)[:50]}")
    
    if not data_list:
        raise ValueError("No data fetched. Check symbols and internet connection.")
    
    # Concatenate all data
    aligned_data = pd.concat(data_list, ignore_index=True)
    
    # Sort by Date and Symbol for consistent ordering
    aligned_data = aligned_data.sort_values(['Date', 'Symbol']).reset_index(drop=True)
    
    # Forward fill any remaining NaN values in OHLC using new pandas syntax
    for col in ['Open', 'High', 'Low', 'Close']:
        aligned_data[col] = aligned_data.groupby('Symbol')[col].transform(lambda x: x.ffill().bfill())
    
    return aligned_data


def get_optimal_universe() -> list[str]:
    """
    Return best-performing assets across all classes for this backtest.
    """
    symbols = []
    for asset_class, tickers in ASSET_UNIVERSE.items():
        symbols.extend(tickers)
    return symbols


def prepare_panel_data(df: pd.DataFrame) -> tuple:
    """
    Convert aligned data into panel format (Date x Symbol).
    
    Args:
        df: DataFrame with Date, Close, Volume, Open, Symbol columns
    
    Returns:
        Tuple of (pivot_close, pivot_volume, pivot_open) - all aligned
    """
    # Create pivot tables
    pivot_close = df.pivot_table(index="Date", columns="Symbol", values="Close", aggfunc='first')
    pivot_volume = df.pivot_table(index="Date", columns="Symbol", values="Volume", aggfunc='first')
    pivot_open = df.pivot_table(index="Date", columns="Symbol", values="Open", aggfunc='first')
    
    # Forward fill for missing data within each symbol, then backward fill (new pandas syntax)
    pivot_close = pivot_close.ffill().bfill()
    pivot_volume = pivot_volume.fillna(0)
    pivot_open = pivot_open.ffill().bfill()
    
    # Remove any remaining NaN rows
    valid_idx = ~(pivot_close.isna().any(axis=1) | pivot_open.isna().any(axis=1))
    pivot_close = pivot_close[valid_idx]
    pivot_volume = pivot_volume.loc[pivot_close.index]
    pivot_open = pivot_open.loc[pivot_close.index]
    
    # Ensure all have at least 100 trading days
    if len(pivot_close) < 100:
        raise ValueError(f"Insufficient data: only {len(pivot_close)} trading days available (need at least 100)")
    
    return pivot_close, pivot_volume, pivot_open
