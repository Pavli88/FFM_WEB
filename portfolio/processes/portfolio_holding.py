# Model imports
from portfolio.models import Positions
from instrument.models import Prices

import pandas as pd


def portfolio_holding_calc(portfolio_code, calc_date):
    print('PORTFOLIO HOLDINGS CALS')
    print(portfolio_code, calc_date)

    positions = pd.DataFrame(Positions.objects.filter(portfolio_name=portfolio_code, date=calc_date).values())
    price_hierarchy = ['oanda', 'MAP', 'ffm_system']
    print(positions)
    prices = pd.DataFrame(Prices.objects.filter(date=calc_date, inst_code__in=list(positions['security'])).values())
    print(prices)

    # Check if there is available prices for all of the securites
    inst_codes_positions_table = list(positions['security'])
    inst_codes_price_table = list(dict.fromkeys(list(prices['inst_code'])))
    print(inst_codes_positions_table)
    print(inst_codes_price_table)
    missing_securities_list = []
    for security_code in inst_codes_positions_table:
        if str(security_code) not in inst_codes_price_table:
            missing_securities_list.append(security_code)

    print(missing_securities_list)
    if len(missing_securities_list) > 0:
        print('Missing securities')
        return 'Missing securities'

    price_list_df = pd.DataFrame()

    for index, row in positions.iterrows():
        price_df = prices[prices['inst_code'] == str(row['security'])]
        for price_source in price_hierarchy:
            price2_df = price_df[price_df['source'] == price_source]
            if len(price2_df) > 0:
                price_list_df = price_list_df.append({'inst_code': list(price2_df['inst_code'])[0],
                                                      'price': list(price2_df['price'])[0]}, ignore_index=True)
                break

    print(price_list_df)
    positions['price'] = price_list_df['price']
    positions['mv'] = price_list_df['price'] * positions['quantity']
    print(positions)
    return ""