from django.shortcuts import render, redirect
from django.db import connection
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Model imports
from portfolio.models import *
from robots.models import *
from mysite.models import *
from instrument.models import *

from datetime import datetime
import datetime
import json
import pandas as pd

# Process imports
from mysite.my_functions.general_functions import *
from portfolio.portfolio_functions import *
from portfolio.processes.port_pos import *
from portfolio.processes.cash_holding import *
from portfolio.processes.processes import *
from robots.processes.robot_balance_calc import *
from portfolio.processes.portfolio_holding import portfolio_holding_calc


# CRUD------------------------------------------------------------------------------------------------------------------
@csrf_exempt
def create_portfolio(request):
    if request.method == "POST":
        body_data = json.loads(request.body.decode('utf-8'))
        port_name = body_data["port_name"]
        port_type = body_data["port_type"]
        port_currency = body_data["port_currency"]
        port_code = body_data["port_code"]
        inception_date = body_data["inception_date"]
        try:
            Portfolio(portfolio_name=port_name,
                      portfolio_code=port_code,
                      portfolio_type=port_type,
                      currency=port_currency,
                      status="Not Funded",
                      inception_date=inception_date).save()
            response = "New Portfolio is created!"
        except:
            response = "Portfolio exists in database!"
    return JsonResponse(response, safe=False)


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
    print("Portfolio transactions")
    if request.method == "GET":
        cursor = connection.cursor()
        cursor.execute("""select pt.id, pt.portfolio_name, pt.quantity, pt.price, 
        pt.mv, pt.date, inst.instrument_name, inst.instrument_type, inst.source 
        from portfolio_trade as pt, 
        instrument_instruments as inst 
        where pt.security=inst.id and pt.portfolio_name='{port_name}';""".format(port_name=portfolio))
        row = cursor.fetchall()
        print(portfolio)
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


# Portfolio related processes-------------------------------------------------------------------------------------------
@csrf_exempt
def new_transaction(request):
    if request.method == "POST":
        body_data = json.loads(request.body.decode('utf-8'))
        quantity = body_data["unit"]
        price = body_data["price"]
        portfolio = body_data["portfolio"]
        security = body_data["sec"]
        security_type = body_data["sec_type"]
        security_id = body_data["sec_id"]
        market_value = float(quantity) * float(price)
        cash_flow = market_value * -1

        if security_type == "Robot":
            source = "ffm_system"
        else:
            source = "oanda"

        print("QUANTITY:", quantity)
        print("PRICE:", price)
        print("PORTFOLIO:", portfolio)
        print("SECURITY:", security)
        print("SECURITY TYPE:", security_type)
        print("SECURITY ID:", security_id)
        print("MARKET VALUE:", market_value)
        print("CASH FLOW:", cash_flow)
        print("SOURCE:", source)

        Trade(portfolio_name=portfolio,
              quantity=quantity,
              price=price,
              mv=market_value,
              sec_type=security_type,
              security=security_id,
              source=source).save()

        print("Saving new trade record to", portfolio)
        print("Updating robot and portfolio cash flow tables")
        print('Adding cash flow record to', portfolio)
        CashFlow(portfolio_code=portfolio,
                 amount=market_value * -1,
                 type="TRADE",
                 currency="USD").save()
        if security_type == "Robot":
            print("Adding cash flow record to", security)
            print("ROBOT CASH FLOW:", market_value)
            RobotCashFlow(robot_name=security,
                          cash_flow=market_value).save()
            print("New cash flow was recorded for", security)
            print("Calculating robot balance")
            balance_calc_message = balance_calc(robot=security, calc_date=get_today())
            print(balance_calc_message)
            print("Sending message to system messages table")
            SystemMessages(msg_type="Cash Flow",
                           msg=str(cash_flow * -1) + "cash flow to " + str(security)).save()

        # print('Portfolio positions calculation')
        # portfolio_positions(portfolio=portfolio, calc_date=get_today())

        # print('Portfolio cash holdings calculation')
        # cash_holding(portfolio=portfolio, calc_date=get_today())

        response = 'Portfolio trade was executed successfully!'

        return JsonResponse(response, safe=False)


