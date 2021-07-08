
def quantity_calc(balance, risk_per_trade, stop_loss, trade_side, trade_price):

    """
    Function to calculate quantity for trade execution based on stop loss level and currenct robot balance data.
    :param balance:
    :param risk_per_trade:
    :param stop_loss:
    :param trade_side:
    :param trade_price:
    :return:
    """

    print(" Balance -", balance, "- Risk per Trade -",
          risk_per_trade, "- Stop Loss -", stop_loss,
          "- Trade Side -", trade_side, "- Trade Price -", trade_price)

    risk_amount = balance * risk_per_trade
    price_sl_dist = float(trade_price)-float(stop_loss)
    quantity = int(risk_amount/price_sl_dist)

    print(" Risk Amount -", risk_amount)
    print(" Price and Stop Distance -", price_sl_dist)
    print(" Quantity -", quantity)

    return quantity