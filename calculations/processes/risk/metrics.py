import pandas as pd
import numpy as np

def correlation_matrix(prices_df):
    returns_df = prices_df.pct_change().dropna()
    correlation_matrix = returns_df.corr()
    return correlation_matrix


def std_dev_of_returns(prices_df):
    returns_df = prices_df.pct_change().dropna()
    std_dev_returns = returns_df.std()
    return std_dev_returns.to_dict()


def portfolio_std(instrument_df, std_devs, correlation_matrix):

    print('PORT STD')
    # Initialize variables
    portfolio_variance = 0
    contributions = {}

    # Iterate over each pair of securities to calculate portfolio variance
    for i, (id_i, row_i) in enumerate(instrument_df.iterrows()):
        weight_i = row_i['weight']
        name_i = row_i['instrument__name']
        std_dev_i = std_devs[name_i]

        for j, (id_j, row_j) in enumerate(instrument_df.iterrows()):
            weight_j = row_j['weight']
            name_j = row_j['instrument__name']
            std_dev_j = std_devs[name_j]

            # Get correlation between securities i and j
            correlation = correlation_matrix.loc[name_i, name_j]

            # Contribution to the portfolio variance from i-j pair
            portfolio_variance += (weight_i * weight_j * std_dev_i * std_dev_j * correlation)

    # Portfolio standard deviation is the square root of portfolio variance
    portfolio_std_dev = np.sqrt(portfolio_variance)

    # Calculate individual contributions to total standard deviation
    for _, row in instrument_df.iterrows():
        name = row['instrument__name']
        weight = row['weight']
        std_dev = std_devs[name]

        # Contribution to the total standard deviation for this security
        contribution = (weight * std_dev / portfolio_std_dev) * 100
        contributions[name] = contribution
    print(portfolio_std_dev)
    print(contributions)
    return portfolio_std_dev, contributions

