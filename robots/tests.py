import requests


# Create your tests here.
r = requests.post("http://127.0.0.1:8000/signals/trade/", "SNP_TEST Close 4335.45")

# r = requests.post("https://pavliati.pythonanywhere.com/signals/trade/", "WHEAT_USD_TRD1 Close 6.145")

# trade_at_oanda(token="ecd553338b9feac1bb350924e61329b7-0d7431f8a1a13bddd6d5880b7e2a3eea")