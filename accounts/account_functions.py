from accounts.models import *
from mysite.my_functions.general_functions import *


def get_brokers():
    return BrokerAccounts.objects.filter().values()


def get_account_info(account_number):
    return BrokerAccounts.objects.filter(account_number=account_number).values()


def get_accounts(broker=None, environment=None):
    if broker is None:
        return BrokerAccounts.objects.filter().values()
    else:
        return BrokerAccounts.objects.filter(broker_name=broker, env=environment).values()


def get_account_balance_history(account, start_date, end_date):
    query = "select date, sum(b.close_balance) " \
            "from robots_balance b, robots_robots r " \
            "where r.name=b.robot_name " \
            "and r.account_number='"+ str(account) +"' and date >='"+\
            str(start_date)+"' and date<='"+str(end_date)+"' group by date;"

    account_history = []

    for acc_data in database_query(query):
        account_history.append({"date": acc_data[0], "value": acc_data[1]})

    return account_history