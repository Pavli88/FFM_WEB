from datetime import datetime, timedelta
import pandas as pd
from portfolio.models import Holding
from instrument.models import Prices
from calculations.processes.risk.metrics import correlation_matrix, std_dev_of_returns, portfolio_risk_calc
import math

def clean_risk_list(risk_list):
    return [
        {
            "label": item["label"],
            "value": item["value"] if isinstance(item["value"], (int, float)) and not math.isnan(item["value"]) else 0.0
        }
        for item in risk_list
    ]

def exposure_metrics(portfolio_code, pricing_period, end_date):
    start_date = end_date - timedelta(days=pricing_period)

    holdings_qs = Holding.objects.filter(portfolio_code__in=portfolio_code, date=end_date).select_related('instrument')
    portfolio_holding = pd.DataFrame(holdings_qs.values(
        'instrument__name', 'mv', 'bv', 'instrument__group', 'instrument_id'
    ))

    if portfolio_holding.empty:
        return {
            "date": end_date.strftime("%Y-%m-%d"),
            "data": {
                "correlation": {},
                "exposures": [],
                "port_std": 0,
                "lev_exp": 0,
                "leverage": 0,
                "risk_structure": [],
                "risk_contribs": []
            }
        }

    portfolio_holding['weight'] = portfolio_holding['mv'] / portfolio_holding['bv'].abs().sum()
    portfolio_holding['pos_lev'] = portfolio_holding['mv'] / portfolio_holding['bv'].sum()
    leverage = portfolio_holding['mv'].abs().sum() / portfolio_holding['bv'].sum()

    portfolio_holding = portfolio_holding[portfolio_holding['instrument__group'] != 'Cash']
    portfolio_holding = portfolio_holding.groupby(['instrument_id', 'instrument__name'])['weight'].sum().reset_index()

    securities = portfolio_holding['instrument_id'].tolist()
    prices_qs = Prices.objects.filter(instrument_id__in=securities, date__range=(start_date, end_date)).select_related('instrument')
    prices_df = pd.DataFrame(prices_qs.values('instrument_id', 'price', 'instrument__name', 'date'))

    if prices_df.empty:
        return {
            "date": end_date.strftime("%Y-%m-%d"),
            "data": {
                "correlation": {},
                "exposures": portfolio_holding.to_dict('records'),
                "port_std": 0,
                "lev_exp": portfolio_holding['weight'].sum(),
                "leverage": leverage,
                "risk_structure": [],
                "risk_contribs": []
            }
        }

    # Build correlation matrix
    price_series = prices_df.groupby('instrument__name')['price'].apply(list).to_dict()
    price_matrix = pd.DataFrame(price_series)
    std_devs = std_dev_of_returns(price_matrix)
    corr_matrix = correlation_matrix(price_matrix)
    corr_dict = corr_matrix.to_dict()

    # Ensure ordering of weights matches correlation matrix
    ordered_names = corr_matrix.columns.tolist()
    portfolio_holding['instrument__name'] = pd.Categorical(
        portfolio_holding['instrument__name'], categories=ordered_names, ordered=True
    )
    sorted_weights_df = portfolio_holding.sort_values('instrument__name').reset_index(drop=True)

    port_std, mrcs, risk_contribs = portfolio_risk_calc(
        correlation_matrix=corr_matrix,
        std_devs=std_devs,
        weights=sorted_weights_df['weight'].to_numpy()
    )

    return {
        "date": end_date.strftime("%Y-%m-%d"),
        "data": {
            "correlation": corr_dict,
            "exposures": sorted_weights_df.rename(columns={'weight': 'weight'}).to_dict('records'),
            "port_std": round(port_std, 4),
            "lev_exp": round(sorted_weights_df['weight'].sum(), 4),
            "leverage": round(leverage, 2),
            "risk_structure": clean_risk_list(mrcs),
            "risk_contribs": clean_risk_list(risk_contribs),
        }
    }
