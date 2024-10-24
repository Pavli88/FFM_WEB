from django.http import JsonResponse
from trade_app.models import Notifications
import pandas as pd
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