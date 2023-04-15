from instrument.models import *


def get_instruments():
    instruments = Instruments.objects.filter().values()
    return instruments


def get_securities(broker=None):
    if broker is None:
        securities = Instruments.objects.filter().values()
    else:
        securities = Instruments.objects.filter(source=broker).values()

    return securities