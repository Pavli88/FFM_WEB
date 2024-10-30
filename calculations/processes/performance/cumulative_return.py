import numpy as np

def calculate_cumulative_returns(returns):
    daily_returns = np.array(returns)
    cumulative_returns = (1 + daily_returns).cumprod() - 1
    return cumulative_returns