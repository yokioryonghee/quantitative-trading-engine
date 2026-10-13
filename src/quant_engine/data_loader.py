from __future__ import annotations

from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import yfinance as yf


# Multi-asset universe: US stocks, Korean stocks, crypto, commodities
ASSET_UNIVERSE = {
    "us_stocks": ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META"],
    "korean_stocks": ["005930.KS", "051910.KS", "000660.KS", "207940.KS"],
    "crypto": ["BTC-USD", "ETH-USD"],
    "commodities": ["GLD", "USO", "DBC"],  # Gold, Oil, Commodities
    "indices": ["SPY", "QQQ"],  # Market indices for hedging
}


def normalize_download(df: pd.DataFrame, symbol: str) -> pd.DataFrame:
    """Normalize flat and either ordering of yfinance MultiIndex columns."""
    df = df.copy()
    if isinstance(df.columns, pd.MultiIndex):
        for level in range(df.columns.nlevels):
            if symbol in df.columns.get_level_values(level):
                df = df.xs(symbol, level=level, axis=1)
                break
        if isinstance(df.columns, pd.MultiIndex):
            raise ValueError(f"Cannot identify OHLC columns for {symbol}")
    df.columns = [str(col).lower() for col in df.columns]
    if "close" not in df.columns or "open" not in df.columns:
        raise ValueError(f"Missing Open/Close columns for {symbol}")
    df.index = pd.to_datetime(df.index).tz_localize(None)
    df.index.name = "Date"
    return df


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
    
    if not symbols:
        raise ValueError("At least one symbol is required")
    data_list = []
    failures = []
    successful_symbols = []
    
    for symbol in symbols:
        try:
            df = yf.download(symbol, start=start_date, end=end_date, progress=False, auto_adjust=True, multi_level_index=False, timeout=20)
            if df is None or df.empty:
                failures.append(f"{symbol}: no data returned")
                print(f"✗ {symbol}: No data")
                continue
            
            # Reset index to convert Date from index to column
            df = normalize_download(df, symbol).reset_index()
            
            # Standardize column names to lowercase
            df.columns = [col.lower() for col in df.columns]
            
            # Create normalized dataframe with required columns only
            normalized = pd.DataFrame({
                'Date': pd.to_datetime(df['date']),
                'Open': pd.to_numeric(df.get('open', np.nan), errors='coerce'),
                'High': pd.to_numeric(df.get('high', np.nan), errors='coerce'),
                'Low': pd.to_numeric(df.get('low', np.nan), errors='coerce'),
                'Close': pd.to_numeric(df.get('close', np.nan), errors='coerce'),
                'Volume': pd.to_numeric(df.get('volume', pd.Series(0, index=df.index)), errors='coerce').fillna(0),
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
            failures.append(f"{symbol}: {e}")
            print(f"✗ {symbol}: {e}")
    
    if not data_list:
        raise ValueError("No data fetched: " + "; ".join(failures))
    
    # Concatenate all data
    aligned_data = pd.concat(data_list, ignore_index=True)
    
    # Sort by Date and Symbol for consistent ordering
    aligned_data = aligned_data.sort_values(['Date', 'Symbol']).reset_index(drop=True)
    
    # Forward fill any remaining NaN values in OHLC using new pandas syntax
    for col in ['Open', 'High', 'Low', 'Close']:
        aligned_data[col] = aligned_data.groupby('Symbol')[col].transform(lambda x: x.ffill())
    
    return aligned_data


def get_optimal_universe() -> list[str]:
    """
    Return the fixed example universe; this is not an optimized or survivorship-free universe.
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
    
    # Carry known prices over closed-market days; never invent pre-listing prices.
    pivot_close = pivot_close.ffill()
    pivot_volume = pivot_volume.fillna(0)
    pivot_open = pivot_open.ffill()
    
    # Remove any remaining NaN rows
    valid_idx = ~(pivot_close.isna().any(axis=1) | pivot_open.isna().any(axis=1))
    pivot_close = pivot_close[valid_idx]
    pivot_volume = pivot_volume.reindex(index=pivot_close.index, columns=pivot_close.columns).fillna(0)
    pivot_open = pivot_open.loc[pivot_close.index]
    
    if pivot_close.shape[1] == 0:
        raise ValueError("No valid price columns available")
    # Ensure all have at least 100 observations
    if len(pivot_close) < 100:
        raise ValueError(f"Insufficient data: only {len(pivot_close)} trading days available (need at least 100)")
    
    return pivot_close, pivot_volume, pivot_open



def convert_to_usd(raw):
    """Convert Korean OHLC quotes to USD using observed USD/KRW daily FX."""
    korean=raw.Symbol.astype(str).str.endswith(('.KS','.KQ'))
    if not korean.any(): return raw
    start=(raw.loc[korean,'Date'].min()-pd.Timedelta(days=10)).strftime('%Y-%m-%d')
    end=(raw.loc[korean,'Date'].max()+pd.Timedelta(days=1)).strftime('%Y-%m-%d')
    downloaded=yf.download('KRW=X',start=start,end=end,progress=False,auto_adjust=True,multi_level_index=False,timeout=20)
    if downloaded is None or downloaded.empty: raise ValueError('USD/KRW FX required for Korean assets')
    fx=normalize_download(downloaded,'KRW=X')['close'].sort_index()
    dates=pd.DatetimeIndex(raw.loc[korean,'Date'])
    rates=fx.reindex(fx.index.union(dates)).ffill().reindex(dates).to_numpy()
    if not np.isfinite(rates).all() or (rates<=0).any(): raise ValueError('Missing/invalid observed FX rates')
    result=raw.copy()
    for field in ['Open','High','Low','Close']:
        result.loc[korean,field]=result.loc[korean,field].to_numpy()/rates
    return result
