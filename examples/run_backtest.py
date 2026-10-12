from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from quant_engine.engine import build_engine


if __name__ == "__main__":
    # Run engine with optimal multi-asset strategy
    results = build_engine(
        initial_capital=100000.0,
        target_leverage=1.5,
    )
