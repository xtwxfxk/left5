# -*- coding: utf-8 -*-
__author__ = 'xtwxfxk'

import logging, urlparse, traceback, hashlib, threading
from shove import Shove

from sqlalchemy import update

from base import AmazonBase
from base.models import URL_TYPE

logger = logging.getLogger('verbose')


class ThreadSet(set):
    def __init__(self):
        self.l = threading.Lock()

    def append(self, val):
        try:
            self.l.acquire()
            set.add(self, val)
        finally:
            if self.l.locked():
                self.l.release()

def category(method):
    def wrapped(self, **kwargs):
        try:
            assert 'url_obj' in kwargs

            method(self, **kwargs)

            url_obj = kwargs.get('url_obj')

            p_categories = url_obj[2].split('@@')
            floor_ul = '/'.join(['ul' for i in range(len(p_categories))])

            category_xpaths = '//ul[@id="zg_browseRoot"]/ul/li/a'
            if floor_ul: category_xpaths = '//ul[@id="zg_browseRoot"]/ul/%s/li/a' % floor_ul

            urls = []

            category_eles = self.lr.xpaths(category_xpaths)
            if category_eles is not None and len(category_eles) > 0:
                for category_ele in category_eles:
                    url = self.wrapped_url(urlparse.urljoin(self.lr.current_url, category_ele.attrib['href']))
                    text = category_ele.text.strip()

                    key = '%s@@%s' % (url_obj[2], text)

                    md5_key = hashlib.md5(key.encode('utf-8')).hexdigest()

                    if md5_key not in self.key_set:
                        logger.info('Add Category: %s' % url)
                        self.url_info[md5_key] = [url, URL_TYPE.BEST_SELL_CATEGORY, key, False, md5_key]
                        self.key_set.add(md5_key)

            self.url_info.sync()
        except:
            logger.error(traceback.format_exc())
    return wrapped

def next_page(method):
    def wrapped(self, **kwargs):

        try:
            method(self, **kwargs)

            urls = []

            for ele in self.lr.xpaths('//div[@id="zg_paginationWrapper"]//a')[1:]:
                page_url = urlparse.urljoin(self.lr.current_url, ele.attrib['href'].strip())

                id = page_url.split('/ref', 1)[0].rsplit('/', 1)[-1]
                index = page_url.split('&pg=', 1)[-1]
                key = '%s_%s' % (id, index)
                md5_key = hashlib.md5(key).hexdigest()

                if md5_key not in self.key_set:
                    logger.info('Add Category Page: %s' % page_url)
                    self.url_info[md5_key] = [page_url, URL_TYPE.BEST_SELL_CATEGORY_NEXT, key, False, md5_key]
                    self.key_set.add(md5_key)

            self.url_info.sync()
        except:
            logger.error(traceback.format_exc())


    return wrapped

def product_url(method):
    def wrapped(self, **kwargs):

        try:
            method(self, **kwargs)

            urls = []
            product_eles = self.lr.xpaths('//div[@class="zg_itemImageImmersion"]/a')

            for ele in product_eles:
                product_url = urlparse.urljoin(self.lr.current_url, ele.attrib['href'].strip())
                asin = product_url.split('/dp/', 1)[1].split('/', 1)[0]

                md5_key = hashlib.md5(asin).hexdigest()

                if md5_key not in self.key_set:
                    logger.info('Add Product: %s' % asin)
                    self.url_info[md5_key] = [product_url, URL_TYPE.PRODUCT_URL, asin, False, md5_key]
                    self.key_set.add(md5_key)

            self.url_info.sync()
        except:
            logger.error(traceback.format_exc())

    return wrapped

def url_over(method):
    def wrapped(self, **kwargs):

        method(self, **kwargs)

        url_obj = kwargs.get('url_obj')
        url_obj[3] = True

        self.url_info[url_obj[4]] = url_obj
        self.url_info.sync()

    return wrapped

class BestSell(AmazonBase):

    URL_INFO_ROOT = 'I:\\amazon_url_info'

    best_url = 'https://www.amazon.com/Best-Sellers/zgbs'

    def __init__(self, key_set, **kwargs):
        super(BestSell, self).__init__(**kwargs)

        self.URL_INFO_ROOT = kwargs.get('url_info_root',  'file:///I:\\amazon_url_info')

        self.url_info = Shove(self.URL_INFO_ROOT)

        self.key_set = key_set


    @category
    @next_page
    @product_url
    @url_over
    def categories(self, url_obj=None, **kwargs):
        self.load(url_obj[0].encode('utf-8'))



    @product_url
    @url_over
    def category_next(self, url_obj=None, **kwargs):
        self.load(url_obj[0].encode('utf-8'))

    @url_over
    def product(self, url_obj=None, **kwargs):

        md5 = hashlib.md5(url_obj[2])
        cache_name = '%s.gz' % md5.hexdigest()

        if self.load_cache(cache_name):
            logger.info('Product File Exists: %s' % url_obj[2])
            return

        super(BestSell, self).product(asin=url_obj[2], **kwargs)

    def categories_first(self, categories):
        self.load(self.best_url)

        category_eles = self.lr.xpaths('//ul[@id="zg_browseRoot"]/ul/li/a')

        for category_ele in category_eles:
            if category_ele.text.strip() in categories:
                url = self.wrapped_url(urlparse.urljoin(self.best_url, category_ele.attrib['href']))

                key = category_ele.text.strip()
                md5_key = hashlib.md5(key.encode('utf-8')).hexdigest()

                if md5_key not in self.key_set:
                    self.url_info[md5_key] = [url, URL_TYPE.BEST_SELL_CATEGORY, key, False, md5_key]
                    self.key_set.add(md5_key)

        self.url_info.sync()
