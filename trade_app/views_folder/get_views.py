from django.http import JsonResponse

# Model imports
from robots.models import Robots, RobotTrades

import pandas as pd


def get_open_trades(request, environment):
    if request.method == "GET":
        print('GET OPEN TRADES')
        robots = pd.DataFrame(Robots.objects.filter(env=environment).values())
        trades = pd.DataFrame(RobotTrades.objects.filter(status="OPEN").values())
        # df = pd.DataFrame(trades)
        print(robots)
        print(trades)
        response_list = []
        for index, row in robots.iterrows():
            filtered_trades_df = trades[trades['robot'] == str(row['id'])]
            filtered_trades_df['mv'] = filtered_trades_df['quantity'] * filtered_trades_df['open_price']
            print(filtered_trades_df)
            for ind, r in filtered_trades_df.iterrows():
                print(r)
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