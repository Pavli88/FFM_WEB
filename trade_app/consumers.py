import json
from channels.generic.websocket import AsyncWebsocketConsumer
from mysite.processes.oanda import *
from random import randint
from asyncio import sleep
import asyncio


class PriceStream(AsyncWebsocketConsumer):
    async def connect(self):
        print("")
        print("Creating a new connection instance...")
        await self.accept()

        # self.accept()
        self.oanda_connection = OandaV20(
            access_token="acc56198776d1ce7917137567b23f9a1-c5f7a43c7c6ef8563d0ebdd4a3b496ac",
            account_id="001-004-2840244-004",
            environment="live")

        print("New connection is successfull!")

    async def disconnect(self, close_code):
        print("Close Code:", close_code)
        print("Websocket connection is closed.")
        pass

    async def receive(self, text_data):
        print("Streaming request received from front end")
        print("STREAMING REQUEST:", text_data)

        self.price_stream = self.oanda_connection.pricing_stream(instrument='EUR_USD')

        print("PRICING STREAM:", self.price_stream)

        for ticks in self.price_stream:
            try:
                prices = {'bid': ticks['bids'][0]['price'],
                          'ask': ticks['asks'][0]['price']}
                print(prices)

                await self.send(text_data=json.dumps(prices))
                await sleep(1)
            except:
                pass

    async def post(self, event):
        print(event)

    async def run_task(self, task):
        print("Running task")
        asyncio.run(task)




