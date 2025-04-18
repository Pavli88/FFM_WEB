import json
import numpy as np
import pandas as pd
from django.db import connection
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
from portfolio.models import Portfolio, Transaction, Holding, Nav, TradeRoutes, PortGroup, TotalReturn
from calculations.processes.risk.drawdown import calculate_drawdowns
from calculations.processes.risk.calculations import exposure_metrics
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_portfolios(request):
    print(request.user)
    filters = {key: value for key, value in request.GET.items() if value}
    filters['user'] = request.user
    try:
        portfolios = Portfolio.objects.select_related('user').filter(**filters).values()
        portfolios_list = list(portfolios)
        return JsonResponse(portfolios_list, safe=False, status=200)

    except Exception as e:
        # Handle errors, such as invalid filters
        return JsonResponse({"error": str(e)}, status=400)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_portfolio_transactions(request):
    if request.method == "POST":
        request_body = json.loads(request.body.decode('utf-8'))

        filters = {}
        for key, value in request_body.items():
            if isinstance(value, list):
                print('MULTIPLE')
                if len(value) > 0:
                    filters[key + '__in'] = value
            else:
                print('GROUP')
                filters[key] = value

        results = Transaction.objects.select_related('security').all().filter(**filters) ##.values()

        l = []
        for transaction in results:
            l.append({
                'id': transaction.id,
                'transaction_link_code': transaction.transaction_link_code,
                'name': transaction.security.name,
                'security_id': transaction.security_id,
                'portfolio_code': transaction.portfolio_code,
                'portfolio_id': transaction.portfolio_id,
                'transaction_type': transaction.transaction_type,
                'currency': transaction.currency,
                'open_status': transaction.open_status,
                'is_active': transaction.is_active,
                'quantity': transaction.quantity,
                'price': transaction.price,
                'fx_rate': transaction.fx_rate,
                'mv': transaction.mv,
                'local_mv': transaction.local_mv,
                'net_cashflow': transaction.net_cashflow,
                'local_cashflow': transaction.local_cashflow,
                'margin_balance': transaction.margin_balance,
                'margin_rate': transaction.margin_rate,
                'account_id': transaction.account_id,
                'broker_id': transaction.broker_id,
                'broker': transaction.broker,
                'trade_date': transaction.trade_date,
                'settlement_date': transaction.settlement_date,
                'bv': transaction.bv,
                'local_bv': transaction.local_bv
            })
        return JsonResponse(l, safe=False)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_open_transactions(request):
    # Fetch portfolio IDs for the authenticated user
    portfolio_ids = Portfolio.objects.filter(
        user=request.user, portfolio_type="Portfolio"
    ).values_list('id', flat=True)

    # Fetch active transactions with related security and broker data
    transactions = Transaction.objects.select_related('security').filter(
        is_active=True,
        portfolio_id__in=portfolio_ids,
        broker_id__isnull=False
    )

    # Serialize the transactions
    transaction_data = [
        {
            'id': txn.id,
            'portfolio_code': txn.portfolio_code,
            'name': txn.security.name if txn.security else None,
            'security_id': txn.security_id,
            'sec_group': txn.security.group if txn.security else None,
            'currency': txn.currency,
            'transaction_type': txn.transaction_type,
            'quantity': txn.quantity,
            'price': txn.price,
            'mv': txn.mv,
            'account_id': txn.account_id,
            'broker_id': txn.broker_id,
            'broker': txn.broker,
            'trade_date': txn.trade_date,
            "margin_balance": txn.margin_balance
        }
        for txn in transactions
    ]

    return JsonResponse(transaction_data, safe=False)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_nav(request):
    if request.method == "POST":
        try:
            request_body = json.loads(request.body.decode('utf-8'))
            print(request_body)
            filters = {key: value for key, value in request_body.items()}

            # Fetch data from the database
            navs = pd.DataFrame(Nav.objects.filter(**filters).values())

            if navs.empty:
                return JsonResponse({"message": "No data found"}, status=404)

            # Group data by date
            grouped_data = navs.groupby('date').apply(lambda x: x.to_dict(orient='records')).to_dict()

            # Convert to list of dictionaries
            result = [{"date": date, "records": records} for date, records in grouped_data.items()]

            return JsonResponse(result, safe=False)  # Ensure response is JSON

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


def transactions_pnls(request):
    if request.method == "GET":
        transactions = Transaction.objects.filter(portfolio_code=request.GET.get("portfolio_code"),
                                                  transaction_link_code__gt=0,
                                                  is_active=0).values()
        return JsonResponse(list(transactions), safe=False)


