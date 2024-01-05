import aiohttp
import asyncio
import logging
import websockets
from websockets import WebSocketServerProtocol, WebSocketProtocolError
import names
import datetime
from pprint import pprint
import json

logging.basicConfig(level=logging.INFO)


# =================================
async def fetch_exchange_rate(session, date):
    url = f"https://api.privatbank.ua/p24api/exchange_rates?json&date={date}"
    async with session.get(url) as response:
        data = await response.json()
        return data

async def get_exchange_rates(dates, currencies):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for date in dates:
            tasks.append(fetch_exchange_rate(session, date))

        results = await asyncio.gather(*tasks)

        formatted_results = []
        for result in results:
            formatted_result = {}
            # pprint(result)
            for i in result['exchangeRate']:
                if i.get('currency') in currencies:
                    formatted_result[i.get('currency')] = {
                        'purchase': i['purchaseRate'],
                        'sale': i['saleRate']
                    }
            formatted_results.append({result['date']:formatted_result})

        return formatted_results
# ==========================================================
class Server:
    clients = set()

    async def register(self, ws: WebSocketServerProtocol):
        ws.name = names.get_full_name()
        self.clients.add(ws)
        logging.info(f'{ws.remote_address} connects')

    async def unregister(self, ws: WebSocketServerProtocol):
        self.clients.remove(ws)
        logging.info(f'{ws.remote_address} disconnects')

    async def send_to_clients(self, message: str):
        if self.clients:
            [await client.send(message) for client in self.clients]

    async def ws_handler(self, ws: WebSocketServerProtocol):
        await self.register(ws)
        try:
            await self.distrubute(ws)
        except WebSocketProtocolError as err:
            logging.error(err)
        finally:
            await self.unregister(ws)

    async def distrubute(self, ws: WebSocketServerProtocol):
        currencies = ['EUR', 'USD']
        async for message in ws:
            if message == '':
                await self.send_to_clients("Please print any text")
            elif message.split( )[0] == 'exchange':
                days = int(message.split( )[1]) if len(message.split( )) > 1 else 1
                if days <= 10:
                    dates = [(datetime.datetime.now() - datetime.timedelta(days=i+1)).strftime('%d.%m.%Y') for i in range(days)]
                    results = await get_exchange_rates(dates, currencies)
                    output = f'Result for past {days} days:{results}'
                    await self.send_to_clients(output)
                else:
                    await self.send_to_clients("The amount of days should be less than 10")
            else:
                await self.send_to_clients(f"{ws.name}: {message}")


async def main():
    server = Server()
    async with websockets.serve(server.ws_handler, 'localhost', 8080):
        await asyncio.Future()  # run forever

if __name__ == '__main__':
    asyncio.run(main())
