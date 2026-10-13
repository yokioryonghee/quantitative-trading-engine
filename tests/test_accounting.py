import numpy as np
import pandas as pd
import pytest
from quant_engine.accounting import simulate
from quant_engine.data_loader import convert_to_usd

def test_shares_drift_without_hidden_rebalances():
    dates=pd.bdate_range('2024-01-01',periods=4)
    prices=pd.DataFrame({'A':[100,100,200,300]},index=dates)
    targets=pd.DataFrame({'A':[.5,.5,.5,.5]},index=dates)
    values,returns,weights,ledger=simulate(prices,targets,prices*0+1,1000,cost_bps=0,borrow_rate=0,rebalance_freq=20)
    assert list(values)==[1000,1000,1500,2000]
    assert len(ledger)==1
    assert weights.iloc[-1,0]==.75

def test_open_execution_includes_fees():
    dates=pd.bdate_range('2024-01-01',periods=3)
    closes=pd.DataFrame({'A':[100,110,120]},index=dates)
    opens=pd.DataFrame({'A':[100,105,115]},index=dates)
    targets=pd.DataFrame({'A':[1.,1.,1.]},index=dates)
    values,_,_,ledger=simulate(closes,targets,closes*0+1,1000,opens,cost_bps=100,borrow_rate=0)
    assert ledger[0]['price']==105
    assert values.iloc[-1]==pytest.approx(1000/1.01*120/105)

def test_nontrading_day_defers_order():
    dates=pd.date_range('2024-01-01',periods=4)
    prices=pd.DataFrame({'A':100.},index=dates); targets=prices*0+.5; volume=prices*0+1
    volume.iloc[1]=0
    _,_,_,ledger=simulate(prices,targets,volume,1000,cost_bps=0,borrow_rate=0)
    assert ledger[0]['date']==dates[2]

def test_fx_conversion(monkeypatch):
    dates=pd.bdate_range('2024-01-01',periods=3)
    import quant_engine.data_loader as loader
    fx=pd.DataFrame({'Open':1000.,'High':1000.,'Low':1000.,'Close':1000.,'Volume':1},index=dates-pd.Timedelta(days=1))
    monkeypatch.setattr(loader.yf,'download',lambda *a,**k:fx)
    raw=pd.DataFrame({'Date':dates,'Symbol':'005930.KS','Open':10000.,'High':10000.,'Low':10000.,'Close':10000.,'Volume':1})
    assert convert_to_usd(raw).Close.eq(10).all()