@csrf_exempt
def pos_calc(request):
    if request.method == "POST":
        print("")
        print("PORTFOLIO POSITIONS CALCULATION")
        body_data = json.loads(request.body.decode('utf-8'))
        date = datetime.datetime.strptime(body_data['start_date'], '%Y-%m-%d').date()
        end_date = datetime.datetime.strptime(body_data['end_date'], '%Y-%m-%d').date()
        portfolio = body_data['portfolio']

        print("Parameters: ", "START DATE:", date, "END DATE:", end_date, "PORTFOLIO:", portfolio)

        if portfolio == "ALL":
            portfolio_list = Portfolio.objects.filter().values_list('portfolio_code', flat=True)
        else:
            portfolio_list = [portfolio]
        response_list = []
        for port in portfolio_list:
            port_data = Portfolio.objects.filter(portfolio_code=port).values()
            inception_date = port_data[0]['inception_date']
            start_date = date
            responses = []
            while start_date <= end_date:
                if inception_date > start_date:
                    responses.append({'date': start_date.strftime('%Y-%m-%d'),
                                      'msgs': [{'msg': 'Calculation date is less than inception date.'}]})
                else:
                    responses.append({'date': start_date.strftime('%Y-%m-%d'),
                                      'msgs': portfolio_positions(portfolio=port, calc_date=start_date)})
                start_date = start_date + timedelta(days=1)
            response_list.append({'portfolio': port, 'response': responses})
        return JsonResponse(response_list, safe=False)


@csrf_exempt
def cash_calc(request):
    print("")
    print("CASH HOLDING CALCULATION")
    body_data = json.loads(request.body.decode('utf-8'))
    date = datetime.datetime.strptime(body_data['start_date'], '%Y-%m-%d').date()
    end_date = datetime.datetime.strptime(body_data['end_date'], '%Y-%m-%d').date()
    portfolio = body_data['portfolio']

    print("Parameters: ", "START DATE:", date, "END DATE:", end_date, "PORTFOLIO:", portfolio)

    if portfolio == "ALL":
        portfolio_list = Portfolio.objects.filter().values_list('portfolio_code', flat=True)
    else:
        portfolio_list = [portfolio]

    response_list = []

    for port in portfolio_list:
        print(">>> PORTFOLIO:", port)
        port_data = Portfolio.objects.filter(portfolio_code=port).values()
        inception_date = port_data[0]['inception_date']
        start_date = date
        responses = []
        while start_date <= end_date:
            if inception_date > start_date:
                print("    DATE:", start_date, )
                responses.append({'date': start_date.strftime('%Y-%m-%d'),
                                  'msg': 'Calculation date is less than inception date.'})
            else:
                print("    DATE:", start_date)
                responses.append({'date': start_date.strftime('%Y-%m-%d'),
                                  'msg': cash_holding(portfolio=port, calc_date=start_date)})
            start_date = start_date + timedelta(days=1)
        response_list.append({'portfolio': port, 'response': responses})
    return JsonResponse(response_list, safe=False)


@csrf_exempt
def holdings_calc(request):
    if request.method == "POST":
        print("")
        print("PORTFOLIO HOLDINGS CALCULATION")
        body_data = json.loads(request.body.decode('utf-8'))
        date = datetime.datetime.strptime(body_data['start_date'], '%Y-%m-%d').date()
        end_date = datetime.datetime.strptime(body_data['end_date'], '%Y-%m-%d').date()
        portfolio = body_data['portfolio']
        print("Parameters: ", "START DATE:", date, "END DATE:", end_date, "PORTFOLIO:", portfolio)
        if portfolio == "ALL":
            portfolio_list = Portfolio.objects.filter().values_list('portfolio_code', flat=True)
        else:
            portfolio_list = [portfolio]
        for port in portfolio_list:
            port_data = Portfolio.objects.filter(portfolio_code=port).values()
            inception_date = port_data[0]['inception_date']
            start_date = date
            while start_date <= end_date:
                if inception_date > start_date:
                    print("    DATE:", start_date,
                          ' - Calculation date is less than inception date. Calculation is not possible.')
                else:
                    print("    DATE:", start_date)
                    portfolio_holding_calc(portfolio=port, calc_date=start_date)
                start_date = start_date + timedelta(days=1)
        response = "Calc ended"
        return JsonResponse(response, safe=False)


@csrf_exempt
def new_cash_flow(request):
    print("*** PORTFOLIO NEW CASH FLOW ***")

    if request.method == "POST":
        body_data = json.loads(request.body.decode('utf-8'))
        portfolio_name = body_data["port_name"]
        amount = body_data["amount"]
        type = body_data["type"]
        currency = body_data["currency"]

        print("PORTFOLIO NAME:", portfolio_name, "TYPE:", type, "AMOUNT:", amount)

        CashFlow(portfolio_code=portfolio_name,
                 amount=amount,
                 type=type,
                 currency=currency).save()

        print("New cashflow was created!")

        if type == "FUNDING":
            port = Portfolio.objects.get(portfolio_name=portfolio_name)
            port.status = "Funded"
            port.save()
            print("")

        response = "Transaction was recorded successfully!"

    return JsonResponse(response, safe=False)


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




