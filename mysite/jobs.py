import requests
from datetime import date

print("ROBOT DAILY BALANCE CALCULATION JOB")
print("DATE:", date.today())
r = requests.post("http://pavliati.pythonanywhere.com/robots/calculate_robot_balance/", json={'robot': 'ALL', 'start_date': str(date.today()), 'end_date': str(date.today())})
print("Robot balance calculation finished!")

print("PORTFOLIO POSITIONS")
# r = requests.post("http://127.0.0.1:8000/robots/calculate_robot_balance/", json={'robot': 'WTI_USD_TRD1', 'start_date': str(date.today()), 'end_date': str(date.today())})
