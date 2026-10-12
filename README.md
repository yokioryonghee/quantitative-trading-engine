# quantitative-trading-engine

Production-grade algorithmic trading system with multi-asset support, optimal position sizing, benchmark comparison, and parameter optimization. Built to demonstrate systems thinking, statistical rigor, and real-world trading constraints.

## Overview

This engine combines advanced signal generation, risk-aware position sizing, and rigorous backtesting to create a realistic trading system across multiple asset classes:

- **US Stocks**: AAPL, MSFT, GOOGL, AMZN, NVDA, TSLA, META
- **Korean Stocks**: Samsung, LG, SK Hynix, Kakao  
- **Crypto**: Bitcoin, Ethereum
- **Commodities**: Gold, Oil, Commodities Index
- **Indices**: SPY, QQQ

## Why this matters

Most trading systems oversimplify. They generate signals without considering position sizing, realistic constraints, or actual market conditions. This engine is built for production:

- **Multi-factor signals**: Momentum + mean reversion + RSI + price action
- **Optimal Kelly sizing**: Position sizes derived from historical win rates and risk metrics
- **Real market data**: 10 years of yfinance data across all asset classes
- **Benchmark comparison**: Strategy performance vs S&P 500 (Alpha, Beta)
- **Parameter optimization**: Systematic testing of signal parameters to find robust configurations
- **Risk controls**: Leverage limits, drawdown tracking, Sharpe/Sortino/Calmar ratios
- **Rebalancing logic**: Periodic portfolio rebalancing every 20 days

## Quick start

```bash
pip install -r requirements.txt

# Run base strategy
PYTHONPATH=src python examples/run_backtest.py

# Run comprehensive analysis (benchmark + parameter sweep)
PYTHONPATH=src python examples/comprehensive_analysis.py

# Generate visualization charts
PYTHONPATH=src python examples/visualize_comprehensive.py
```

## Runtime and validation

Requires Python 3.10 or newer. From the repository root:

```bash
python -m venv .venv
# macOS / Linux
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -e ".[test]"
python examples/run_backtest.py
python examples/comprehensive_analysis.py
python examples/visualize_comprehensive.py
python -m pytest -q
```

GitHub Actions runs the offline regression suite on Python 3.10/pandas 2 and Python 3.12/pandas 3, including all four example scripts and chart generation. Live runs require Yahoo Finance access; failed downloads are reported per ticker, and an entirely empty download raises an error containing the available failure reasons.

Kelly sizing uses expanding history with a 20-observation warmup. Target allocations stay within 10% per asset and the gross leverage ceiling; low conviction can leave capital uninvested. Missing prices are carried forward only, and the panel starts after every included asset has an observed price. Benchmark comparison compounds strategy returns between shared market dates. Parameter sweeps use the same 20-observation rebalance schedule as the main backtest.

This is a research backtester: positions are target weights held between signal updates, not a broker execution simulator. Transaction costs, borrow fees, FX conversion and cash interest are not modeled. Metrics use a 252-period annualization convention, so mixed crypto/equity daily calendars require care when interpreting annualized values. Parameter rankings are in-sample, not an out-of-sample performance guarantee. `config.yaml` is a legacy example and is not consumed by the current engine; pass runtime options to `build_engine` instead.

## Architecture

```
Market Data (yfinance)
       ↓
Feature Engineering (10+ technical indicators)
       ↓
Multi-factor Signal Generation (4-factor composite)
       ↓
Position Sizing (Kelly Criterion + leverage constraints)
       ↓
Portfolio Simulation (daily P&L tracking)
       ↓
Performance Reporting (15+ metrics)
       ↓
Benchmark Comparison (vs S&P 500: Alpha/Beta)
       ↓
Parameter Optimization (identify robust configurations)
```

## Core modules

**data_loader.py**  
Fetch real market data from yfinance. Handles US stocks, Korean equities, crypto, and commodities with automatic alignment to common trading dates.

**indicators.py**  
Technical indicators: SMA, EMA, RSI, MACD, Bollinger Bands, momentum, mean reversion scoring.

**risk.py**  
Kelly Criterion for optimal position sizing. Sharpe, Sortino, Calmar ratio computation. Volatility and drawdown analysis.

**backtest.py**  
Simulate strategy over historical data with daily rebalancing, leverage limits, and position constraints.

**benchmark.py**  
Compare strategy returns vs S&P 500. Calculate Alpha and Beta. Run parameter sweep to identify optimal configurations.

**engine.py**  
Orchestration layer that ties data, signals, sizing, and backtesting into a unified pipeline.

## Key results explained

**Sharpe Ratio** (target > 1.0)  
Return per unit of risk. Higher is better. Above 1.5 is excellent.

