# quantitative-trading-engine

Production-grade quantitative trading system with signal generation, backtesting, risk controls, and portfolio analytics.

A hiring manager should immediately understand this project as a real algorithmic trading engine rather than a toy script. The repository is designed around a clean pipeline:

- Market data ingestion
- Feature engineering and signal generation
- Risk management and position sizing
- Backtesting and performance analytics
- Reporting and portfolio evaluation

## Why this project stands out

This is not just a simple moving-average bot. It is structured like an engineering system:

- modular design with distinct responsibilities
- config-driven strategy parameters
- backtesting with performance metrics
- drawdown and Sharpe-ratio analysis
- explicit risk controls that matter in real trading

## Architecture

```text
market-data -> feature-engineering -> signal-generation -> risk-management -> backtest -> reporting
      |                              |                    |              |             |
      v                              v                    v              v             v
   data loader                 indicators           position sizing   performance   portfolio summary
```

## Core modules

- `src/quant_engine/data_loader.py`: ingest and normalize market data
- `src/quant_engine/indicators.py`: feature and signal generation
- `src/quant_engine/risk.py`: volatility, drawdown, position sizing, Sharpe analysis
- `src/quant_engine/backtest.py`: strategy simulation and performance metrics
- `src/quant_engine/engine.py`: orchestration layer for complete workflow

## Quick start

1. Install dependencies

```bash
pip install -r requirements.txt
```

2. Run the example backtest

```bash
PYTHONPATH=src python examples/run_backtest.py
```

## Typical metrics reported

- cumulative return
- annualized return
- volatility
- Sharpe ratio
- maximum drawdown
- turnover / exposure

## What recruiters see

This project communicates a clear story:

- data-aware engineering
- strategy design
- risk consciousness
- validation mindset
- production-style system thinking

## Stack

- Python
- pandas
- numpy
- matplotlib
- pyyaml

## License

MIT
