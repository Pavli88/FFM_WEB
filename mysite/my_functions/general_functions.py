import datetime
from datetime import datetime
from datetime import date
from django.db import connection


def get_today():
    return date.today()


def beginning_of_year():
    return date(date.today().year, 1, 1)


def beginning_of_month():
    return date(date.today().year, date.today().month, 1)


def database_query(query):
    cursor = connection.cursor()
    cursor.execute(query)

    return cursor.fetchall()