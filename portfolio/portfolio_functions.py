from portfolio.models import *


def get_portfolios(port=None, port_type=None):

    """
    Retrieves portfolio records from database
    :return:
    """

    if port is not None:
        return Portfolio.objects.filter(portfolio_name=port).values()
    elif port_type is not None:
        return Portfolio.objects.filter(portfolio_type=port_type).values()
    elif port is None and port_type is None:
        return Portfolio.objects.filter().values()


