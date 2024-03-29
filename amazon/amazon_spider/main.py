# -*- coding: utf-8 -*-
__author__ = 'xtwxfxk'

import logging, logging.config, time, traceback

from lutils.futures.thread import LThreadPoolExecutor

from spider.best_sell import BestSell
from spider.base.models import Url, URL_TYPE, Session

logging.config.fileConfig('logging.conf')

logger = logging.getLogger('verbose')

multiple = 8

string_proxies = [
    'socks4://192.168.1.188:1080',
    'socks4://192.168.1.188:1081',
    # 'socks4://192.168.1.188:1082',
    # 'socks4://192.168.1.188:1083',
    'socks4://192.168.1.188:1084',
]

executor = LThreadPoolExecutor(max_workers=len(string_proxies)*multiple*3)

# b = BestSell(string_proxy='socks4://192.168.1.188:1080')

# b.product('B01FQN3W5U')

spider_categories=['Home & Kitchen', 'Home Improvement', 'Beauty', 'Electronics', 'Sports & Outdoors', 'Health & Personal Care']

# b.categories_first(categories=spider_categories)
# b.categories(url_obj=url_obj)

bs = []
for i in range(multiple):
    for string_proxy in string_proxies:
        bs.append(BestSell(string_proxy=string_proxy))

# bs[0].categories_first(categories=spider_categories)


def category():
    session = Session()
    while session.query(Url).filter_by(type=URL_TYPE.BEST_SELL_CATEGORY, has_crawled=False).count() > 0:
        for i, url_obj in enumerate(session.query(Url).filter_by(type=URL_TYPE.BEST_SELL_CATEGORY, has_crawled=False)): # .limit(20*len(string_proxies))):
            executor.submit(bs[i%len(bs)].categories, url_obj=url_obj)
            time.sleep(0.1)

        time.sleep(30)

def category_next():
    try:
        session = Session()
        while session.query(Url).filter_by(type=URL_TYPE.BEST_SELL_CATEGORY_NEXT, has_crawled=False).count() > 0:
            for i, url_obj in enumerate(session.query(Url).filter_by(type=URL_TYPE.BEST_SELL_CATEGORY_NEXT, has_crawled=False)): #.limit(20*len(string_proxies))):
                executor.submit(bs[i%len(bs)].category_next, url_obj=url_obj)
                time.sleep(0.1)

            time.sleep(30)
    except:
        logger.error(traceback.format_exc())


def product():
    try:
        session = Session()
        while session.query(Url).filter_by(type=URL_TYPE.PRODUCT_URL, has_crawled=False).count() > 0:
            for i, url_obj in enumerate(session.query(Url).filter_by(type=URL_TYPE.PRODUCT_URL, has_crawled=False)): #.limit(20*len(string_proxies))):
                executor.submit(bs[i%len(bs)].product, url_obj=url_obj)
                time.sleep(0.1)
            time.sleep(30)
    except:
        logger.error(traceback.format_exc())

executor.submit(product)
executor.submit(category_next)
executor.submit(category)







