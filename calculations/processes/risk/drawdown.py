import numpy as np

def calculate_drawdowns(return_series):
    cumulative_returns = (1 + np.array(return_series)).cumprod()
    peak = np.maximum.accumulate(cumulative_returns)
    drawdowns = ((peak - cumulative_returns) / peak)* -1
    max_drawdown = np.max(drawdowns)  # Maximum drawdown
    return {'drawdowns': drawdowns.tolist(), 'max_drawdown': float(max_drawdown)}
