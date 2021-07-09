import requests

# Create your tests here.
# r = requests.post("http://127.0.0.1:8000/portfolios/create/new_cash_flow/", {"port_name": "SSS", "amount": 100, "type": "Portfolio"})
# r = requests.post("http://127.0.0.1:8000/portfolios/create/", {"port_name": "SSS", "amount": 100, "type": "Portfolio"})

r = requests.post("http://127.0.0.1:8000/portfolios/positions", json={"portfolio": "ALL", "start_date": '2021-07-01', "end_date": '2021-07-07'})