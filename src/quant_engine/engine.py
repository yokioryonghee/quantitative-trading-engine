from __future__ import annotations

import pandas as pd

from quant_engine.backtest import run_backtest
from quant_engine.data_loader import load_market_data


def generate_report(df: pd.DataFrame, strategy_params: dict | None = None) -> dict:
    params = strategy_params or {"short_window": 10, "long_window": 30, "risk_per_trade": 0.01}
    report = run_backtest(df, **params)
    return report


def build_engine(config_path: str | None = None) -> dict:
    df = load_market_data(synthetic=True)
    params = {
        "short_window": 10,
        "long_window": 30,
        "risk_per_trade": 0.01,
    }
    return generate_report(df, params)
