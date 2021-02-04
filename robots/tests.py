from django.test import TestCase
import requests

# Create your tests here.
r = requests.post("http://127.0.0.1:8000/robots/signals/trade/", "testdd BUY 1796.1")

# r = requests.get("http://127.0.0.1:8000/robots/add_scheduler/")
# r = requests.get("http://127.0.0.1:8000/robots/add_job/")
