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
    
    data_dict = {}
    for symbol in symbols:
        try:
            df = yf.download(symbol, start=start_date, end=end_date, progress=False)
            if not df.empty:
                data_dict[symbol] = df
                print(f"✓ {symbol}")
            else:
                print(f"✗ {symbol}: No data")
        except Exception as e:
            print(f"✗ {symbol}: {str(e)[:50]}")
    
    if not data_dict:
        raise ValueError("No data fetched. Check symbols and internet connection.")
    
    # Normalize and align all data
    aligned_list = []
    for sym, df in data_dict.items():
        df_copy = df.reset_index()
        
        # Standardize column names
        df_copy.columns = [col.lower() for col in df_copy.columns]
        
        # Extract only required columns, handle missing ones
        df_normalized = pd.DataFrame()
        df_normalized['Date'] = pd.to_datetime(df_copy['date'])
        df_normalized['Open'] = df_copy.get('open', np.nan)
        df_normalized['High'] = df_copy.get('high', np.nan)
        df_normalized['Low'] = df_copy.get('low', np.nan)
        df_normalized['Close'] = df_copy.get('close', np.nan)
        df_normalized['Volume'] = df_copy.get('volume', 0.0)
        df_normalized['Symbol'] = sym
        
        aligned_list.append(df_normalized)
    
    # Concatenate all normalized data
    aligned_data = pd.concat(aligned_list, ignore_index=True)
    aligned_data = aligned_data.sort_values(['Date', 'Symbol']).reset_index(drop=True)
    
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
    """
    pivot_close = df.pivot_table(index="Date", columns="Symbol", values="Close")
    pivot_volume = df.pivot_table(index="Date", columns="Symbol", values="Volume")
    pivot_open = df.pivot_table(index="Date", columns="Symbol", values="Open")
    
    # Forward fill for gaps, then backward fill (handle leading/trailing NaNs)
    pivot_close = pivot_close.ffill().bfill()
    pivot_volume = pivot_volume.fillna(0)
    pivot_open = pivot_open.ffill().bfill()
    
    # Remove any rows with NaN values
    pivot_close = pivot_close.dropna()
    pivot_volume = pivot_volume.loc[pivot_close.index]
    pivot_open = pivot_open.loc[pivot_close.index]
    
    return pivot_close, pivot_volume, pivot_open