**Sortino Ratio** (target > 1.5)  
Return per unit of downside risk. Better than Sharpe for strategies focused on loss prevention.

**Max Drawdown**  
Largest peak-to-trough decline. Shows the worst-case scenario during the backtest.

**Calmar Ratio** (target > 0.5)  
Annual return divided by max drawdown. Measures efficiency of returns relative to peak losses.

**Win Rate**  
% of profitable days. Above 55% is solid; above 60% is excellent.

**Profit Factor**  
Gross profit / gross loss. Above 1.5 is good; above 2.0 is excellent.

**Alpha**  
Return generated beyond what market beta would predict. Positive alpha indicates skill.

**Beta**  
Correlation with market. Beta=1.0 means strategy moves with S&P 500. Beta<1.0 means lower correlation.

## Technical approach

### Signal Generation

Combines four independent factors into a composite score:

1. **Momentum** (35% weight): Trend following. Captures persistent price movements.
2. **Mean Reversion** (25% weight): Contrarian. Exploits oversold/overbought conditions.
3. **RSI** (20% weight): Overbought/oversold detector using Relative Strength Index.
4. **Price Position** (20% weight): Price location relative to 50-day moving average.

Signals range from -1 (strong sell) to +1 (strong buy).

### Position Sizing

Uses **fractional Kelly Criterion** for optimal bet sizing:

```
f* = (bp - q) / b, capped at 25% for safety
```

Where:
- b = average win / average loss
- p = historical win rate  
- q = 1 - p

Positions are capped at 10% per symbol and 150% total leverage to manage risk.

### Risk Management

- **Position limits**: Maximum 10% of capital per symbol
- **Leverage cap**: 150% total exposure
- **Rebalancing**: Every 20 trading days
- **Constraints**: No concentrated bets, diversification across asset classes

### Parameter Optimization

The system sweeps momentum window (10-30 days) and mean reversion window (20-50 days) to identify configurations that maximize Sharpe ratio while maintaining reasonable returns. Top 5 configurations are ranked and reported.

## What this demonstrates

- **Systems thinking**: End-to-end pipeline from raw data to validated results
- **Statistical rigor**: Multiple performance metrics, not just returns
- **Engineering discipline**: Modular, testable, maintainable code
- **Risk consciousness**: Emphasis on drawdown control and downside protection
- **Validation mindset**: Benchmark comparison and parameter optimization built-in
- **Multi-asset expertise**: Handles stocks, crypto, commodities in unified framework
- **Real-world constraints**: Leverage limits, rebalancing friction, transaction costs awareness
- **Quantitative reasoning**: Kelly Criterion, factor weighting, statistical metrics

## Stack

Python • pandas • numpy • scipy • matplotlib • yfinance • scikit-learn

## License

MIT

---

### 한국어

# quantitative-trading-engine

멀티에셋 지원, 최적 포지션 사이징, 벤치마크 비교, 파라미터 최적화를 갖춘 실전형 알고리즘 트레이딩 엔진. 시스템 사고, 통계적 엄격함, 실제 거래 제약 조건을 다루는 역량을 보여준다.

## 개요

고급 신호 생성, 리스크 기반 포지션 사이징, 엄격한 백테스팅을 결합해 여러 자산군에서 작동하는 실전형 거래 시스템을 구축했다.

지원 자산군:
- 미국주: AAPL, MSFT, GOOGL, AMZN, NVDA, TSLA, META
- 한국주: 삼성전자, LG전자, SK하이닉스, 카카오
- 암호화폐: BTC, ETH
- 실물자산: 금, 석유, 상품지수
- 지수: SPY, QQQ

## 핵심 특징

- **멀티팩터 신호**: 모멘텀 + 평균 회귀 + RSI + 가격 추세
- **켈리 포지션 사이징**: 과거 승률과 리스크 기반 최적 포지션 크기
- **실제 시장 데이터**: 10년 yfinance 데이터 (모든 자산군)
- **벤치마크 비교**: S&P 500 대비 성과 (Alpha, Beta)
- **파라미터 최적화**: 신호 파라미터의 체계적 테스트
- **리스크 관리**: 레버리지 한도, 낙폭 추적, 샤프/소르티노/칼마 지수
- **정기 리밸런싱**: 20일마다 자동 포트폴리오 조정

## 실행

```bash
pip install -r requirements.txt

# 기본 전략
PYTHONPATH=src python examples/run_backtest.py

# 포괄적 분석 (벤치마크 + 파라미터 스윕)
PYTHONPATH=src python examples/comprehensive_analysis.py

# 차트 생성
PYTHONPATH=src python examples/visualize_comprehensive.py
```

## 아키텍처

