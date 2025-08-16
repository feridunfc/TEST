import numpy as np, pandas as pd

def _ann_factor(freq='D'): return 252.0 if freq.upper().startswith('D') else 52.0

def sharpe(r: pd.Series, rf=0.0, freq='D'):
    r = np.asarray(r, float); 
    if r.size==0: return 0.0
    ex = r - rf/_ann_factor(freq); mu = np.nanmean(ex); sd=float(np.nanstd(ex, ddof=1) or 0.0)
    return 0.0 if sd==0 else float(np.sqrt(_ann_factor(freq))*mu/sd)

def sortino(r: pd.Series, rf=0.0, freq='D'):
    r = np.asarray(r, float); ex = r - rf/_ann_factor(freq)
    dn = ex[ex<0]; sd=float(np.nanstd(dn, ddof=1) or 0.0)
    return 0.0 if sd==0 else float(np.sqrt(_ann_factor(freq))*np.nanmean(ex)/sd)

def max_drawdown(eq: pd.Series):
    eq = np.asarray(eq, float); 
    if eq.size==0: return 0.0
    peak = np.maximum.accumulate(eq); dd = (eq-peak)/(peak+1e-12); return float(np.nanmin(dd))

def annualized_return(r: pd.Series, freq='D'):
    r = np.asarray(r, float); 
    if r.size==0: return 0.0
    g = np.nanprod(1+r); n=len(r); af=_ann_factor(freq); 
    return 0.0 if n==0 else float(g**(af/n)-1)

def calmar(r: pd.Series, eq: pd.Series, freq='D'):
    ar = annualized_return(r, freq); mdd = abs(max_drawdown(eq)); return 0.0 if mdd==0 else float(ar/mdd)

def compute_metrics(r: pd.Series, freq='D'):
    eq = (1+r.fillna(0)).cumprod()
    return {'ann_return': annualized_return(r,freq),'sharpe':sharpe(r,freq=freq),'sortino':sortino(r,freq=freq),'max_dd':max_drawdown(eq),'calmar':calmar(r,eq,freq=freq)}
