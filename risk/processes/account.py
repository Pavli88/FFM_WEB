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

        return {"nav": self.account_data["account"]["NAV"],
                "latest_bal": float(self.account_data["account"]["balance"])}