import datetime
from datetime import datetime
from datetime import date


def get_today():
    return date.today()


def beginning_of_year():
    return date(date.today().year, 1, 1)


def beginning_of_month():
    return date(date.today().year, date.today().month, 1)
