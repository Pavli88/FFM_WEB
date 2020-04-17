import oandapy
import pandas as pd
import argparse

# Arguments

parser = argparse.ArgumentParser()

parser.add_argument("--env", help="Defines the environment. live or practise")
parser.add_argument("--st_bal", help="Start balance for the trading day.")

args = parser.parse_args()

if args.env == None:
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
    risk_ammount = 0
else:
    risk_ammount = float(args.st_bal) * daily_risk_limit

oanda = oandapy.APIv20(environment=environment, access_token=acces_token)

a = oanda.account.get_account(account_id=account).as_dict()

daily_opening_balance = float(a["account"]["balance"])
nav = float(a["account"]["NAV"])
unrealized_pnl = float(a["account"]["unrealizedPL"])
unrealized_return = round(unrealized_pnl/daily_opening_balance, 3)

print("-----------------------------------")
print("          BALANCE SUMMARY          ")
print("-----------------------------------")
print("Environment:", environment)
print("Opening Balance:", float(args.st_bal))
print("Daily Risk Ammount:", risk_ammount)
print("Daily NAV Down Limit:", float(args.st_bal) - risk_ammount)
print("Current NAV:", nav)
print("Latest Balance", daily_opening_balance)
print("")
print("Return:")
print("-------")
print("Realized P&L to Daily Risk Ammount:", round((daily_opening_balance - float(args.st_bal))/risk_ammount, 3))
print("Realized P&L", daily_opening_balance - float(args.st_bal))
print("Realized Return", round((daily_opening_balance - float(args.st_bal))/float(args.st_bal), 3))
print("Unrealized P&L", unrealized_pnl)
print("Unrealized Return", unrealized_return)