# quantitative-trading-engine

A daily-bar research backtester with rule-based signals, share/cash accounting, benchmark comparison and parameter sweeps. It does not submit broker orders or claim verified market outperformance.

## 설치와 실행

Git, Python 3.10 이상과 Yahoo Finance 연결이 필요합니다.

macOS / Linux:

```bash
git clone https://github.com/yokioryonghee/quantitative-trading-engine.git
cd quantitative-trading-engine
python3 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/python examples/run_backtest.py
.venv/bin/python examples/comprehensive_analysis.py
.venv/bin/python examples/visualize_comprehensive.py
```

Windows PowerShell:

```powershell
git clone https://github.com/yokioryonghee/quantitative-trading-engine.git
cd quantitative-trading-engine
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\python.exe examples/run_backtest.py
.\.venv\Scripts\python.exe examples/comprehensive_analysis.py
.\.venv\Scripts\python.exe examples/visualize_comprehensive.py
```

이미 내려받았다면 프로젝트 폴더에서 `git pull origin main`으로 갱신하고 가상환경 Python으로 설치·실행합니다. 차트는 `backtest_comprehensive_analysis.png`에 저장됩니다. GUI가 없는 환경은 `MPLBACKEND=Agg`를 지정합니다.

## 계산 방식

- yfinance 조정 일봉을 읽고 미래 가격을 과거로 역채움하지 않습니다. 미국 주식/ETF, 암호화폐, 상품, 한국 종목을 예제로 사용합니다.
- 한국 OHLC 가격은 관측된 USD/KRW 자료로 USD 환산합니다. FX가 없거나 잘못되면 해당 계산을 중단합니다.
- 모멘텀, 평균 회귀, RSI, 이동평균 대비 가격을 고정 가중치로 조합합니다. 학습하는 ML 모델이나 실시간 feed는 없습니다.
- 투자 비중은 과거 신호와 이후 수익에서 얻은 payoff를 이용하는 제한된 Kelly식 휴리스틱입니다. 최적 비중을 입증하지 않습니다.
- 20개 관측마다 완료 종가로 목표 비중을 계산합니다. `build_engine`은 이후 거래 가능한 관측 시가에서 주문을 실행합니다. 개별 `run_backtest`에 시가를 전달하지 않으면 이후 관측 종가 체결을 사용합니다.
- 주식 수량과 현금을 추적합니다. 재조정 사이에는 수량을 유지하므로 실제 비중이 가격에 따라 변합니다. 목표 종목 비중 상한은 10%, 목표 gross exposure 상한은 기본 150%입니다. 연속적인 실시간 비중 보장은 아닙니다.
- 거래량이 0인 날은 매매하지 않습니다. 기본 편도 비용 10bp와 연 3% 차입 가정을 반영합니다. 비용은 실제 중개사 수수료가 아닌 연구 설정입니다.
- 종료 시 보유 자산을 마지막 종가로 평가합니다. 가상의 최종 청산은 하지 않습니다. `trade_ledger`, `realized_weights`, `execution`을 결과에 포함합니다.
- 파라미터 스윕은 같은 수량 회계와 실행 가격을 사용합니다. 순위는 in-sample 결과이며 독립 미래 성능 검증이 아닙니다.

## 모듈

| 파일 | 역할 |
|---|---|
| data_loader.py | 다운로드 정규화, 관측 가격 정렬, FX 환산 |
| indicators.py | 과거 일봉 특징과 규칙 신호 |
| risk.py | 신호 payoff 기반 크기 휴리스틱과 목표 노출 제한 |
| accounting.py | 다음 관측 체결, 수량·현금·비용·차입 회계 |
| backtest.py | 주기적 목표 생성과 성과 집계 |
| benchmark.py | 공통 날짜 benchmark 비교와 파라미터 스윕 |
| engine.py | 전체 실행 연결 |

`build_engine`에서 종목·기간·자본·노출 상한을 지정합니다. `config.yaml`은 예전 예제이며 현재 실행기가 읽지 않습니다.

## 테스트

```bash
.venv/bin/python -m pip install -e ".[test]"
.venv/bin/python -m pytest -q
```

Windows는 `.\.venv\Scripts\python.exe`로 바꿉니다. GitHub Actions는 pandas 2와 3에서 데이터 형식, 인과성, 가격 정렬, 수량 유지, 비용, 거래 가능일, FX와 네 개 예제 실행/PNG 생성을 검사합니다. 실제 시세 대신 mock 응답을 사용합니다.

## 해석 범위

서로 다른 시장의 일봉 종가·시가가 실제로 동시에 형성되는 것은 아닙니다. FX 일봉 환산과 달력별 노출은 일별 근사 모델이며 동시각 intraday USD 체결을 재현하지 않습니다. Sharpe 등은 252-period 가정이어서 혼합 달력 해석에 주의가 필요합니다.

현재 종목 목록은 과거 시점의 생존 편향 없는 유니버스가 아닙니다. 실제 수익성, 주문/체결, 시장 충격, 차입 가능 수량, 계좌 동기화와 운영 안정성은 별도 검증해야 합니다.
