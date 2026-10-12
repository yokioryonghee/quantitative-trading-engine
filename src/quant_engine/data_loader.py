from __future__ import annotations

from typing import Dict

import pandas as pd


def load_market_data(path: str | None = None, synthetic: bool = True) -> pd.DataFrame:
    if path is not None:
        df = pd.read_csv(path, parse_dates=["Date"])
        if "Close" not in df.columns:
            raise ValueError("CSV input must contain a 'Close' column.")
        return df.sort_values("Date").reset_index(drop=True)

    if synthetic:
        import numpy as np

        rng = np.random.default_rng(42)
        n = 252 * 2
        drift = 0.0007
        noise = rng.normal(0, 0.012, n)
        prices = 100 * np.exp(np.cumsum(drift + noise))
        dates = pd.date_range("2023-01-01", periods=n, freq="B")
        return pd.DataFrame({"Date": dates, "Close": prices})

    raise ValueError("Either provide a CSV path or set synthetic=True.")


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    cols = {c.lower(): c for c in df.columns}
    normalized = df.copy()
    normalized = normalized.rename(columns={v: k for k, v in cols.items()})
    return normalized
