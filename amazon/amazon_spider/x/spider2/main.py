# -*- coding: utf-8 -*-
__author__ = 'xtwxfxk'

import os, logging, logging.config

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

logging.config.fileConfig(os.path.join(BASE_DIR, 'logging.conf'))
logger = logging.getLogger('verbose')

spider_categories=['Home & Kitchen', 'Home Improvement', 'Beauty', 'Electronics', 'Sports & Outdoors', 'Health & Personal Care']

string_proxies = [
    'socks4://192.168.1.188:1080',
    'socks4://192.168.1.188:1081',
    'socks4://192.168.1.188:1082',
    'socks4://192.168.1.188:1083',
    # 'socks5://192.168.1.188:1084',
    # 'socks5://192.168.1.188:1085',
]

# def do_first(categories=[], is_all=False):
#     import urlparse
#     from lutils.lrequest import LRequest
#     from spider.base.models import URL_TYPE, Url
#
#     lr = LRequest(string_proxy='socks4://192.168.1.188:1080')
#
#     best_url = 'https://www.amazon.com/Best-Sellers-Beauty/zgbs/'
#     lr.load(best_url)
#
#     category_eles = lr.xpaths('//ul[@id="zg_browseRoot"]/ul/li/a')
#     for category_ele in category_eles:
#         if category_ele.text.strip() in categories or is_all:
#             Url.create(url=urlparse.urljoin(best_url, category_ele.attrib['href']), type=URL_TYPE.BEST_SELL_CATEGORY, name=category_ele.text.strip())

if __name__ == "__main__":

    # do_first(categories=spider_categories)

    from spider.best_sell import BestSell

    bs = BestSell(string_proxies=string_proxies)

    bs.best_categories(spider_categories)