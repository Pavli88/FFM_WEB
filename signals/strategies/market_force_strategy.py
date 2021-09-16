from mysite.processes.oanda import *
import matplotlib.pyplot as plt
from time import time, sleep
from datetime import datetime


class MarketForceStrategy:
    def __init__(self, token, account_id, environment, instrument, initial_frame_count, time_frame):
        self.time_frame = time_frame
        self.instrument = instrument
        self.connection = OandaV20(access_token="acc56198776d1ce7917137567b23f9a1-c5f7a43c7c6ef8563d0ebdd4a3b496ac",
                                   account_id="001-004-2840244-004",
                                   environment="live")

        self.initial_data = self.get_candle_data(count=initial_frame_count)
        self.df = self.create_dataframe(self.initial_data)

        if self.time_frame == 'M1':
            self.time_multiplier = 1
        elif self.time_frame == 'M5':
            self.time_multiplier = 5

        print(self.df)

    def get_candle_data(self, count):
        return self.connection.candle_data(instrument=self.instrument,
                                           count=count,
                                           time_frame=self.time_frame)['candles']

    def create_dataframe(self, data):

        time_list = []
        open_list = []
        close_list = []
        low_list = []
        high_list = []

        for record in data:
            time_list.append(record['time'])
            open_list.append(float(record['mid']['o']))
            close_list.append(float(record['mid']['c']))
            low_list.append(float(record['mid']['l']))
            high_list.append(float(record['mid']['h']))

        df = pd.DataFrame({'time': time_list,
                           'open': open_list,
                           'high': high_list,
                           'low': low_list,
                           'close': close_list})

        return df

    def calculate_indicators(self, df):

        df['MA50'] = df['close'].rolling(window=50).mean()
        df['MA100'] = df['close'].rolling(window=100).mean()
        df['MA200'] = df['close'].rolling(window=200).mean()
        df['Dist50'] = (df['close']-df['MA50']) / df['MA50']
        df['Dist100'] = (df['close']-df['MA100']) / df['MA100']
        df['Dist200'] = (df['close']-df['MA200']) / df['MA200']
        df['MA100_DIST100'] = df['Dist100'].rolling(window=100).mean()
        df['50Under'] = df['Dist50'].le(df['MA100_DIST100'])
        df['200Under'] = df['Dist200'].le(df['MA100_DIST100'])

        return df

    def add_new_row(self, df):
        self.df = self.df.append(df)

    def run(self):
        # self.add_new_row(df=self.create_dataframe(self.get_candle_data(count=1)))
        # df = self.calculate_indicators(df=self.df)
        #
        # print(df.iloc[-2:])
        # plt.figure(figsize=[15,10])
        # plt.grid(True)
        # plt.plot(df['Dist200'],label='data')
        # plt.plot(df['Dist50'],label='data')
        # plt.plot(df['MA100_DIST100'],label='data')
        # plt.legend(loc=2)
        # plt.show()
        while True:
            sleep(60 * self.time_multiplier - time() % 60 * self.time_multiplier)
            now = datetime.now()
            current_time = now.strftime("%H:%M")
            self.add_new_row(df=self.create_dataframe(self.get_candle_data(count=1)))
            df = self.calculate_indicators(df=self.df)
            print(df)
            print(df.iloc[-2:])

strategy = MarketForceStrategy(token="acc56198776d1ce7917137567b23f9a1-c5f7a43c7c6ef8563d0ebdd4a3b496ac",
                               account_id="001-004-2840244-004",
                               environment='live',
                               instrument='EUR_USD',
                               initial_frame_count=500,
                               time_frame='M1')

strategy.run()

# plt.figure(figsize=[15,10])
# plt.grid(True)
# plt.plot(df['Dist200'],label='data')
# plt.plot(df['Dist50'],label='data')
# plt.plot(df['MA100_DIST100'],label='data')
# plt.legend(loc=2)
# plt.show()