import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd

from quant_engine.benchmark import compare_with_benchmark, fetch_benchmark_data
from quant_engine.data_loader import fetch_market_data, prepare_panel_data
from quant_engine.engine import build_engine


class DataPipelineTests(unittest.TestCase):
    def download(self, symbol, **kwargs):
        dates = pd.bdate_range("2024-01-01", periods=300)
        close = 100 * np.exp(np.arange(300) * 0.001 + np.sin(np.arange(300)) * 0.01)
        frame = pd.DataFrame({"Close": close, "High": close + 2,
                              "Low": close - 2, "Open": close + 1,
                              "Volume": 1000}, index=dates)
        frame.index.name = "Date"
        frame.columns = pd.MultiIndex.from_product([frame.columns, [symbol]])
        return frame

    @patch("quant_engine.data_loader.yf.download")
    def test_multiticker_columns_preserve_prices_and_pipeline_runs(self, download):
        download.side_effect = self.download
        raw = fetch_market_data(["AAPL", "MSFT"])
        prices, volume, opens = prepare_panel_data(raw)
        expected = self.download("AAPL")["Close"]["AAPL"]
        np.testing.assert_allclose(prices["AAPL"], expected)
        np.testing.assert_allclose(opens["AAPL"], expected + 1)
        self.assertTrue((volume == 1000).all().all())
        results = build_engine(symbols=["AAPL", "MSFT"])
        self.assertTrue(np.isfinite(results["final_value"]))
        self.assertEqual(len(results["returns"]), 300)

    @patch("quant_engine.benchmark.yf.download")
    def test_benchmark_is_series_and_aligns_mixed_calendars(self, download):
        download.side_effect = self.download
        benchmark = fetch_benchmark_data()
        self.assertIsInstance(benchmark, pd.Series)
        daily = benchmark.reindex(pd.date_range(benchmark.index[0], benchmark.index[-1])).ffill()
        result = compare_with_benchmark(daily.pct_change(), benchmark)
        self.assertTrue(np.isfinite(result["beta"]))

    def test_legacy_flat_columns_with_adjusted_close(self):
        frame = self.download("AAPL")
        frame.columns = frame.columns.get_level_values(0)
        frame["Adj Close"] = frame["Close"]
        with patch("quant_engine.data_loader.yf.download", return_value=frame):
            raw = fetch_market_data(["AAPL"])
        np.testing.assert_allclose(raw["Close"], frame["Close"])
        np.testing.assert_allclose(raw["Open"], frame["Open"])


if __name__ == "__main__":
    unittest.main()
