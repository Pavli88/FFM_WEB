from accounts.models import *


def get_brokers():
    return BrokerAccounts.objects.filter().values()


def get_accounts(broker=None, environment=None):
    if broker is None:
        return BrokerAccounts.objects.filter().values()
    else:
        return BrokerAccounts.objects.filter(broker_name=broker, env=environment).values()
