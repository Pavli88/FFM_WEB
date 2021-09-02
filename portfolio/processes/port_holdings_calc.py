import os
import time
import requests
import argparse
import pandas as pd
import datetime
import numpy as np
from datetime import timedelta

# Arguments
parser = argparse.ArgumentParser()
parser.add_argument("--portfolio", help="Portfolio where holding data is calculated")
parser.add_argument("--date", help="Portfolio where holding data is calculated")

args = parser.parse_args()


def portfolio_holdings_calc():
    portfolio = args.portfolio
    calc_date = args.date

    print("----------------------------")
    print("PORTFOLIO HOLDING CALCULATOR")
    print("----------------------------")
    print("PORTFOLIO:", portfolio)
    print("CALC DATE:", calc_date)

    # Fetching portfolios settings for calculations

    # Fetching positions
    print("Fetching positions data from database")
    print("Sending request to server")
    positions_request = requests.get(url="http://127.0.0.1:8000/portfolios/get_positions", params={'portfolio' : portfolio,
                                                                                                   'date' : calc_date})
    print("")
    while True:
        print("test")
        time.sleep(1)
    # Fetching prices for positions

    # Saving down holdings to holdings table

    return ""


if __name__ == "__main__":
    portfolio_holdings_calc()