from django.shortcuts import render
from risk.processes.account import *


# Main site for risk management
def risk_main(request):

    """
    Loads the main page of the risk app
    :param request:
    :return:
    """

    return render(request, 'risk_app/risk_main.html')


def get_balance(request):

    account_number = "001-004-2840244-004"
    acces_token = "db81a15dc77b29865aac7878a7cb9270-6cceda947c717f9471b5472cb2c2adbd"

    env = request.GET.get("env_1", "")
    opening_bal = float(request.GET.get("op_bal", ""))
    account = Account(environment=env, acces_token=acces_token, account_number=account_number).get_balance_info()
    print(account)
    return render(request, 'risk_app/risk_main.html', {"env": env,
                                                       "nav": float(account["nav"]),
                                                       "op_bal": opening_bal,
                                                       "lat_bal": float(account["latest_bal"]),
                                              }
                  )
