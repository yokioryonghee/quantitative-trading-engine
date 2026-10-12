# quantitative-trading-engine

A production-ready algorithmic trading system that handles signal generation, backtesting, risk management, and portfolio analysis in a unified pipeline.

## The problem

Most trading bots are toy scripts—they generate buy/sell signals without thinking about real-world constraints like position sizing, drawdown control, or whether the strategy actually works on historical data.

This project takes it seriously. It's built like a real trading engine: data flows through feature engineering → signal generation → position sizing → backtest validation → performance reporting.

## What's inside

**Data ingestion**: Load and normalize market data from files or generate synthetic data for testing.

**Signal generation**: Technical indicators (SMA, EMA) combined with multi-timeframe logic to create trading signals.

**Risk management**: Compute volatility, position sizing based on risk tolerance, and track maximum drawdown—the stuff that keeps traders from blowing up accounts.

**Backtesting**: Run strategy simulations and measure what actually matters: cumulative return, Sharpe ratio, annualized return, max drawdown.

**Clean architecture**: Each module has one job. Easy to extend, easy to test, easy to reason about.

## Quick start

```bash
pip install -r requirements.txt
PYTHONPATH=src python examples/run_backtest.py
```

Output:
```
Cumulative Return: 0.4523
Annualized Return: 0.2145
Sharpe Ratio: 1.8732
Max Drawdown: -0.1203
```

## Structure

```
src/quant_engine/
├── data_loader.py      # Market data handling
├── indicators.py       # Technical signals
├── risk.py            # Position sizing, drawdown, Sharpe
├── backtest.py        # Strategy simulation
└── engine.py          # Orchestration
```

## Why this matters

This demonstrates:
- **Systems thinking**: Data → feature → signal → validation pipeline
- **Risk awareness**: Not just returns, but drawdown and volatility management
- **Engineering discipline**: Modular, testable, extensible code
- **Validation mindset**: Always backtest before trading

## Stack

Python • pandas • numpy • matplotlib

---

### 한국어

# quantitative-trading-engine

실제 운영을 상상할 수 있는 알고리즘 트레이딩 엔진. 데이터 수집부터 신호 생성, 리스크 관리, 백테스트까지 한 파이프라인으로 처리한다.

## 문제

대부분의 자동매매 봇은 단순한 스크립트에 불과하다. 신호를 뽑는 데는 능숙하지만, 포지션 크기 조절, 손절한도, 과거 데이터에서 실제로 통하는지 검증하는 부분은 거의 다루지 않는다.

설계: 데이터 → 기술지표 → 신호 생성 → 포지션 사이징 → 백테스트 검증 → 성과 분석.

## 구성

**데이터 로드**: CSV 파일 또는 합성 데이터를 통해 시장 데이터 처리.

**신호 생성**: 이동평균(SMA, EMA) 등 기술지표를 조합해 거래 신호 생성.

**리스크 관리**: 변동성 계산, 위험도 기반 포지션 크기 결정, 최대 낙폭 추적—계좌를 망치지 않게 하는 핵심 요소다.

**백테스트**: 전략을 과거 데이터로 시뮬레이션하고 실제 중요한 지표를 측정한다 (수익률, 샤프 지수, 최대 낙폭).

**깔끔한 구조**: 각 모듈이 한 가지 책임만 갖도록 만들어 확장과 테스트가 쉽다.

## 실행

```bash
pip install -r requirements.txt
PYTHONPATH=src python examples/run_backtest.py
```

결과:
```
Cumulative Return: 0.4523
Annualized Return: 0.2145
Sharpe Ratio: 1.8732
Max Drawdown: -0.1203
```

## 폴더 구조

```
src/quant_engine/
├── data_loader.py      # 시장 데이터 처리
├── indicators.py       # 기술 신호 생성
├── risk.py            # 포지션 크기, 낙폭, 샤프 지수
├── backtest.py        # 전략 시뮬레이션
└── engine.py          # 전체 조율
```




- **리스크 인식**: 수익률만 보지 않고 변동성과 낙폭까지 고려
- **엔지니어링 역량**: 모듈화, 확장성, 테스트 가능성
- **검증 습관**: 트레이딩 전 백테스트로 타당성을 검증

## 기술 스택

Python • pandas • numpy • matplotlib
