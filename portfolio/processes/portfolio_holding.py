# Model imports
from portfolio.models import Positions
from instrument.models import Prices
from mysite.models import Exceptions

import pandas as pd
from datetime import datetime
import datetime
from mysite.my_functions.general_functions import get_today


def portfolio_holding_calc(portfolio_code, calc_date):
    print('PORTFOLIO HOLDINGS CALS')
    print(portfolio_code, calc_date)

    positions = pd.DataFrame(Positions.objects.filter(portfolio_name=portfolio_code, date=calc_date).values())
    if len(positions) == 0:
        try:
            existing_exception = Exceptions.objects.get(entity_code=portfolio_code,
                                                        exception_type='No Positions',
                                                        calculation_date=calc_date)
            existing_exception.status = 'Alert'
            existing_exception.save()
        except Exceptions.DoesNotExist:
            Exceptions(exception_level='Portfolio',
                       entity_code=portfolio_code,
                       exception_type='No Positions',
                       process='Portfolio Holding',
                       status='Alert',
                       creation_date=datetime.datetime.now(),
                       calculation_date=calc_date).save()
    price_hierarchy = ['MAP', 'ffm_system', 'oanda'] # 'MAP', 'ffm_system', 'oanda'
    if len(price_hierarchy) == 0:
        try:
            existing_exception = Exceptions.objects.get(entity_code=portfolio_code,
                                                        exception_type='Missing Price Hierarchy',
                                                        calculation_date=calc_date)
            existing_exception.status = 'Error'
            existing_exception.save()
        except Exceptions.DoesNotExist:
            Exceptions(exception_level='Portfolio',
                       entity_code=portfolio_code,
                       exception_type='Missing Price Hierarchy',
                       process='Portfolio Holding',
                       status='Error',
                       creation_date=datetime.datetime.now(),
                       calculation_date=calc_date).save()
    if len(positions) == 0 or len(price_hierarchy) == 0:
        return 'End of process'

    print(positions)
    prices = pd.DataFrame(Prices.objects.filter(date=calc_date, inst_code__in=list(positions['security'])).values())
    print(prices)

    price_list_df = pd.DataFrame()
    for index, row in positions.iterrows():
        price_df = prices[prices['inst_code'] == str(row['security'])]
        for price_source in price_hierarchy:
            price2_df = price_df[price_df['source'] == price_source]
            if len(price2_df) > 0:
                price_list_df = price_list_df.append({'inst_code': list(price2_df['inst_code'])[0],
                                                      'price': list(price2_df['price'])[0]}, ignore_index=True)
                break
            else:
                price_list_df = price_list_df.append({'inst_code': None,
                                                      'price': None}, ignore_index=True)

    print(price_list_df)

    # Check if there is available prices for all of the securites list(dict.fromkeys(list(prices['inst_code'])))
    inst_codes_positions_table = list(positions['security'])
    available_prices = list(price_list_df['inst_code'])
    print(inst_codes_positions_table)
    print(available_prices)
    missing_prices_list = []
    for missing_price in inst_codes_positions_table:
        if str(missing_price) not in available_prices:
            missing_prices_list.append(missing_price)
    print(missing_prices_list)

    # Raising Exceptions for missing prices
    for missing_price in missing_prices_list:
        print(missing_price)
        try:
            existing_exception = Exceptions.objects.get(security_id=missing_price, calculation_date=calc_date)
            existing_exception.status = 'Error'
            existing_exception.save()
            print(existing_exception)
        except Exceptions.DoesNotExist:
            Exceptions(exception_level='Security',
                       entity_code=portfolio_code,
                       exception_type='Missing Price',
                       process='Portfolio Holding',
                       security_id=missing_price,
                       status='Error',
                       creation_date=datetime.datetime.now(),
                       calculation_date=calc_date).save()


    # positions['price'] = price_list_df['price']
    # positions['mv'] = price_list_df['price'] * positions['quantity']
    # print(positions)
    return ""