
import pandas as pd

def calculate_correlation_matrix(symbol_returns: pd.DataFrame) -> pd.DataFrame:
    return symbol_returns.corr()

def cluster_exposure(positions: dict, corr: pd.DataFrame, threshold: float = 0.7) -> list:
    symbols = list(corr.columns)
    visited = set()
    clusters = []
    for s in symbols:
        if s in visited: 
            continue
        cluster = {s}
        visited.add(s)
        for t in symbols:
            if t not in visited and (corr.loc[s,t] > threshold or corr.loc[t,s] > threshold):
                cluster.add(t)
                visited.add(t)
        clusters.append(sorted(cluster))
    out = []
    for cluster in clusters:
        exp = sum(positions.get(sym, 0.0) for sym in cluster)
        out.append({"cluster": cluster, "exposure": exp})
    return out
