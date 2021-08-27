import json
from channels.generic.websocket import AsyncWebsocketConsumer
from mysite.processes.oanda import *
from random import randint
from asyncio import sleep


class PriceStream(AsyncWebsocketConsumer):
    async def connect(self):
        print("Creating a new connection instance...")
        await self.accept()
        for i in range(1000):
            await self.send(json.dumps({'value' : randint(-20, 20)}))
            await sleep(1)

        # self.accept()
        # self.oanda_connection = OandaV20(
        #     access_token="acc56198776d1ce7917137567b23f9a1-c5f7a43c7c6ef8563d0ebdd4a3b496ac",
        #     account_id="001-004-2840244-004",
        #     environment="live")

        print("New connection is successfull!")

    async def disconnect(self, close_code):
        print("Close Code:", close_code)
        print("Websocket connection is closed.")
        pass

    async def receive(self, text_data):
        pass

        # self.price_stream = self.oanda_connection.pricing_stream(instrument=text_data)
        #
        # print("PRICING STREAM:", self.price_stream)
        #
        # for ticks in self.price_stream:
        #     try:
        #         prices = {'bid': ticks['bids'][0]['price'],
        #                   'ask': ticks['asks'][0]['price']}
        #         print(prices)
        #
        #         self.send(text_data=json.dumps(prices))
        #     except:
        #         pass

