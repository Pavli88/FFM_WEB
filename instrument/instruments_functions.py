from instrument.models import *


def get_instruments():
    instruments = Instruments.objects.filter().values()
    return instruments