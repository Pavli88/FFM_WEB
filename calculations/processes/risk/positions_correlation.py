import pandas as pd

def correlation_matrix(prices_df):
    returns_df = prices_df.pct_change().dropna()
    correlation_matrix = returns_df.corr()
    return correlation_matrix
