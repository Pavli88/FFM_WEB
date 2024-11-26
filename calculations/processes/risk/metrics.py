import pandas as pd
import numpy as np

def correlation_matrix(prices_df):
    returns_df = prices_df.pct_change().dropna()
    correlation_matrix = returns_df.corr()
    return correlation_matrix.fillna(0)


def std_dev_of_returns(prices_df):
    returns_df = prices_df.pct_change().dropna()
    std_dev_returns = returns_df.std()
    return std_dev_returns.to_dict()


def portfolio_std(instrument_df, std_devs, correlation_matrix):
    portfolio_variance = 0
    marginal_risks = {}
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

    # Calculate marginal risk for each instrument
    for i, (id_i, row_i) in enumerate(instrument_df.iterrows()):
        weight_i = row_i['weight']
        name_i = row_i['instrument__name']
        std_dev_i = std_devs[name_i]

        # Marginal risk contribution for security i
        marginal_contribution = 0
        for j, (id_j, row_j) in enumerate(instrument_df.iterrows()):
            weight_j = row_j['weight']
            name_j = row_j['instrument__name']
            std_dev_j = std_devs[name_j]

            # Get correlation between securities i and j
            correlation = correlation_matrix.loc[name_i, name_j]

            # Contribution from security i in relation to security j
            marginal_contribution += weight_j * std_dev_i * std_dev_j * correlation

        # Adjust for the weight of security i
        marginal_risks[name_i] = (2 * weight_i * marginal_contribution) / portfolio_std_dev

    desired_order = correlation_matrix.index.tolist()
    instrument_df['instrument__name'] = pd.Categorical(instrument_df['instrument__name'], categories=desired_order, ordered=True)
    instrument_df_sorted = instrument_df.sort_values('instrument__name').reset_index(drop=True)
    # print(instrument_df_sorted)
    # print("FIRST")
    # print(correlation_matrix)
    # print(instrument_df_sorted['weight'].to_list())
    # print(desired_order)
    # print(marginal_risks)
    # print(portfolio_std_dev)
    return portfolio_std_dev, marginal_risks

def portfolio_risk_calc(correlation_matrix, std_devs, weights):
    asset_names = list(std_devs.keys())
    std_dev_values = np.array(list(std_devs.values()))
    covariance_matrix = np.outer(std_dev_values, std_dev_values) * correlation_matrix

    # Portfolio variance and standard deviation (total risk)
    portfolio_variance = weights.T @ covariance_matrix @ weights
    portfolio_std_dev = np.sqrt(portfolio_variance)

    # Calculate Marginal Risk Contributions (MRC)
    mrcs = (covariance_matrix @ weights) / portfolio_std_dev
    mrcs_dict = [{'label': asset, 'value': mrc} for asset, mrc in zip(asset_names, mrcs)]

    # Calculate individual contributions
    individual_contributions = weights * mrcs
    contrib_dict = [{'label': asset, 'value': cont} for asset, cont in zip(asset_names, individual_contributions)]
    return portfolio_std_dev, mrcs_dict, contrib_dict



