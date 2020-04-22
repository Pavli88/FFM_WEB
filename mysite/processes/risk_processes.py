import oandapy
import pandas as pd
import argparse


class Account:

    def __init__(self, environment, acces_token, account_number):
        self.account_number = account_number
        self.environment = environment
        self.acces_token = acces_token
        self.oanda = oandapy.APIv20(environment=self.environment, access_token=self.acces_token)

    def get_account(self, display_table=None):

        """
        Gets account data form the appropriate environment.
        :return:
        """

        self.account = self.oanda.account.get_account(account_id=self.account_number).as_dict()

        if display_table is None:
            pass
        else:
            print(pd.DataFrame.from_dict(self.account))

        return self.account

    def get_balance_info(self):
        self.account_data = self.get_account()

        return {"nav": self.account_data["account"]["NAV"]}

# daily_opening_balance = float(a["account"]["balance"])
# nav = float(a["account"]["NAV"])
# unrealized_pnl = float(a["account"]["unrealizedPL"])
# unrealized_return = round(unrealized_pnl/daily_opening_balance, 3)
#
# print("-----------------------------------")
# print("          BALANCE SUMMARY          ")
# print("-----------------------------------")
# print("Environment:", environment)
# print("Opening Balance:", float(args.st_bal))
# print("Daily Risk Ammount:", risk_ammount)
# print("Daily NAV Down Limit:", float(args.st_bal) - risk_ammount)
# print("Current NAV:", nav)
# print("Latest Balance", daily_opening_balance)
# print("")
# print("Return:")
# print("-------")
# print("Realized P&L to Daily Risk Ammount:", round((daily_opening_balance - float(args.st_bal))/risk_ammount, 3))
# print("Realized P&L", daily_opening_balance - float(args.st_bal))
# print("Realized Return", round((daily_opening_balance - float(args.st_bal))/float(args.st_bal), 3))
# print("Unrealized P&L", unrealized_pnl)
# print("Unrealized Return", unrealized_return)
#
# print("Active robots:")

if __name__ == "__main__":

    # Arguments

    parser = argparse.ArgumentParser()

    parser.add_argument("--env", help="Defines the environment. live or practise")
    parser.add_argument("--st_bal", help="Start balance for the trading day.")

    args = parser.parse_args()

    # Environment parameters
    if args.env is None:
        raise Exception("Execution is stopped! Environment was not given!")

    if args.env == "practice":
        account_number = "101-004-11289420-001"
        acces_token = "ecd553338b9feac1bb350924e61329b7-0d7431f8a1a13bddd6d5880b7e2a3eea"
    elif args.env == "live":
        account_number = "001-004-2840244-004"
        acces_token = "db81a15dc77b29865aac7878a7cb9270-6cceda947c717f9471b5472cb2c2adbd"

    daily_risk_limit = 0.05

    # Starting balance
    if args.st_bal is None:
        risk_ammount = 0
    else:
        risk_ammount = float(args.st_bal) * daily_risk_limit

    account = Account(environment=args.env, acces_token=acces_token, account_number=account_number)
    print(account.get_balance_info())

