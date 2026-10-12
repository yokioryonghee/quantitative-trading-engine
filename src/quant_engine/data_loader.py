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
        DataFrame with multi-index (Date, Symbol) with OHLCV data.
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
    
    # Align all data to common dates
    aligned_list = []
    for sym, df in data_dict.items():
        df_copy = df.reset_index()
        df_copy["Symbol"] = sym
        aligned_list.append(df_copy)
    
    aligned_data = pd.concat(aligned_list, ignore_index=True)
    
    # Handle columns flexibly (some may not have Adj Close)
    if "Adj Close" in aligned_data.columns:
        aligned_data = aligned_data[["Date", "Open", "High", "Low", "Close", "Adj Close", "Volume", "Symbol"]]
    else:
        aligned_data = aligned_data[["Date", "Open", "High", "Low", "Close", "Volume", "Symbol"]]
    
    aligned_data["Date"] = pd.to_datetime(aligned_data["Date"])
    aligned_data = aligned_data.sort_values(["Date", "Symbol"]).reset_index(drop=True)
    
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
    
    # Forward fill for gaps, then backward fill (use newer pandas syntax)
    pivot_close = pivot_close.fillna(method="ffill").fillna(method="bfill")
    pivot_volume = pivot_volume.fillna(0)
    
    return pivot_close, pivot_volume, pivot_open
