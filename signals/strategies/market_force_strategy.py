from mysite.processes.oanda import *

from time import time, sleep
from datetime import datetime
import matplotlib.pyplot as plt
# Indicator import
from signals.functions.indicators import *


class MarketForceStrategy:
    def __init__(self, df):
        self.df = df

    def calculate_indicators(self, threshold):
        # Moving averages
        ma50 = moving_avg(df=self.df, source='close', length=50)
        ma100 = moving_avg(df=self.df, source='close', length=100)
        ma200 = moving_avg(df=self.df, source='close', length=200)

        # Distances
        dist50 = percentage_distance(df=self.df, comparator='close', compared=ma50)
        dist100 = percentage_distance(df=self.df, comparator='close', compared=ma100)
        dist200 = percentage_distance(df=self.df, comparator='close', compared=ma200)
        #
        ma100_dist100 = moving_avg(df=self.df, source=dist100, length=100)
        ma10_dist50 = moving_avg(df=self.df, source=dist50, length=10)

        crossover(self.df, self.df[ma10_dist50], threshold, name='MA10_D50_CO_0')
        crossunder(self.df, self.df[ma10_dist50], threshold, name='MA10_D50_CA_0')
        crossover(self.df, self.df[ma100_dist100], threshold, name='MA100_D100_CO_0')
        crossunder(self.df, self.df[ma100_dist100], threshold, name='MA100_D100_CA_0')
        above(self.df, self.df[ma100_dist100], threshold, name='MA100_D100_Above_0')
        below(self.df, self.df[ma100_dist100], threshold, name='MA100_D100_Below_0')

    def signal_generator(self):
        df = self.df.tail(1)

        # Buy Signal
        if df['MA10_D50_CO_0'].iloc[0] and df['MA100_D100_Above_0'].iloc[0]:
            print("BUY SIGNAL")
            return 'BUY'

        # Sell Signal
        elif df['MA10_D50_CA_0'].iloc[0] and df['MA100_D100_Below_0'].iloc[0]:
            print("SELL SIGNAL")
            return 'SELL'

        # Buy Close Signal
        elif df['MA100_D100_CA_0'].iloc[0]:
            return 'BUY Close'

        # Sell Close Signal
        elif df['MA100_D100_CO_0'].iloc[0]:
            return 'SELL Close'
        else:
            return None


def strategy_evaluate(df, params):
    strategy = MarketForceStrategy(df=df)
    strategy.calculate_indicators(threshold=params['threshold'])
    return strategy.signal_generator()
