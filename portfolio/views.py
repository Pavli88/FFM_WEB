from django.shortcuts import render, redirect
from django.db import connection
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Model imports
from portfolio.models import *
from mysite.models import *
from instrument.models import *

from datetime import datetime
import datetime
import json
import pandas as pd

# Process imports
from mysite.my_functions.general_functions import *

# CRUD------------------------------------------------------------------------------------------------------------------

# READ
def get_portfolio_data(request, portfolio):
    if request.method == "GET":
        if portfolio == 'all':
            portfolio_data = Portfolio.objects.filter().values()
        else:
            portfolio_data = Portfolio.objects.filter(portfolio_code=portfolio).values()
        response = list(portfolio_data)
        return JsonResponse(response, safe=False)


def get_port_transactions(request, portfolio):
    if request.method == "GET":
        cursor = connection.cursor()
        cursor.execute("""select pt.id, pt.portfolio_code, pt.quantity, pt.price, 
        pt.mv, pt.date, inst.instrument_name, inst.instrument_type, inst.source , inst.currency, pt.transaction_type
        from portfolio_trade as pt, 
        instrument_instruments as inst 
        where pt.security=inst.id and pt.portfolio_code='{port_name}';""".format(port_name=portfolio))
        row = cursor.fetchall()
        print(row)
        return JsonResponse(row, safe=False)


def get_cash_flow(request):
    if request.method == "GET":
        portfolio = request.GET.get('portfolio')
        start_date= request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        cash_flow_data = CashFlow.objects.filter(portfolio_code=portfolio).values()
        response = {'amount': [record['amount'] for record in cash_flow_data],
                    'type': [record['type'] for record in cash_flow_data]}
        return JsonResponse(response, safe=False)


def get_cash_holdings(request):
    if request.method == "GET":
        portfolio = request.GET.get('portfolio')
        date = request.GET.get('date')
        cash_holding_data = CashHolding.objects.filter(portfolio_code=portfolio).values()

        return JsonResponse(list(cash_holding_data), safe=False)


def get_positions(request):
    print("PORTFOLIO POSITIONS REQUEST")

    if request.method == "GET":
        portfolio = request.GET.get('portfolio')
        date = request.GET.get('date')
        positions = Positions.objects.filter(portfolio_name=portfolio).filter(date=date).values()
        print("PORTFOLIO:", portfolio)
        print("DATE:", date)
        print(positions)

        return JsonResponse(list({}), safe=False)


def get_portfolio_nav(request, portfolio_code):
    if request.method == "GET":
        start_date = request.GET.get('start_date')
        portfolio_nav = Nav.objects.filter(portfolio_code=portfolio_code).filter(date__gte=start_date).values()
        return JsonResponse(list(portfolio_nav), safe=False)


# Portfolio Group Related Processes-------------------------------------------------------------------------------------
@csrf_exempt
def add_port_to_group(request):
    print("*** PORTFOLIO GROUP ADDITION ***")
    if request.method == "POST":
        parent_id = request.POST.get("process")
        children_id = request.POST.get("process")
        try:
            PortGroup(parent_id=parent_id, children_id=children_id, connection_id=str(parent_id)+str(children_id)).save()
        except:
            response = {"message": "Connection exists in database!"}
    return JsonResponse(response, safe=False)


# Portfolio Import stream related processes
@csrf_exempt
def portfolio_import_stream(request, import_stream):
    if request.method == "POST":
        body_data = json.loads(request.body.decode('utf-8'))
        data_stream = body_data["data"]
        df = pd.DataFrame(data_stream)
        print(df)
        if import_stream=='NAV':
            for index, row in df.iterrows():
                portfolio_nav = Nav.objects.filter(portfolio_code=row['portfolio_code']).filter(date=row['date']).values()
                if len(portfolio_nav) == 0:
                    new_nav_record = Nav(portfolio_name=row['portfolio_name'],
                                         accured_expenses=row['accured_expenses'],
                                         date=row['date'],
                                         accured_income=row['accured_income'],
                                         cash_val=row['cash_val'],
                                         long_liab=row['long_liab'],
                                         nav_per_share=row['nav_per_share'],
                                         pos_val=row['pos_val'],
                                         short_liab=row['short_liab'],
                                         total=row['total'],
                                         portfolio_code=row['portfolio_code'])
                    new_nav_record.save()
                elif len(portfolio_nav) > 0:
                    p = Nav.objects.get(id=portfolio_nav[0]['id'])
                    p.portfolio_name = row['portfolio_name']
                    p.accured_expenses = row['accured_expenses']
                    p.date = row['date']
                    p.accured_income = row['accured_income']
                    p.cash_val = row['cash_val']
                    p.long_liab = row['long_liab']
                    p.nav_per_share = row['nav_per_share']
                    p.pos_val = row['pos_val']
                    p.short_liab = row['short_liab']
                    p.total = row['total']
                    p.portfolio_code = row['portfolio_code']
                    p.save()
        response = {"message": "Connection exists in database!"}
        return JsonResponse(response, safe=False)




