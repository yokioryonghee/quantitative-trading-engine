"""Share/cash accounting with explicit next-open or next-close execution."""
import numpy as np
import pandas as pd

def simulate(prices,targets,volume,capital,open_prices=None,cost_bps=10.,borrow_rate=.03,cash_rate=0.,rebalance_freq=20):
    if not np.isfinite([capital,cost_bps,borrow_rate,cash_rate]).all() or capital<=0 or not 0<=cost_bps<10000 or min(borrow_rate,cash_rate)<0:
        raise ValueError('Invalid accounting settings')
    if not targets.index.equals(prices.index) or not targets.columns.equals(prices.columns) or not np.isfinite(targets.to_numpy()).all():
        raise ValueError("Finite aligned targets required")
    execution=prices if open_prices is None else open_prices.reindex_like(prices)
    if execution.isna().any().any() or not np.isfinite(execution.to_numpy()).all() or (execution<=0).any().any():
        raise ValueError('Execution prices must be finite positive and aligned')
    tradable=volume.reindex_like(prices).fillna(0).gt(0)
    shares=np.zeros(prices.shape[1]); cash=float(capital); values=[]; ledger=[]; weights=[]
    pending=np.zeros(prices.shape[1]); need=np.zeros(prices.shape[1],dtype=bool)
    previous_target=np.zeros(prices.shape[1]); previous_value=float(capital)
    fee=cost_bps/10000
    for i,date in enumerate(prices.index):
        current_target=targets.iloc[i].to_numpy(dtype=float)
        # Orders derive only from a completed earlier close.
        if i:
            last_target=targets.iloc[i-1].to_numpy(dtype=float)
            changed=np.full(prices.shape[1],(i-1)%rebalance_freq==0,dtype=bool)
            pending[changed]=last_target[changed]; need|=changed; previous_target=last_target.copy()
            days=(date-prices.index[i-1]).total_seconds()/86400 if isinstance(prices.index,pd.DatetimeIndex) else 1.
            financing=(max(-cash,0.)+np.sum(np.maximum(-shares*prices.iloc[i-1].to_numpy(),0.)))*borrow_rate*days/365.25
            interest=max(cash,0.)*cash_rate*days/365.25
            cash+=interest-financing
        px=execution.iloc[i].to_numpy(dtype=float)
        before=cash+np.dot(shares,px)
        if before<=0: raise ValueError('Portfolio exhausted before execution')
        active=need & tradable.iloc[i].to_numpy()
        if active.any():
            # Solve post-fee equity so target allocations include their own fees.
            old_notional=shares[active]*px[active]
            low,high=0.,before
            for _ in range(60):
                equity=(low+high)/2
                residual=equity+fee*np.abs(pending[active]*equity-old_notional).sum()-before
                if residual>0: high=equity
                else: low=equity
            after=(low+high)/2
            desired=pending[active]*after/px[active]
            delta=desired-shares[active]
            costs=np.abs(delta*px[active])*fee
            cash-=np.sum(delta*px[active])+costs.sum()
            for column,change,cost in zip(np.flatnonzero(active),delta,costs):
                if abs(change)>1e-12:
                    ledger.append(dict(date=date,symbol=prices.columns[column],shares=float(change),price=float(px[column]),cost=float(cost)))
            shares[active]=desired; need[active]=False
        closing=prices.iloc[i].to_numpy(dtype=float)
        value=cash+np.dot(shares,closing)
        if not np.isfinite(value) or value<=0: raise ValueError('Portfolio exhausted after marking')
        values.append(value); weights.append(shares*closing/value)
        previous_value=value
    # Marked NAV; holdings remain open at the final close. No fictitious liquidation.
    cumulative=pd.Series(values,index=prices.index)
    returns=cumulative.pct_change(fill_method=None).fillna(cumulative.iloc[0]/capital-1)
    return cumulative,returns,pd.DataFrame(weights,index=prices.index,columns=prices.columns),ledger