@csrf_exempt
def get_holding(request):
    if request.method == "POST":
        request_body = json.loads(request.body.decode('utf-8'))
        date = request_body['date']
        portfolio_codes = request_body['portfolio_code']
        holdings = Holding.objects.select_related('instrument').filter(date=date).filter(portfolio_code__in=portfolio_codes)

        holdings_list = [
            {
                'portfolio_code': holding.portfolio_code,
                'date': holding.date,
                'trd_id': holding.trd_id,
                'inv_num': holding.inv_num,
                'trade_date': holding.trade_date,
                'trade_type': holding.trade_type,
                'instrument_id': holding.instrument_id,
                'name': holding.instrument.name,
                'group': holding.instrument.group,
                'type': holding.instrument.type,
                'currency': holding.instrument.currency,
                'beg_quantity': holding.beg_quantity,
                'quantity': holding.quantity,
                'trade_price': round(holding.trade_price, 4),
                'beg_market_price': holding.beg_market_price,
                'market_price': round(holding.market_price, 4),
                'fx_rate': round(holding.fx_rate,  4),
                'mv': holding.mv,
                'beg_bv': holding.beg_bv,
                'bv': holding.bv,
                'weight': holding.weight,
                'pos_lev': holding.pos_lev,
                'ugl': holding.ugl,
                'rgl': holding.rgl,
                'price_pnl': holding.price_pnl,
                'trd_pnl': holding.trd_pnl,
                'total_pnl': holding.total_pnl,
            }
            for holding in holdings
        ]
        response_df = pd.DataFrame(holdings_list).fillna(0)
        print(response_df)
        response_df['net_weight'] = response_df['mv'] / response_df['mv'].sum()
        response_df['gross_weight'] = response_df['mv'] / response_df['mv'].abs().sum()
        response_df['abs_weight'] = response_df['mv'].abs() / response_df['mv'].abs().sum()
        return JsonResponse(response_df.to_dict('records'), safe=False)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_exposures(request):
    if request.method == "GET":
        try:
            # responses = calculate_holdings(portfolio_code=request.GET.get("portfolio_code"), calc_date=request.GET.get("date"))
            # print(responses)
            stress_percentage = float(request.GET.get("stress_percentage")) / 100
            holding_df = pd.read_json(Holding.objects.get(date=request.GET.get("date"), portfolio_code=request.GET.get("portfolio_code")).data)
            nav = Nav.objects.filter(portfolio_code=request.GET.get("portfolio_code"), date=request.GET.get("date")).values()[0]['total']
            holding_df['contribution'] = (holding_df['unrealized_pnl'] / nav) * 100
            holding_df['ticked'] = False
            holding_df['sim_price'] = np.where(holding_df['transaction_type'] == 'Purchase', holding_df['valuation_price'] * (1 - stress_percentage), holding_df['valuation_price'] * (1 + stress_percentage))
            holding_df['sim_profit'] = np.where(holding_df['transaction_type'] == 'Purchase', (holding_df['sim_price'] - holding_df['trade_price']) * holding_df['ending_pos'] * holding_df['fx_rate'], (holding_df['trade_price'] - holding_df['sim_price']) * holding_df['ending_pos'] * holding_df['fx_rate'])
            holding_df['sim_contr'] = (holding_df['sim_profit'] / nav) * 100
            holding_df['sim_contr_amended'] = (holding_df['sim_profit'] / nav) * 100
            holding_df['sensitivity'] = abs(holding_df['sim_contr']) - abs(holding_df['contribution'])
            holding_df = holding_df[(holding_df['ending_mv'] > 0.0) & (holding_df['instrument_name'] != 'Cash')].round(
                {'ending_mv': 1,
                 'base_leverage': 1,
                 'unrealized_pnl': 2,
                 'fx_rate': 2,
                 'trade_price': 4,
                 'valuation_price': 4,
                 'contribution': 2,
                 'sim_contr': 2,
                 'sim_profit': 2,
                 'sim_price': 2,
                 'sensitivity': 2,
                 'sim_contr_amended': 2
                 })
            total_sim_profit = holding_df['sim_profit'].sum()
            sim_nav = round(nav + total_sim_profit, 2)
            sim_drawdown = round((nav - sim_nav) / nav, 3) * -100

            return JsonResponse({
                'data': holding_df.to_dict('records'),
                'nav': round(nav, 2),
                'sim_nav': sim_nav,
                'sim_dd': round(sim_drawdown, 2)
            }, safe=False)
        except Holding.DoesNotExist:
            return JsonResponse({'data': [], 'nav': 0.0}, safe=False)

def get_drawdown(request):
    if request.method == "GET":
        total_returns = pd.DataFrame(TotalReturn.objects.filter(portfolio_code=request.GET.get("portfolio_code"), period='dtd').order_by('end_date').values())
        drawdown_records = calculate_drawdowns(return_series=total_returns['total_return'])
        return JsonResponse(drawdown_records, safe=False)

