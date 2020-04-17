import oandapy
import pandas as pd
import argparse

# Example command line command
# python execute.py --st_bal 150 --env live --sec EUR_USD --q 1000 --sl perc

# Arguments
parser = argparse.ArgumentParser()

parser.add_argument("--env", help="Defines the environment. live or practise")
parser.add_argument("--st_bal", help="Start balance for the trading day.")
parser.add_argument("--sec", help="Security to trade")
parser.add_argument("--q", help="Quantity to trade. Either + or -")
parser.add_argument("--sl", help="SL Level. Percentage of account or price level")
parser.add_argument("--slpv", help="SL Percentage Level Value.")
parser.add_argument("--sl_prec", help="SL Level precision to round up")
parser.add_argument("--pl", help="Pyramiding Limit")

args = parser.parse_args()

# Checking SL
if args.sl == None:
    raise Exception("SL is missing! You cannot execute trade !")

# Checking quantity
if args.q == None:
    raise Exception("Quantity is not given!")

# Checking if security was given
if args.sec == None:
    raise Exception("Security is not defined!")

# Environment check
if args.env == "practice":
    account = "101-004-11289420-001"
    environment = "practice"
    acces_token = "ecd553338b9feac1bb350924e61329b7-0d7431f8a1a13bddd6d5880b7e2a3eea"
else:
    account = "001-004-2840244-004"
    environment = "live"
    acces_token = "db81a15dc77b29865aac7878a7cb9270-6cceda947c717f9471b5472cb2c2adbd"

daily_risk_limit = 0.05

#Starting balance
if args.st_bal == None:
    raise Exception("Starting balance was not given! Use starting balance.")
else:
    risk_ammount = float(args.st_bal) * daily_risk_limit

# Creating an Oanda object
oanda = oandapy.APIv20(environment=environment, access_token=acces_token)

a = oanda.account.get_account(account_id=account).as_dict()

# Account balance data
daily_opening_balance = float(a["account"]["balance"])
nav = float(a["account"]["NAV"])
unrealized_pnl = float(a["account"]["unrealizedPL"])
unrealized_return = round(unrealized_pnl/daily_opening_balance, 3)

print("-----------------------------------")
print("          TRADE EXECUTION          ")
print("-----------------------------------")
print("Environment:", environment)
print("Opening Balance:", float(args.st_bal))
print("Daily Risk Ammount:", risk_ammount)
print("Daily NAV Down Limit:", float(args.st_bal) - risk_ammount)
print("Current NAV:", nav)
print("Latest Balance", daily_opening_balance)
print("")
print("Checking if new trade execution is allowed and risk limit was not reached...")

# Checking if trade can be executed based on daily risk limit
if float(args.st_bal) - risk_ammount > daily_opening_balance:
    raise Exception("You have reached your daily risk limit. Trading is not allowed for this day!")
else:
    print("Trade can be executed !")

# Fetching out open positions
print("Fetching out open positions...")

open_trades = oanda.trades.get_open_trades(account_id=account).as_dict()
open_trades_table = pd.DataFrame.from_dict(open_trades["trades"])

try:
    open_trade_id_list = len(list(open_trades_table["id"]))
except:
    open_trade_id_list = 0

print("Number of open trades:", open_trade_id_list)

if args.pl == None:
    pyramiding_limit = 0
else:
    pyramiding_limit = int(args.pl)

print("Pyramiding limit:",pyramiding_limit )

if int(open_trade_id_list) == pyramiding_limit:
    raise Exception("Number of trades breached the pyramiding limit! Trade cannot be executed!")

print("New trade cannot breach pyramiding limit. Trade can be executed!")

# Fetching best bid ask prices
bid_ask = oanda.pricing.get_pricing(account_id=account, instruments=[args.sec]).as_dict()
bids = pd.DataFrame.from_dict(bid_ask["prices"][0]["bids"])
asks = pd.DataFrame.from_dict(bid_ask["prices"][0]["asks"])

print("")
print("ASK:", list(asks["price"])[0])
print("BID", list(bids["price"])[-1])

print("")

# Calculating SL
if args.sl == "perc":

    if args.slpv == None:
        sl_perc = float(input("Add the percentage of risk per trade on account (Example: 0.03):"))
    else:
        sl_perc = float(args.slpv)

    if sl_perc >= daily_risk_limit:
        raise Exception("Execution is stopped! You cannot execute trades with risk larger then the daily risk limit!")
    else:
        sl_risk_ammount = daily_opening_balance*sl_perc
        print("SL Risk Ammount:", daily_opening_balance*sl_perc)

        if float(args.q) > 0:
            sl_level = float(list(asks["price"])[-1]) - (sl_risk_ammount / abs(float(args.q)))
        else:
            sl_level = float(list(bids["price"])[-1]) + (sl_risk_ammount / abs(float(args.q)))
else:
    sl_level = float(args.sl)

    if float(args.q) > 0:

        if float(list(asks["price"])[0]) < sl_level:
            raise Exception("BUY trade! SL is larger than market price !")
        sl_risk_ammount = (float(list(asks["price"])[0])*float(args.q)) - (sl_level*float(args.q))
    else:
        if float(list(bids["price"])[0]) > sl_level:
            raise Exception("SELL trade! SL is smaller than market price !")
        sl_risk_ammount = ((sl_level*float(args.q)) - (float(list(bids["price"])[0])*float(args.q))) * -1

    if sl_risk_ammount > risk_ammount:
        raise Exception("Position size and risk is larger than the daily total risk ammount ! Execution stopped !")

    print("SL Risk Ammount:", sl_risk_ammount)

if float(args.q) > 0:
    print("BUY", float(args.q), r"@", float(list(asks["price"])[0]), "SL", sl_level)
    print("Trade Market Value:", float(list(asks["price"])[0])*float(args.q))
else:
    print("SELL", float(args.q), r"@", float(list(bids["price"])[-1]), "SL", sl_level)
    print("Trade Market Value:", float(list(bids["price"])[-1])*float(args.q))

# Creating Order
print("")
print("Executing order in", environment, "environment")

if args.sl_prec is None:
    prec = 4
else:
    prec = int(args.sl_prec)

order = {"instrument": str(args.sec),
         "units": str(args.q),
         "type": "MARKET",
         "stopLossOnFill": {"price": str(round(sl_level, prec))}
         }
order_submint = oanda.orders.create_order(account_id=account, order=order)
print("Order was executed")