
import aiohttp
import asyncio
import sys
from pprint import pprint
import datetime

all_currencies = ['AUD','AZN','BYN','CAD','CHF','CNY','CZK','DKK','EUR','GBP','GEL','HUF','ILS','JPY','KZT','MDL','NOK','PLN','SEK','SGD','TMT','TRY','UAH','USD','UZS','XAU','AUD','AZN','BYN','CAD','CHF','CNY','CZK','DKK','EUR','GBP','GEL','HUF','ILS','JPY','KZT','MDL','NOK','PLN','SEK','SGD','TMT','TRY','UAH','USD','UZS','XAU']


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

async def main():
    # Parse command line arguments
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    currencies = ['EUR', 'USD'] + sys.argv[2:]
    if days <= 10:
        # Generate list of dates
        dates = [(datetime.datetime.now() - datetime.timedelta(days=i)).strftime('%d.%m.%Y') for i in range(days)]
        results = await get_exchange_rates(dates, currencies)
        pprint(results)
        
    else:
        print('Please check the day amount (should be less than 10 days)!')

        
if __name__ == '__main__':
    asyncio.run(main())
