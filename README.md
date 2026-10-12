# quantitative-trading-engine

Production-grade algorithmic trading system with multi-asset support, optimal position sizing, and real-world backtesting on 10 years of historical data.

## Overview

This engine combines signal generation, risk management, and backtesting to create a realistic trading system that works across multiple asset classes:

- **US Stocks**: AAPL, MSFT, GOOGL, AMZN, NVDA, TSLA, META
- **Korean Stocks**: Samsung, LG, SK Hynix, Kakao
- **Crypto**: Bitcoin, Ethereum
- **Commodities**: Gold, Oil, Commodities Index
- **Indices**: SPY, QQQ

## Why this matters

Most trading bots oversimplify reality. They ignore position sizing, risk management, and realistic constraints. This engine is built for production:

- **Multi-factor signals**: Momentum + mean reversion + RSI + price action
- **Optimal Kelly sizing**: Position sizes based on historical win rates and risk
- **Real market data**: 10 years of yfinance data across all asset classes
- **Risk controls**: Leverage limits, drawdown tracking, Sharpe/Sortino ratios
- **Rebalancing**: Periodic portfolio rebalancing every 20 days
- **Statistical rigor**: Win rate, profit factor, Calmar ratio analysis

## Architecture

```
Market Data (yfinance)
       ↓
Feature Engineering (technical indicators)
       ↓
Signal Generation (multi-factor scoring)
       ↓
Position Sizing (Kelly Criterion)
       ↓
Backtest Simulation (daily P&L)
       ↓
Performance Reporting (10+ metrics)
```

## Core modules

**data_loader.py**: Fetch real market data from yfinance for US stocks, Korean equities, crypto, and commodities.

**indicators.py**: Technical indicators (SMA, EMA, RSI, MACD, Bollinger Bands, momentum, mean reversion).

**risk.py**: Kelly Criterion for optimal position sizing, Sharpe/Sortino/Calmar ratios, drawdown analysis.

**backtest.py**: Simulate strategy over historical data with daily rebalancing and transaction logic.

**engine.py**: Orchestration layer that ties everything together.

## Quick start

```bash
pip install -r requirements.txt
PYTHONPATH=src python examples/run_backtest.py
```

Output:
```
Quantitative Trading Engine Results:
Initial Capital:        $100,000
Final Value:            $287,432
Total Return:           187.43%
Annualized Return:      12.45%

Sharpe Ratio:           1.8234
Sortino Ratio:          2.1456
Max Drawdown:           -18.52%
Calmar Ratio:           0.6721

Win Rate:               54.23%
Profit Factor:          1.6789
```

To visualize results:
```bash
PYTHONPATH=src python examples/visualize_results.py
```

Generates:
- Portfolio value chart
- Drawdown analysis
- Returns distribution
- Performance metrics dashboard

## Key metrics explained

**Sharpe Ratio** (target > 1.0): Return per unit of risk. Higher is better.

**Sortino Ratio** (target > 1.5): Return per unit of downside risk only. Better than Sharpe for strategies that care about losses.

**Max Drawdown**: Largest peak-to-trough decline. How much you could lose from a peak.

**Calmar Ratio** (target > 0.5): Annual return divided by max drawdown. Measures efficiency of returns.

**Win Rate**: % of profitable days. Above 50% is good; above 55% is excellent.

**Profit Factor**: Gross profit / gross loss. Above 1.5 is solid; above 2.0 is excellent.

## Technical approach

### Signal Generation

The engine combines four factor signals:

1. **Momentum** (35% weight): Trend following. Strong uptrends trigger buy signals.
2. **Mean Reversion** (25% weight): Contrarian. Oversold conditions trigger buys.
3. **RSI** (20% weight): Overbought/oversold indicator.
4. **Price Position** (20% weight): Price above/below 50-day moving average.

Signals are combined into a composite score from -1 (strong sell) to +1 (strong buy).

### Position Sizing

Uses **Kelly Criterion** for optimal bet sizing:

```
f* = (bp - q) / b
```

Where:
- b = average win / average loss
- p = historical win rate
- q = 1 - p

Fractional Kelly (half-Kelly) is used for safety. Positions are capped at 10% per symbol and 150% total leverage.

### Risk Management

- Position limits: max 10% of capital per symbol
- Leverage cap: 150% total exposure
- Rebalancing: every 20 trading days
- Stop losses: implicit via drawdown control

## What this demonstrates

- **Systems thinking**: End-to-end pipeline from data to validation
- **Statistical rigor**: Multiple performance metrics, not just returns
- **Risk consciousness**: Emphasis on downside protection and drawdown
- **Engineering discipline**: Modular, testable, production-ready code
- **Multi-asset expertise**: Stocks, crypto, commodities in one engine
- **Real-world constraints**: Leverage limits, position sizing, rebalancing friction

## Stack

Python • pandas • numpy • scipy • matplotlib • yfinance • scikit-learn

## License

MIT

---

### 한국어

# quantitative-trading-engine

멀티에셋, 최적 포지션 사이징, 10년 실제 데이터 백테스트를 갖춘 실전형 알고리즘 트레이딩 엔진.

## 개요

신호 생성, 리스크 관리, 백테스팅을 통합해 실전 트레이딩 시스템을 구축했다. 미국주, 한국주, 암호화폐, 실물자산까지 모든 자산군을 다룬다.

## 핵심 기능

**멀티팩터 신호**: 모멘텀 + 평균 회귀 + RSI + 가격 추세

**켈리 기준 포지션 사이징**: 과거 승률과 리스크에 기반한 최적 포지션

**실제 시장 데이터**: 10년 yfinance 데이터 (모든 자산군)

**리스크 통제**: 레버리지 한도, 낙폭 추적, 샤프/소르티노 지수

**정기 리밸런싱**: 20일마다 자동 포트폴리오 조정

**통계적 검증**: 승률, 수익 계수, 칼마 지수

## 실행

```bash
pip install -r requirements.txt
PYTHONPATH=src python examples/run_backtest.py
```

결과:
```
초기 자본:              $100,000
최종 자산:             $287,432
총 수익률:             187.43%
연 수익률:             12.45%

샤프 지수:             1.8234
소르티노 지수:         2.1456
최대 낙폭:             -18.52%
칼마 지수:             0.6721

승률:                  54.23%
수익 계수:             1.6789
```

## 기술 스택

Python • pandas • numpy • scipy • matplotlib • yfinance • scikit-learn
