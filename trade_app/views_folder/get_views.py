from django.http import JsonResponse
from trade_app.models import Notifications, Signal, Order
from portfolio.models import Portfolio
from instrument.models import Instruments
import pandas as pd
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from broker_apis.oanda import OandaV20


def get_open_trades(request, environment):
    if request.method == "GET":
        robots = pd.DataFrame(Robots.objects.filter(env=environment).values())
        trades = pd.DataFrame(RobotTrades.objects.filter(status="OPEN").values())
        response_list = []
        for index, row in robots.iterrows():
            filtered_trades_df = trades[trades['robot'] == str(row['id'])]
            filtered_trades_df['mv'] = filtered_trades_df['quantity'] * filtered_trades_df['open_price']
            record = {'id': row['id'],
                      'robot_name': row['name'],
                      'market': row['security'],
                      'total_positions': len(filtered_trades_df['id']),
                      'total_units': filtered_trades_df['quantity'].sum(),
                      'average_price': round(abs(filtered_trades_df['mv'].sum()/filtered_trades_df['quantity'].sum()), 2),
                      'trades': filtered_trades_df.to_dict(orient='records')}
            if len(filtered_trades_df['id']) > 0:
                response_list.append(record)
        return JsonResponse(response_list, safe=False)


def trade_signals(request):
    print("Get Trade Signal notifications")
    return JsonResponse(list(Notifications.objects.filter().values()), safe=False)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_signals(request):
    user = request.user
    portfolios = Portfolio.objects.filter(user=user)
    portfolio_codes = portfolios.values_list('portfolio_code', flat=True)

    signals = Signal.objects.filter(portfolio__portfolio_code__in=portfolio_codes, created_at__date=request.GET.get('date')).order_by('-created_at')

    # Gyűjtsük ki az összes security_id-t
    security_ids = list({
        s.raw_data.get('security_id') for s in signals
        if s.raw_data.get('security_id') is not None
    })

    # Töltsük be a kapcsolódó instrumentumokat
    instruments = Instruments.objects.filter(id__in=security_ids)
    instrument_map = {inst.id: inst.name for inst in instruments}

    # Készítsük el a válasz listát
    signal_data = [
        {
            'id': s.id,
            'type': s.type,
            'portfolio_code': s.raw_data.get('portfolio_code'),
            'raw_data': s.raw_data,
            'source': s.source,
            'status': s.status,
            'error_message': s.error_message,
            'executed_at': s.executed_at,
            'created_at': s.created_at,
            'instrument_name': instrument_map.get(s.raw_data.get('security_id'), '-')
        }
        for s in signals
    ]

    return Response({'signals': signal_data}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_orders(request):
    user = request.user
    signal_id = request.GET.get('signal_id')

    # Lekérjük az adott userhez tartozó megbízásokat
    orders = Order.objects.filter(signal_id=signal_id).order_by('-created_at')

    # Gyűjtjük a security_id-ket
    security_ids = list({o.security_id for o in orders if o.security_id is not None})

    # Lekérjük az instrumentumokat
    instruments = Instruments.objects.filter(id__in=security_ids)
    instrument_map = {inst.id: inst.name for inst in instruments}

    # Összeállítjuk a válasz struktúrát
    order_data = [
        {
            'id': o.id,
            'portfolio_code': o.portfolio.portfolio_code,
            'symbol': o.symbol,
            'security_id': o.security_id,
            'instrument_name': instrument_map.get(o.security_id, '-'),
            'side': o.side,
            'quantity': str(o.quantity),
            'executed_price': str(o.executed_price) if o.executed_price else None,
            'fx_rate': str(o.fx_rate) if o.fx_rate else None,
            'status': o.status,
            'error_message': o.error_message,
            'executed_at': o.executed_at,
            'created_at': o.created_at,
            'signal_id': o.signal.id if o.signal else None,
            'broker_order_id': o.broker_order_id,
        }
        for o in orders
    ]

    return Response({'orders': order_data}, status=status.HTTP_200_OK)
