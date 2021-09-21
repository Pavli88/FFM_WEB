from mysite.processes.oanda import *

from time import time, sleep
from datetime import datetime


class MarketForceStrategy:
    def __init__(self, df):
        self.df = df

    def calculate_indicators(self):

        self.df['MA50'] = self.df['close'].rolling(window=50).mean()
        self.df['MA100'] = self.df['close'].rolling(window=100).mean()
        self.df['MA200'] = self.df['close'].rolling(window=200).mean()
        self.df['Dist50'] = (self.df['close']-self.df['MA50']) / self.df['MA50']
        self.df['Dist100'] = (self.df['close']-self.df['MA100']) / self.df['MA100']
        self.df['Dist200'] = (self.df['close']-self.df['MA200']) / self.df['MA200']
        self.df['MA100_DIST100'] = self.df['Dist100'].rolling(window=100).mean()
        self.df['50Under'] = self.df['Dist50'].le(self.df['MA100_DIST100'])
        self.df['200Under'] = self.df['Dist200'].le(self.df['MA100_DIST100'])

    def signal_generator(self):
        self.df = self.df.iloc[-2:]
        df50_list = list(self.df['50Under'])
        df200_list = list(self.df['200Under'])
        now = datetime.now()
        current_time = now.strftime("%H:%M")

        # Current Condition
        if df50_list[-1] is True and df200_list[-1] is True:
            current_condition = "SELL"
        elif df50_list[-1] is False and df200_list[-1] is False:
            current_condition = "BUY"
        else:
            current_condition = "NETURAL"

        # Previous condition
        if df50_list[0] is True and df200_list[0] is True:
            prev_condition = "SELL"
        elif df50_list[0] is False and df200_list[0] is False:
            prev_condition = "BUY"
        else:
            prev_condition = "NETURAL"

        print(current_time, 'Previous Condition:', prev_condition)
        print(current_time, 'Current Condition:', current_condition)

        if prev_condition == 'NETURAL' and current_condition == 'BUY':
            return 'BUY'

        if prev_condition == 'NETURAL' and current_condition == 'SELL':
            return 'SELL'


def strategy_evaluate(df):
    strategy = MarketForceStrategy(df=df)
    strategy.calculate_indicators()
    return strategy.signal_generator()

