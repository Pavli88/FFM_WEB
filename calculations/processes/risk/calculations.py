from datetime import datetime, timedelta
import pandas as pd
from portfolio.models import Holding
from instrument.models import Prices
from calculations.processes.risk.metrics import correlation_matrix, std_dev_of_returns, portfolio_std


def exposure_metrics(portfolio_code, pricing_period, end_date):
    start_date = end_date - timedelta(days=pricing_period)

    portfolio_holding = pd.DataFrame(
        Holding.objects.filter(portfolio_code__in=portfolio_code, date=end_date).select_related('instrument')
        .values('instrument__name', 'mv', 'bv', 'instrument__group', 'instrument_id')
    )
    if portfolio_holding.empty:
        return {"date": end_date.date(),
                "data": {
                    "correlation": {},
                    "exposures": [],
                    "port_std": 0,
                    "lev_exp": 0,
                    "risk_structure": []
                }}

    portfolio_holding['weight'] = portfolio_holding['mv'] / portfolio_holding['bv'].sum()
    portfolio_holding = portfolio_holding[portfolio_holding['instrument__group'] != 'Cash']
    portfolio_holding = portfolio_holding.groupby(['instrument_id', 'instrument__name'])['weight'].sum().reset_index()
    # portfolio_holding['weight2'] = portfolio_holding['weight'].abs() / portfolio_holding['weight'].abs().sum()
    securities_list = portfolio_holding['instrument_id'].tolist()
    # print(portfolio_holding)
    # Fetch price data within date range for relevant securities
    prices_df = pd.DataFrame(
        Prices.objects.filter(instrument_id__in=securities_list, date__range=(start_date, end_date))
        .select_related('instrument')
        .values('instrument_id', 'price', 'instrument__name', 'date')
    )

    if prices_df.empty:
        return {"date": end_date.date(),
                "data": {
                    "correlation": {},
                    "exposures": [],
                    "port_std": 0,
                    "lev_exp": 0,
                    "risk_structure": []
                }}

    # Prepare data for correlation matrix calculation
    data = prices_df.groupby('instrument__name')['price'].apply(list).to_dict()
    prices_matrix = pd.DataFrame(data)

    std_devs = std_dev_of_returns(prices_matrix)

    # Calculate correlation matrix
    corr_matrix = correlation_matrix(prices_matrix)
    corr_dict = corr_matrix.to_dict()

    port_std, marginal_risks = portfolio_std(portfolio_holding, std_devs, corr_matrix)
    risk_contribs = [{"label": key, "value": float(value)} for key, value in marginal_risks.items()]
    # print(corr_matrix)
    # print(portfolio_holding)
    # print(std_devs)

    return {"date": end_date.date(),
            "data": {
                "correlation": corr_dict,
                "exposures": portfolio_holding.to_dict('records'),
                "port_std": port_std,
                "lev_exp": portfolio_holding['weight'].sum(),
                "risk_structure": risk_contribs
            }}