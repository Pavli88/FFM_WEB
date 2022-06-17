import pandas as pd


def monthly_returns_calc(data):
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])
    monthly_return_list = []
    for i in range(1, 13):
        monthly_df = df[df['date'].dt.month == i]
        monthly_df.reset_index(drop=True)
        if len(monthly_df['close_balance']) == 0:
            starting_balance = 0.0
            ending_balance = 0.0
        else:
            starting_balance = list(monthly_df['close_balance'])[0]
            ending_balance = list(monthly_df['close_balance'])[-1]
        cash_flow = monthly_df['cash_flow'].sum()
        if starting_balance == 0.0:
            monthly_return = 0.0
        else:
            monthly_return = (((ending_balance-cash_flow)/starting_balance)-1)*100
        monthly_return_list.append(round(monthly_return, 2))
    return monthly_return_list