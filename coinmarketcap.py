from prometheus_client import start_http_server, Metric, REGISTRY
from threading import Lock
from cachetools import cached, TTLCache
import argparse
import json
import logging
import requests
import sys
import time
import os

# lock of the collect method
lock = Lock()

# coinmarketcap pro api key
try:
    CMC_PRO_API_KEY = os.environ['API_KEY']
except KeyError:
    print('Error!\nCoinMarketCap API KEY is not set.\nYou neet to set an environment variable API_KEY on the CLI.')
    sys.exit(1)
# coinmarketcap pro coin id
try:
    CMC_PRO_COIN_ID = os.environ['CoinID']
except KeyError:
    print('Error!\nCoinMarketCap Currency ID is not set.\nYou neet to set an environment variable CoinID on the CLI.')
    sys.exit(1)

# caching API for 2min
cache = TTLCache(maxsize=1000, ttl=120)

# logging setup
log = logging.getLogger('coinmarketcap-exporter')
log.setLevel(logging.INFO)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
log.addHandler(ch)


class CoinClient():
    def __init__(self):
        self.endpoint = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'

    @cached(cache)
    def tickers(self):
        r = requests.get('%s?id=%s&CMC_PRO_API_KEY=%s' % (self.endpoint, CMC_PRO_COIN_ID, CMC_PRO_API_KEY))
        return json.loads(r.content.decode('UTF-8'))

class CoinCollector():
    def __init__(self):
        self.client = CoinClient()

    def collect(self):
        with lock:
            log.info('collecting...')
            response = self.client.tickers()
            if not response['data']:
                log.info('HTTP error')
            metric = Metric('coin_market', 'coinmarketcap metric values', 'gauge')
            for _, value in response['data'].items():
                for that in ['cmc_rank', 'total_supply', 'max_supply', 'circulating_supply']:
                    coinmarketmetric = '_'.join(['coin_market', that])
                    if value[that] is not None:
                        metric.add_sample(coinmarketmetric, value=float(value[that]), labels={'id': value['slug'], 'name': value['name'], 'symbol': value['symbol']})
                for price in ['USD']:
                    for that in ['price', 'volume_24h', 'market_cap', 'percent_change_1h', 'percent_change_24h', 'percent_change_7d']:
                        coinmarketmetric = '_'.join(['coin_market', that, price]).lower()
                        if value['quote'][price] is None:
                            continue
                        if value['quote'][price][that] is not None:
                            metric.add_sample(coinmarketmetric, value=float(value['quote'][price][that]), labels={'id': value['slug'], 'name': value['name'], 'symbol': value['symbol']})
            yield metric

if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument('--port', nargs='?', const=9101, help='The TCP port to listen on', default=9101)
        parser.add_argument('--addr', nargs='?', const='0.0.0.0', help='The interface to bind to', default='0.0.0.0')
        args = parser.parse_args()
        log.info('listening on http://%s:%d/metrics' % (args.addr, args.port))

        REGISTRY.register(CoinCollector())
        start_http_server(int(args.port), addr=args.addr)

        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print(" Interrupted")
        exit(0)
