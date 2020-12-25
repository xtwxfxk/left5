# -*- coding: utf-8 -*-
__author__ = 'xtwxfxk'

import logging, logging.config, time, traceback
from shove import Shove

# from lutils.futures.thread import LThreadPoolExecutor

from spider1.best_sell2 import BestSell, ThreadSet
from spider1.base.models import URL_TYPE

logging.config.fileConfig('logging.conf')

logger = logging.getLogger('verbose')

multiple = 8


string_proxies = [
    'socks4://192.168.1.188:1080',
    'socks4://192.168.1.188:1081',
    'socks4://192.168.1.188:1082',
    # 'socks4://192.168.1.188:1083',
    'socks4://192.168.1.188:1084',
]

url_info_root = 'file:///I:\\amazon_url_info\\best_sell'

executor = LThreadPoolExecutor(max_workers=len(string_proxies)*multiple*2)

spider_categories=['Home & Kitchen', 'Home Improvement', 'Beauty', 'Electronics', 'Sports & Outdoors', 'Health & Personal Care']

url_info = Shove(url_info_root)
key_set = ThreadSet()

key_set = key_set.union(url_info.keys())

bs = []
for i in range(multiple):
    for string_proxy in string_proxies:
        bs.append(BestSell(key_set, string_proxy=string_proxy, url_info_root=url_info_root))

# bs[0].categories_first(categories=spider_categories)


def spider():

    while 1:
        i = 0
        for key, value in url_info.items():
            if not value[3]:
                if value[1] == URL_TYPE.BEST_SELL_CATEGORY:
                   executor.submit(bs[i%len(bs)].categories, url_obj=value)
                if value[1] == URL_TYPE.BEST_SELL_CATEGORY_NEXT:
                   executor.submit(bs[i%len(bs)].category_next, url_obj=value)
                elif value[1] == URL_TYPE.PRODUCT_URL:
                    executor.submit(bs[i%len(bs)].product, url_obj=value)

                i += 1

        logger.info('Wait 5 Second...')
        time.sleep(5)

spider()







