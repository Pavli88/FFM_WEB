from django.shortcuts import render, redirect
from risk.processes.account import *
from mysite.processes.oanda import *
from mysite.views import *
from risk.models import *


# Main site for risk management
def risk_main(request):

    """
    Loads the main page of the risk app
    :param request:
    :return:
    """

    print("Loading all accounts from database...")
    print("Loading all robots from database")

    robots = get_robot_list()

    # , {"accounts": get_account_data(),
    #    "robots": robots[:-1]}

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
                                                       "lat_bal": float(account["latest_bal"]), })


def save_account_risk(request):

    """
    Process to updated account level risk parameters
    :param request:
    :return:
    """

    if request.method == "POST":
        account = request.POST.get("account")
        daily_risk_limit = request.POST.get("loss_limit")

        print("Request received to amend account level risk parameters")
        print("Account:", account)
        print("Daily Risk Limit:", daily_risk_limit)

    try:
        print("Updating account level risk parameters for", account)
        account_risk_params = AccountRisk.objects.get(account=account)
        account_risk_params.account = account
        account_risk_params.daily_risk_limit = daily_risk_limit
        account_risk_params.save()
        print("Record has been updated!")
    except:
        print("Risk account record does not exists for this account. Creating first risk record for account")
        account_risk_params = AccountRisk(account=account,
                                          daily_risk_limit=daily_risk_limit)
        account_risk_params.save()
        print("New record has been created")

    return redirect('risk main template')


def save_robot_risk(request):

    print("Request to amend robot risk parameters")

    if request.method == "POST":
        robot = request.POST.get("robot")
        sl_policy = request.POST.get("sl_policy")
        init_exp = request.POST.get("in_exp")
        quantity = request.POST.get("qt")
        p_level = request.POST.get("p_level")
        m_dd = request.POST.get("max_dd")

    print("------------------")
    print("Updated Parameters")
    print("------------------")
    print("Robot:", robot)
    print("SL Policy:", sl_policy)
    print("Initial Exposure:", init_exp)
    print("Quantity:", quantity)
    print("Pyramiding Level:", p_level)
    print("Maximum Drawdown:", m_dd)

    print("Updating robot parameters in database")

    try:
        robot_risk = RobotRisk.objects.get(robot=robot)
        robot_risk.p_level = p_level
        robot_risk.in_exp = init_exp
        robot_risk.sl_policy = sl_policy
        robot_risk.m_dd = m_dd
        robot_risk.quantity = quantity
        robot_risk.save()
        print("Parameters have been updated!")
    except:
        robot_risk = RobotRisk(robot=robot,
                               p_level=p_level,
                               in_exp=init_exp,
                               sl_policy=sl_policy,
                               m_dd=m_dd,
                               quantity=quantity)

        robot_risk.save()
        print("New parameters have been saved!")

    return redirect('risk main template')