import json
import http.client
import pandas as pd

class CapitalBrokerConnection:
    def __init__(self, ENV, email, api_password, api_key):
        "Establishes connection and Authenticates the user"

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

        if ENV == 'DEMO':
            self.URL = DEMO_URL
        if ENV == 'LIVE':
            self.URL = LIVE_URL

        self.conn = http.client.HTTPSConnection(self.URL)
        self.conn.request("POST", "/api/v1/session", payload, headers)
        res = self.conn.getresponse()
        header_dict = dict(res.getheaders())

        self.cst_token = header_dict.get('CST')
        self.x_security_token = header_dict.get('X-SECURITY-TOKEN')

        data = json.loads(res.read().decode("utf-8"))

        print(pd.DataFrame(data['accounts']))

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
        print(data.decode("utf-8"))

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
        print(data.decode("utf-8"))

    def switch_account(self, account_id):
        payload = json.dumps({
            "accountId": "274430448666751262"
        })
        headers = {
            'X-SECURITY-TOKEN': self.x_security_token,
            'CST': self.cst_token,
            'Content-Type': 'application/json'
        }
        self.conn.request("PUT", "/api/v1/session", payload, headers)
        res = self.conn.getresponse()
        data = res.read()
        print(data.decode("utf-8"))

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

    def create_position(self):
        payload = json.dumps({
            "epic": "SILVER",
            "direction": "BUY",
            "size": 1,
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
        data = res.read()
        print(data.decode("utf-8"))

    def get_single_position(self, deal_id):
        payload = ''
        headers = {
            'X-SECURITY-TOKEN': self.x_security_token,
            'CST': self.cst_token,
        }
        self.conn.request("GET", f"/api/v1/positions/{deal_id}", payload, headers)
        res = self.conn.getresponse()
        data = res.read()
        print(data.decode("utf-8"))

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
        # print(pd.DataFrame(data))

    def get_deal_status(self):
        payload = ''
        headers = {
            'X-SECURITY-TOKEN': self.x_security_token,
            'CST': self.cst_token,
        }
        deal_reference = "p_006011e7-0055-311e-0000-000080cb15d7"
        self.conn.request("GET", f"/api/v1/confirms/{deal_reference}", payload, headers)
        res = self.conn.getresponse()
        data = json.loads(res.read().decode("utf-8"))
        print(pd.DataFrame(data))

    def close_position(self, deal_id):
        payload = ''
        headers = {
            'X-SECURITY-TOKEN': self.x_security_token,
            'CST': self.cst_token,
        }
        self.conn.request("DELETE", f"/api/v1/positions/{deal_id}", payload, headers)
        res = self.conn.getresponse()
        data = res.read()
        print(data.decode("utf-8"))

pd.set_option('display.max_columns', None)    # Show all columns
pd.set_option('display.max_rows', None)       # Show all rows
pd.set_option('display.max_colwidth', None)   # Show full content of each column
pd.set_option('display.expand_frame_repr', False)

EMAIL='pavlicsekati@gmail.com'
API_PASSWORD = 'Tedike88!'
API_KEY = 'b8khxC1bTYBHEXZr'

con = CapitalBrokerConnection(ENV='DEMO', email=EMAIL, api_password=API_PASSWORD, api_key=API_KEY)

# con.close_position(deal_id="006011e7-0055-311e-0000-000080cb1558")
# con.get_single_position(deal_id='006011e7-0055-311e-0000-000080cb158a')

# con.get_deal_status()
con.switch_account(account_id='274430448666751262')
con.get_all_positions()
# con.get_session_details()
# con.create_position()