@csrf_exempt
def get_total_returns(request):
    if request.method == "POST":
        request_body = json.loads(request.body.decode('utf-8'))
        filters = {}
        for key, value in request_body.items():
            filters[key] = value

        total_returns = TotalReturn.objects.filter(**filters).order_by('end_date').values()
        return JsonResponse(list(total_returns), safe=False)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_trade_routes(request):
    if request.method == "GET":
        cursor = connection.cursor()
        cursor.execute("""
        select pt.id,
       pt.is_active,
       pt.quantity,
       pt.broker_account_id,
       pt.inst_id,
       instrument_instruments.name,
       source_ticker, source,
       broker_name,
       account_number from portfolio_traderoutes as pt
inner join instrument_instruments on pt.inst_id = instrument_instruments.id
inner join instrument_tickers on pt.ticker_id = instrument_tickers.id
inner join accounts_brokeraccounts on pt.broker_account_id = accounts_brokeraccounts.id
where pt.portfolio_code = '{portfolio_code}';
        """.format(portfolio_code=request.GET.get("portfolio_code")))

        row = cursor.fetchall()
        df = pd.DataFrame(row, columns=[col[0] for col in cursor.description])

        return JsonResponse(df.to_dict('records'), safe=False)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_port_groups(request):
    # Get the logged-in user
    owner = request.user

    # Filter PortGroup where the related Portfolio's owner is the logged-in user
    port_groups = PortGroup.objects.select_related('portfolio').filter(portfolio__user=owner)

    # Format response
    g = [
        {
            'id': group.id,
            'name': group.portfolio.portfolio_name,
            'parent_id': group.parent_id,
            'portfolio_code': group.portfolio.portfolio_code,
            'portfolio_type': group.portfolio.portfolio_type,
            'currency': group.portfolio.currency,
        }
        for group in port_groups
    ]

    return JsonResponse(g, safe=False, status=200)


@csrf_exempt
def get_position_exposures(request):
    try:
        request_body = json.loads(request.body.decode('utf-8'))
        portfolio_code = request_body["portfolio_code"]
        period = int(request_body["period"]) + 2
        end_date = request_body["date"]
        sample_period = int(request_body["sample_period"])
        start_date = datetime.strptime(end_date, "%Y-%m-%d") - timedelta(days=sample_period)

        exp_list = []

        while start_date <= datetime.strptime(end_date, "%Y-%m-%d"):
            # print(start_date)

            if start_date.weekday() == 5 or start_date.weekday() == 6:
                pass
            else:
                exp_metrics = exposure_metrics(portfolio_code=portfolio_code, end_date=start_date, pricing_period=period)
                exp_list.append(exp_metrics)
            start_date += timedelta(days=1)

        return JsonResponse(exp_list, safe=False, status=200)

    except ValueError as e:
        return JsonResponse({"error": f"Invalid parameter: {e}"}, status=400)
    except Exception as e:
        # Log the error if logging is configured
        return JsonResponse({"error": "An unexpected error occurred."}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_child_portfolios(request, portfolio_code):
    if request.method == "GET":
        query = """
        WITH RECURSIVE portfolio_hierarchy AS (
            -- Base case: Select the given Portfolio Group using its portfolio_code
            SELECT 
                p.id AS parent_id,
                p.portfolio_name AS parent_name,
                p.portfolio_type,
                p.portfolio_code,
                p.id AS child_id,
                p.portfolio_name AS child_name,
                p.portfolio_type AS child_type,
                p.portfolio_code AS child_code
            FROM portfolio_portfolio p
            WHERE p.portfolio_code = %s  -- Parameterized query
    
            UNION ALL
    
            -- Recursive case: Find all children of the current parent in the hierarchy
            SELECT 
                ph.child_id AS parent_id,
                ph.child_name AS parent_name,
                ph.child_type AS portfolio_type,
                ph.child_code AS portfolio_code,
                p2.id AS child_id,
                p2.portfolio_name AS child_name,
                p2.portfolio_type AS child_type,
                p2.portfolio_code AS child_code
            FROM portfolio_hierarchy ph
            JOIN portfolio_portgroup pr ON ph.child_id = pr.parent_id
            JOIN portfolio_portfolio p2 ON pr.portfolio_id = p2.id
        )
        -- Retrieve only Automated portfolios from the hierarchy
        SELECT child_id, child_name, child_type, child_code
        FROM portfolio_hierarchy
        WHERE child_type = 'Portfolio';
        """

        # Execute query
        with connection.cursor() as cursor:
            cursor.execute(query, [portfolio_code])  # Prevents SQL injection
            results = cursor.fetchall()

        # Convert results to a list of dictionaries
        data = [
            row[3] for row in results
        ]
        print(data)
        # Return JSON response
        return JsonResponse({"child_portfolios": data}, safe=False)

# from django.db.models import Sum, Case, When, F

# Query to group by date and calculate positive and negative rgl
# result = (
#     PortfolioHolding.objects.values('date')
#     .annotate(
#         positive_rgl=Sum(Case(When(rgl__gt=0, then=F('rgl')), default=0)),
#         negative_rgl=Sum(Case(When(rgl__lt=0, then=F('rgl')), default=0)),
#     )
#     .order_by('date')  # Optional: to order by date
# )