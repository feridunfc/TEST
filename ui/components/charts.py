import pandas as pd
import plotly.graph_objects as go
def equity_curve_chart(equity: pd.Series, title: str = "Equity Curve"):
    fig = go.Figure()
    if equity is not None and len(equity)>0:
        fig.add_trace(go.Scatter(x=equity.index, y=equity.values, mode="lines", name="Equity"))
    fig.update_layout(title=title, height=420)
    return fig
def drawdown_chart(equity: pd.Series, title: str = "Drawdown"):
    fig = go.Figure()
    if equity is not None and len(equity)>0:
        dd = equity / equity.cummax() - 1.0
        fig.add_trace(go.Bar(x=dd.index, y=dd.values, name="Drawdown"))
    fig.update_layout(title=title, height=300)
    return fig
