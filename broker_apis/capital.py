import json
import http.client
import pandas as pd

class CapitalBrokerConnection:
    def __init__(self, ENV, email, api_password, api_key, account_number):
        pd.set_option('display.max_columns', None)  # Show all columns
        pd.set_option('display.max_rows', None)  # Show all rows
        pd.set_option('display.max_colwidth', None)  # Show full content of each column
        pd.set_option('display.expand_frame_repr', False)

        "Establishes connection and Authenticates the user"
        self.account_number = account_number
        LIVE_URL = 'api-capital.backend-capital.com/'
        DEMO_URL = 'demo-api-capital.backend-capital.com'

        payload = json.dumps({
            "identifier": email,
            "password": api_password,
        })

        headers = {
            'X-CAP-API-KEY': api_key,
            'Content-Type': 'application/json'
        }

        if ENV == 'Demo':
            self.URL = DEMO_URL
        if ENV == 'Live':
            self.URL = LIVE_URL

        self.conn = http.client.HTTPSConnection(self.URL)
        self.conn.request("POST", "/api/v1/session", payload, headers)
        res = self.conn.getresponse()
        header_dict = dict(res.getheaders())

        self.cst_token = header_dict.get('CST')
        self.x_security_token = header_dict.get('X-SECURITY-TOKEN')

        self.data = json.loads(res.read().decode("utf-8"))

    @classmethod
    def from_credentials(cls, credentials, account):
        return cls(
            email=credentials.email,
            api_password=credentials.password,
            api_key=credentials.api_token,
            account_number=account.account_number,
            ENV=credentials.environment
        )

    def get_accounts(self):
        return self.data['accounts']

    def get_session_details(self):
        """Get session details."""
        payload = ''
        headers = {
            'X-SECURITY-TOKEN': self.x_security_token,
            'CST': self.cst_token,
        }
        self.conn.request("GET", "/api/v1/session", payload, headers)
        res = self.conn.getresponse()
        data = res.read()


    def close_session(self):
        """Close session."""
        payload = ''
        headers = {
            'X-SECURITY-TOKEN': self.x_security_token,
            'CST': self.cst_token,
        }
        self.conn.request("DELETE", "/api/v1/session", payload, headers)
        res = self.conn.getresponse()
        data = res.read()


    def switch_account(self):
        payload = json.dumps({
            "accountId": self.account_number,
        })
        headers = {
            'X-SECURITY-TOKEN': self.x_security_token,
            'CST': self.cst_token,
            'Content-Type': 'application/json'
        }
        self.conn.request("PUT", "/api/v1/session", payload, headers)
        res = self.conn.getresponse()
        data = res.read()


    def get_single_market(self):
        """Get market details by EPIC (instrument code)."""
        payload = ''
        headers = {
            'X-SECURITY-TOKEN': self.x_security_token,
            'CST': self.cst_token,
        }
        self.conn.request("GET", "/api/v1/markets/SILVER", payload, headers)
        res = self.conn.getresponse()
        data = res.read()
        print(data.decode("utf-8"))

    def create_position(self, security, quantity):

        if quantity < 0:
            direction = 'SELL'
        if quantity > 0:
            direction = 'BUY'

        payload = json.dumps({
            "epic": security,
            "direction": direction,
            "size": abs(quantity),
            # "guaranteedStop": True,
            # "stopLevel": 20,
            # "profitLevel": 27
        })
        headers = {
            'X-SECURITY-TOKEN': self.x_security_token,
            'CST': self.cst_token,
            'Content-Type': 'application/json'
        }
        self.conn.request("POST", "/api/v1/positions", payload, headers)
        res = self.conn.getresponse()
        return json.loads(res.read().decode("utf-8"))

    def submit_market_order(self, security, quantity, sl_price=None):
        self.switch_account()
        response = self.create_position(security=security, quantity=quantity)

        if 'errorCode' in response:
            return {'broker_id': '-', 'status': 'failed', 'trade_price': 0, 'fx_rate': 0, 'reason': f"An error occurred during trade execution ({response['errorCode']})"}

        deal = self.get_deal_status(deal_reference=response['dealReference'])

        if deal['dealStatus'] == 'ACCEPTED':
            deal_id = deal['affectedDeals'][0]['dealId']
            return {'broker_id': deal_id, 'status': 'accepted', 'trade_price': deal['level'], 'fx_rate': 1}

        if deal['dealStatus'] == 'REJECTED':
            deal_id = deal['dealId']
            return {'broker_id': deal_id, 'status': 'rejected', 'trade_price': deal['level'], 'fx_rate': 0, 'reason': deal['rejectReason']}

    def get_single_position(self, deal_id):
        payload = ''
        headers = {
            'X-SECURITY-TOKEN': self.x_security_token,
            'CST': self.cst_token,
        }
        self.conn.request("GET", f"/api/v1/positions/{deal_id}", payload, headers)
        res = self.conn.getresponse()
        data = res.read()
        # print(data.decode("utf-8"))

    def get_all_positions(self):
        "Returns all open positions."

        payload = ''
        headers = {
            'X-SECURITY-TOKEN': self.x_security_token,
            'CST': self.cst_token,
        }
        self.conn.request("GET", "/api/v1/positions", payload, headers)
        res = self.conn.getresponse()
        data = json.loads(res.read().decode("utf-8"))
        for x in data['positions']:
            print(x['position'])


    def get_deal_status(self, deal_reference):
        payload = ''
        headers = {
            'X-SECURITY-TOKEN': self.x_security_token,
            'CST': self.cst_token,
        }
        self.conn.request("GET", f"/api/v1/confirms/{deal_reference}", payload, headers)
        res = self.conn.getresponse()
        data = json.loads(res.read().decode("utf-8"))
        return data

    def close_trade(self, trd_id):
        payload = ''
        headers = {
            'X-SECURITY-TOKEN': self.x_security_token,
            'CST': self.cst_token,
        }
        self.conn.request("DELETE", f"/api/v1/positions/{trd_id}", payload, headers)
        res = self.conn.getresponse()
        response = json.loads(res.read().decode("utf-8"))

        if 'errorCode' in response:
            return {'broker_id': '-', 'status': 'failed', 'trade_price': 0, 'fx_rate': 0, 'reason': f"Trade is not open at the broker ({trd_id})"}

        deal = self.get_deal_status(deal_reference=response['dealReference'])

        return {
            'broker_id': deal['affectedDeals'][0]['dealId'],
            'units': deal['size'],
            'price': deal['level'],
            'fx_rate': 1,
            'status': 'accepted'
        }


# #
# EMAIL='pavlicsekati@gmail.com'
# API_PASSWORD = 'Tedike88!'
# # API_KEY = 'b8khxC1bTYBHEXZr'
# API_KEY = 'RdRB8p3umXqcAFyP'
# con = CapitalBrokerConnection(
#     ENV='Demo',
#     email=EMAIL,
#     api_password=API_PASSWORD,
#     api_key=API_KEY,
#     account_number='274430448666751262'
# )
# a = con.get_accounts()

# con.close_position(deal_id="006011e7-0055-311e-0000-000080cb1558")


# con.get_deal_status()
# con.switch_account()
# con.get_all_positions()
# con.get_session_details()
# con.create_position()
# con.submit_market_order(security='EURGBP', quantity=1000000000)
# con.get_deal_status()
# con.get_single_position(deal_id='00005552-001c-241e-0000-0000806d330a')
