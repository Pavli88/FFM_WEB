from portfolio.models import *


def get_portfolios(port=None, port_type=None):
    """
    Retrieves all portfolio records from database
    :return:
    """
    if port is not None:
        return Portfolio.objects.filter(portfolio_name=port).values()
    elif port_type is not None:
        return Portfolio.objects.filter(portfolio_type=port_type).values()


