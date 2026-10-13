import runpy
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from quant_engine import backtest, benchmark, data_loader, engine
from quant_engine.risk import allocate_positions_optimal


@pytest.fixture
def prices():
    rng = np.random.default_rng(42)
    return pd.DataFrame(
        100 * np.cumprod(1 + rng.normal(.002, .012, (300, 3)), axis=0),
        index=pd.bdate_range('2023-01-02', periods=300, name='Date'),
        columns=['AAPL', 'MSFT', 'SPY'],
    )


@pytest.mark.parametrize('layout', ['flat', 'field_first', 'ticker_first'])
def test_download_formats(monkeypatch, prices, layout):
    def download(symbol, **kwargs):
        close = prices[symbol]
        df = pd.DataFrame({'Open': close, 'High': close * 1.01, 'Low': close * .99, 'Close': close, 'Volume': 100}, index=close.index)
        if layout != 'flat':
            df.columns = pd.MultiIndex.from_tuples([(col, symbol) if layout == 'field_first' else (symbol, col) for col in df.columns])
        return df
    monkeypatch.setattr(data_loader.yf, 'download', download)
    raw = data_loader.fetch_market_data(list(prices))
    panel, volume, _ = data_loader.prepare_panel_data(raw)
    pd.testing.assert_frame_equal(panel, prices, check_names=False, check_freq=False)
    result = engine.build_engine(symbols=list(prices))
    assert np.isfinite(result['final_value'])
    assert result['num_trades'] > 0
    series = benchmark.fetch_benchmark_data()
    assert isinstance(series, pd.Series)
    comparison = benchmark.compare_with_benchmark(result['returns'], series)
    assert np.isfinite(comparison['beta'])


def test_download_failure_preserves_reason(monkeypatch):
    def fail(*args, **kwargs):
        raise RuntimeError('upstream unavailable')
    monkeypatch.setattr(data_loader.yf, 'download', fail)
    with pytest.raises(ValueError, match='AAPL: upstream unavailable'):
        data_loader.fetch_market_data(['AAPL'])


def test_panel_does_not_backfill_prelisting(prices):
    rows = []
    for i, symbol in enumerate(prices):
        close = prices[symbol].iloc[i * 30:]
        rows.extend({'Date': day, 'Symbol': symbol, 'Close': value, 'Open': value, 'Volume': 100} for day, value in close.items())
    panel, _, _ = data_loader.prepare_panel_data(pd.DataFrame(rows))
    assert panel.index[0] == prices.index[60]


def test_limits_and_causality(prices):
    returns = prices.pct_change().fillna(0)
    signals = pd.DataFrame(.4, index=prices.index, columns=prices.columns)
    positions = allocate_positions_optimal(signals, returns, target_leverage=.15)
    assert positions.abs().max().max() <= .10 + 1e-12
    assert positions.abs().sum(axis=1).max() <= .15 + 1e-12
    changed = returns.copy()
    changed.iloc[150:] = -.2
    actual = allocate_positions_optimal(signals, changed, target_leverage=.15)
    pd.testing.assert_frame_equal(positions.iloc[:150], actual.iloc[:150])
    assert allocate_positions_optimal(signals * 0, returns).eq(0).all().all()


def test_backtest_prefix_and_rebalancing(prices):
    volume = prices * 0 + 100
    result = backtest.run_backtest(prices, volume)
    changed = prices.copy()
    changed.iloc[150:] *= .5
    altered = backtest.run_backtest(changed, volume)
    pd.testing.assert_series_equal(result['returns'].iloc[:150], altered['returns'].iloc[:150])
    positions = result['positions']
    changes = positions.sub(positions.shift(1).fillna(0)).abs().gt(1e-12)
    assert result['num_trades'] == len(result['trade_ledger']) > 0
    assert all(prices.index.get_loc(row['date']) % 20 == 1 for row in result['trade_ledger'])
    assert all(i % 20 == 0 for i in np.flatnonzero(changes.any(axis=1)))


def test_benchmark_calendar_and_beta():
    daily = pd.date_range('2024-01-01', periods=40)
    returns = pd.Series(np.linspace(-.01, .02, 40), index=daily)
    wealth = (1 + returns).cumprod()
    benchmark_prices = wealth.loc[wealth.index.dayofweek < 5] * 100
    result = benchmark.compare_with_benchmark(returns, benchmark_prices)
    assert result['beta'] == pytest.approx(1)
    assert result['outperformance'] == pytest.approx(0)


def test_parameter_sweep_uses_same_backtest(prices):
    result = benchmark.parameter_sweep(prices, prices * 0, [10], [30])[0]
    expected = backtest.run_backtest(prices, prices * 0, momentum_window=10, mean_reversion_window=30)
    assert result['total_return'] == expected['total_return']
    assert result['sharpe_ratio'] == expected['sharpe_ratio']


@pytest.mark.parametrize('script', ['run_backtest.py', 'comprehensive_analysis.py', 'visualize_comprehensive.py', 'visualize_results.py'])
def test_examples_run_offline(monkeypatch, tmp_path, prices, script):
    import matplotlib.pyplot as plt
    def download(symbol, **kwargs):
        close = prices['SPY']
        if symbol == 'KRW=X':
            dates=pd.bdate_range(close.index.min()-pd.Timedelta(days=10),close.index.max())
            close=pd.Series(1000.,index=dates)
        return pd.DataFrame({'Open': close, 'Close': close, 'High': close, 'Low': close, 'Volume': 100}, index=close.index)
    monkeypatch.setattr(data_loader.yf, 'download', download)
    monkeypatch.setattr(plt, 'show', lambda: None)
    example = Path(__file__).resolve().parents[1] / 'examples' / script
    monkeypatch.chdir(tmp_path)
    runpy.run_path(str(example), run_name='__main__')
    if script.startswith('visualize'):
        assert list(tmp_path.glob('*.png'))
    plt.close('all')

