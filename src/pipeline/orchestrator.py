import numpy as np, pandas as pd, yfinance as yf
from typing import Optional, Dict
from config.config import AppConfig, load_config
from pipeline.backtest import simple_backtest, run_walkforward
from core.metrics import compute_metrics
from core.strategies.registry import get_strategy

def _normalize(df: pd.DataFrame)->pd.DataFrame:
    df = df.rename(columns={c:c.lower() for c in df.columns})
    if 'adj close' in df.columns: df = df.rename(columns={'adj close':'adj_close'})
    if not isinstance(df.index, pd.DatetimeIndex): df.index=pd.to_datetime(df.index)
    return df.sort_index()

def _load(cfg: AppConfig)->pd.DataFrame:
    if cfg.data.source=='yfinance':
        df = yf.download(cfg.data.symbol, start=cfg.data.start, end=cfg.data.end, interval=cfg.data.interval, auto_adjust=cfg.data.auto_adjust, progress=False)
    elif cfg.data.source=='csv':
        df = pd.read_csv(cfg.data.csv_path, index_col=0, parse_dates=True)
    else:
        df = pd.read_parquet(cfg.data.parquet_path)
    df = _normalize(df)
    return df[['open','high','low','close','volume']]

def _rsi(s: pd.Series, n:int=14)->pd.Series:
    d=s.diff(); up=d.clip(lower=0); dn=(-d).clip(lower=0)
    rs = up.rolling(n).mean()/(dn.rolling(n).mean()+1e-12)
    return 100 - (100/(1+rs))

def _features(df: pd.DataFrame)->pd.DataFrame:
    f = pd.DataFrame(index=df.index)
    f['ret1']=df['close'].pct_change().fillna(0.0)
    f['sma20']=df['close'].rolling(20).mean()
    f['sma50']=df['close'].rolling(50).mean()
    f['rsi14']=_rsi(df['close'],14)
    try:
        from features.market_regime_detector import regime_flags
        f = f.join(regime_flags(df['close']), how='left')
    except Exception: pass
    try:
        from features.anomaly_detector import anomaly_score
        f['anomaly']=anomaly_score(df['close'])
    except Exception: pass
    return f.fillna(method='ffill').fillna(0.0)

def run_pipeline(strategy_name: str, params: Optional[Dict]=None, cfg: Optional[AppConfig]=None):
    cfg = cfg or load_config()
    df = _load(cfg)
    feats = _features(df)
    strat = get_strategy(strategy_name, params or {})
    sig = strat.generate_signals(df, feats).fillna(0.0)
    if cfg.bt.walkforward_splits>1:
        bt = run_walkforward(df, feats, strat, cfg.fees, n_splits=cfg.bt.walkforward_splits, seed=cfg.bt.seed)
    else:
        bt = simple_backtest(df, sig, cfg.fees)
    stats = compute_metrics(bt['equity'].pct_change().fillna(0.0))
    return df, {'equity': bt['equity'], 'signals': sig, 'stats': stats, 'costs': bt.get('costs')}