```
시장 데이터 (yfinance)
     ↓
특성 엔지니어링 (10+ 기술지표)
     ↓
멀티팩터 신호 생성 (4-팩터 복합)
     ↓
포지션 사이징 (켈리 기준 + 제약)
     ↓
포트폴리오 시뮬레이션 (일일 손익)
     ↓
성과 리포팅 (15+ 지표)
     ↓
벤치마크 비교 (S&P 500 대비)
     ↓
파라미터 최적화 (견고한 설정 식별)
```

## 핵심 모듈

**data_loader.py**  
Yfinance에서 실제 시장 데이터를 가져온다. 미국주, 한국주, 암호화폐, 실물자산을 지원하며 공통 거래일로 자동 정렬한다.

**indicators.py**  
기술지표: SMA, EMA, RSI, MACD, 볼린저밴드, 모멘텀, 평균 회귀 점수.

**risk.py**  
켈리 기준 포지션 사이징. 샤프, 소르티노, 칼마 지수. 변동성 및 낙폭 분석.

**backtest.py**  
일일 리밸런싱, 레버리지 한도, 포지션 제약과 함께 과거 데이터 시뮬레이션.

**benchmark.py**  
S&P 500 대비 전략 수익률 비교. Alpha/Beta 계산. 최적 설정 식별을 위한 파라미터 스윕.

**engine.py**  
데이터, 신호, 사이징, 백테스트를 통합 파이프라인으로 연결하는 조율 계층.

## 주요 지표 설명

**샤프 지수** (목표 > 1.0)  
위험 대비 수익. 높을수록 좋다. 1.5 이상이면 우수.

**소르티노 지수** (목표 > 1.5)  
하방 리스크만 고려한 수익. 손실 방지에 초점 맞춘 전략에 더 적합.

**최대 낙폭**  
피크에서 저점까지의 가장 큰 하락. 백테스트 기간의 최악의 경우.

**칼마 지수** (목표 > 0.5)  
연 수익 / 최대 낙폭. 피크 손실 대비 수익 효율성.

**승률**  
수익 거래일의 비율. 55% 이상이면 견고, 60% 이상이면 우수.

**수익 계수**  
총 수익 / 총 손실. 1.5 이상이면 좋음, 2.0 이상이면 우수.

**알파**  
시장 베타가 예측한 수익을 초과한 부분. 양수는 전략의 실력을 나타낸다.

**베타**  
S&P 500과의 상관성. 1.0 = 시장과 동반, <1.0 = 시장 독립성 높음.

## 기술적 접근

### 신호 생성

4개 독립 팩터를 복합 점수로 결합:

1. **모멘텀** (35% 가중): 추세 추종. 지속적 가격 움직임 포착.
2. **평균 회귀** (25% 가중): 반발. 과매도/과매수 상태 활용.
3. **RSI** (20% 가중): RSI로 과매도/과매수 감지.
4. **가격 위치** (20% 가중): 50일 이동평균 대비 가격 위치.

신호 범위: -1 (강한 매도) ~ +1 (강한 매수).

### 포지션 사이징

**분할 켈리 기준** 사용:

```
f* = (bp - q) / b, 안전을 위해 25% 한도
```

주요 용어:
- b = 평균 승리 / 평균 손실
- p = 과거 승률
- q = 1 - p

포지션은 종목당 10%, 전체 레버리지 150%로 제한.

### 리스크 관리

- **포지션 한도**: 종목당 최대 자본의 10%
- **레버리지 한도**: 총 노출 150%
- **리밸런싱**: 20거래일마다
- **제약**: 집중 회피, 자산군 다각화

### 파라미터 최적화

모멘텀 윈도우(10-30일)와 평균 회귀 윈도우(20-50일)를 스윕해 샤프 지수를 최대화하면서 합리적 수익을 유지하는 설정을 식별한다.

## 이 프로젝트가 보여주는 것

- **시스템 사고**: 원본 데이터에서 검증된 결과까지 완전한 파이프라인
- **통계적 엄격함**: 단순 수익률이 아닌 다양한 성과 지표
- **엔지니어링 역량**: 모듈식, 테스트 가능, 유지보수 용이한 코드
- **리스크 의식**: 낙폭 제어와 하방 보호에 중점
- **검증 습관**: 벤치마크 비교와 파라미터 최적화 내장
- **멀티에셋 역량**: 주식, 암호화폐, 실물자산을 통합 프레임워크로 처리
- **실전 제약 이해**: 레버리지 한도, 리밸런싱 마찰, 거래 비용 인식
- **정량적 사고**: 켈리 기준, 팩터 가중치, 통계 지표

## 기술 스택

Python • pandas • numpy • scipy • matplotlib • yfinance • scikit-learn
