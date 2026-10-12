from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from quant_engine.data_loader import load_market_data
from quant_engine.engine import build_engine


if __name__ == "__main__":
    df = load_market_data(synthetic=True)
    report = build_engine()
    print("Cumulative Return:", round(report["cumulative_return"], 4))
    print("Annualized Return:", round(report["annualized_return"], 4))
    print("Sharpe Ratio:", round(report["sharpe_ratio"], 4))
    print("Max Drawdown:", round(report["max_drawdown"], 4))
