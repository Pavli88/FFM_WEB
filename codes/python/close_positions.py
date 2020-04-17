import oandapy
import pandas as pd
import argparse

# Example command line command
# python close_positions.py --ca all

# Arguments
parser = argparse.ArgumentParser()

parser.add_argument("--env", help="Defines the environment. live or practise")
parser.add_argument("--ca", help="Close all trades on the account")

args = parser.parse_args()

# Environment check
if args.env == None:
    account = "101-004-11289420-001"
    environment = "practice"
    acces_token = "ecd553338b9feac1bb350924e61329b7-0d7431f8a1a13bddd6d5880b7e2a3eea"
else:
    account = "001-004-2840244-004"
    environment = "live"
    acces_token = "db81a15dc77b29865aac7878a7cb9270-6cceda947c717f9471b5472cb2c2adbd"

print("-----------------------------------")
print("          TRADE EXECUTION          ")
print("-----------------------------------")
print("Environment:", environment)
# Creating an Oanda object
oanda = oandapy.APIv20(environment=environment, access_token=acces_token)
open_trades = oanda.trades.get_open_trades(account_id=account).as_dict()
open_trades_table = pd.DataFrame.from_dict(open_trades["trades"])
open_trade_id_list = list(open_trades_table["id"])

print("Closing Trades")

if args.ca is not None:
    for id in open_trade_id_list:
        oanda.trades.close_trade(account_id=account, trade_id=id, units="ALL")
        print("Trade:", id)

