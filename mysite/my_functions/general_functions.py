import datetime
from datetime import datetime
from datetime import date
from datetime import timedelta
import datetime

def get_today():
    return date.today()


def beginning_of_year():
    return date(date.today().year, 1, 1)


def beginning_of_month():
    return date(date.today().year, date.today().month, 1)


def previous_business_day(currenct_day):
    date = datetime.datetime.strptime(currenct_day, '%Y-%m-%d')
    if date.date().weekday() == 0:
        result = date + timedelta(-3)
    elif date.date().weekday() == 6:
        result = date + timedelta(-2)
    else:
        result = date + timedelta(-1)
    return result.date()


def previous_month_end(current_day):
    return current_day.replace(day=1) - datetime.timedelta(days=1)
