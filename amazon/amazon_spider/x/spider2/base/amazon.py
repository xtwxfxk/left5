# -*- coding: utf-8 -*-
__author__ = 'xtwxfxk'

import os, time, traceback, codecs, urlparse, xlsxwriter, base64, StringIO, random, io, json, copy, cPickle, threading, hashlib, Queue, urllib, logging
from PIL import Image
from collections import OrderedDict
from ClientForm import ControlNotFoundError

from lutils import todir3
from lutils.captcha.gsa_captcha import GsaCaptcha
from lutils.lrequest import LRequest
from lutils.thread import LThread
from lutils.futures.thread import LThreadPoolExecutor

from models import Url, URL_TYPE

logger = logging.getLogger('verbose')

class Amazon(object):

    CACHE_ROOT = 'I:\\cache'
    CACHE_EXPIRED_DAYS = 15

    best_url = 'https://www.amazon.com/Best-Sellers/zgbs'
    home_url = 'http://www.amazon.com'

    max_workers = 1
    string_proxies = []
    captcha = None

    def __init__(self, **kwargs):

        Amazon.CACHE_ROOT = kwargs.get('CACHE_ROOT', 'I:\\cache')
        Amazon.CACHE_EXPIRED_DAYS = kwargs.get('CACHE_EXPIRED_DAYS', 15)


        Amazon.max_workers = kwargs.get('max_workers', 1)
        Amazon.string_proxies = kwargs.get('string_proxies', [])

        if len(Amazon.string_proxies) > 0:
            Amazon.lr = LRequest(string_proxy=Amazon.string_proxies[0])

        Amazon.captcha = GsaCaptcha(ip='192.168.1.188', port='8000')

        self.executor = LThreadPoolExecutor(max_workers=Amazon.max_workers)

    # def load(self, lr, url):
    #     if Amazon.check_captcha(lr):
    #         lr.load(url)



    def best_categories(self, spider_categories):
        self.load(self.lr, self.best_url)

        # category_eles = self.lr.xpaths('//ul[@id="zg_browseRoot"]/ul/li/a')
        # for category_ele in category_eles:
        #     if category_ele.text.strip() in spider_categories:
        #         url = Amazon.wrapped_url(urlparse.urljoin(self.best_url, category_ele.attrib['href']))
        #
        #         if Url.select().where(Url.url==url).wrapped_count() < 1:
        #             Url.create(url=url, type=URL_TYPE.BEST_SELL_CATEGORY, name=category_ele.text.strip())


        for url in Url.select().where(Url.type==URL_TYPE.BEST_SELL_CATEGORY, Url.has_crawled==False):
            print url.url

    @staticmethod
    def wrapped_url(url):
        return url.split('/ref', 1)[0]


    @staticmethod
    def check_captcha(lr):
        captcha_img_ele = lr.xpath('//form[contains(@action, "Captcha")]//img[contains(@src, "captcha")]')
        if captcha_img_ele is not None:
            while 1:
                if captcha_img_ele is not None:
                    logger.info('Need Captcha')
                    form = lr.get_forms()[0]
                    lr.load(captcha_img_ele.attrib['src'])
                    cap = Amazon.captcha.decode_stream(lr.body)
                    logger.info('    Captcha: %s' % (cap))
                    form['field-keywords'] = cap
                    lr.load(form.click())
                else:
                    return True

                captcha_img_ele = lr.xpath('//form[contains(@action, "Captcha")]//img[contains(@src, "captcha")]')

        return False

    @staticmethod
    def load(lr, url, is_xpath=True):
        lr.load(url, is_xpath=is_xpath)
        if Amazon.check_captcha(lr):
            lr.load(url, is_xpath=is_xpath)

    @staticmethod
    def load_cache(key):
        cache_path = os.path.join(Amazon.CACHE_ROOT, key[0], key[1], key)

        try:
            return cPickle.loads(gzip.GzipFile(cache_path, 'rb').read())
        except:
            return {}

    @staticmethod
    def save_cache(key, data):
        _p = os.path.join(Amazon.CACHE_ROOT, key[0], key[1])
        if not os.path.exists(_p): os.makedirs(_p)

        cache_path = os.path.join(Amazon.CACHE_ROOT, key[0], key[1], key)

        gzip_file = gzip.open(cache_path, 'wb')
        gzip_file.write(cPickle.dumps(data))
        gzip_file.close()


    class _Amazon():

        from decorators import cache

        def __init__(self, **kwargs):

            self.lr = LRequest(string_proxy=kwargs.get('string_proxy', ''))



        @cache
        def product_url(self, asin):
            Amazon.load(self.lr, 'https://www.amazon.com/dp/%s' % asin)





        def spider_best_categories(self, spider_categories):
            self.load(self.best_url)




