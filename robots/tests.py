import requests


# Create your tests here.
r = requests.post("http://127.0.0.1:8000/robots/signals/trade/", "SNP_TEST SELL 4320.4133")

# trade_at_oanda(token="ecd553338b9feac1bb350924e61329b7-0d7431f8a1a13bddd6d5880b7e2a3eea")