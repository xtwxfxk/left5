# -*- coding: utf-8 -*-
__author__ = 'xtwxfxk'

import logging, urlparse, traceback, threading

# from multiprocessing.queues import Empty
from Queue import Empty, Queue

from sqlalchemy import update

from base import AmazonBase
from base.models import Url, URL_TYPE, Session, DictDot


logger = logging.getLogger('verbose')


def category(method):
    def wrapped(self, **kwargs):
        assert 'url_obj' in kwargs
        # session = Session(autocommit=True)

        method(self, **kwargs)

        url_obj = kwargs.get('url_obj')

        p_categories = url_obj.key.split('@@')
        floor_ul = '/'.join(['ul' for i in range(len(p_categories))])

        category_xpaths = '//ul[@id="zg_browseRoot"]/ul/li/a'
        if floor_ul: category_xpaths = '//ul[@id="zg_browseRoot"]/ul/%s/li/a' % floor_ul

        urls = []
        category_eles = self.lr.xpaths(category_xpaths)
        if category_eles is not None and len(category_eles) > 0:
            for category_ele in category_eles:
                url = self.wrapped_url(urlparse.urljoin(self.lr.current_url, category_ele.attrib['href']))
                text = category_ele.text.strip()

                key = '%s@@%s' % (url_obj.key, text)

                urls.append(Url(url=url, type=URL_TYPE.BEST_SELL_CATEGORY, name=text, key=key))

        self.output.put(['add', urls])
    return wrapped

def next_page(method):
    def wrapped(self, **kwargs):

        method(self, **kwargs)

        urls = []
        for ele in self.lr.xpaths('//div[@id="zg_paginationWrapper"]//a')[1:]:
            page_url = urlparse.urljoin(self.lr.current_url, ele.attrib['href'].strip())

            id = page_url.split('/ref', 1)[0].rsplit('/', 1)[-1]
            index = page_url.split('&pg=', 1)[-1]
            key = '%s_%s' % (id, index)

            urls.append(Url(url=page_url, type=URL_TYPE.BEST_SELL_CATEGORY_NEXT, key=key))

        self.output.put(['add', urls])

    return wrapped

def product_url(method):
    def wrapped(self, **kwargs):
        method(self, **kwargs)

        urls = []
        product_eles = self.lr.xpaths('//div[@class="zg_itemImageImmersion"]/a')
        for ele in product_eles:
            product_url = urlparse.urljoin(self.lr.current_url, ele.attrib['href'].strip())
            asin = product_url.split('/dp/', 1)[1].split('/', 1)[0]

            urls.append(Url(url=product_url, type=URL_TYPE.PRODUCT_URL, key=asin))

        self.output.put(['add', urls])

    return wrapped

def url_over(method):
    def wrapped(self, **kwargs):
        try:
            # session = Session(autocommit=True)

            url_obj = kwargs.get('url_obj')

            method(self, **kwargs)
        except Exception as e:
            logger.error(e)
            logger.error(traceback.format_exc())

            self.output.put(['error', [url_obj, ]])
        else:
            self.output.put(['over', [url_obj, ]])

    return wrapped

class BestSell(AmazonBase, threading.Thread):

    best_url = 'https://www.%s/gp/bestsellers'

    def __init__(self, **kwargs):
        # super(BestSell, self).__init__(**kwargs)

        AmazonBase.__init__(self, **kwargs)
        threading.Thread.__init__(self)

        self.input = kwargs.get('input')
        self.output = kwargs.get('output')

        self.session = Session(autocommit=True)

    @category
    @next_page
    @product_url
    @url_over
    def categories(self, url_obj=None, **kwargs):
        self.load(url_obj.url.encode('utf-8'))


    @product_url
    @url_over
    def category_next(self, url_obj=None, **kwargs):
        self.load(url_obj.url.encode('utf-8'))

    @url_over
    def product(self, url_obj=None, **kwargs):
        super(BestSell, self).product(asin=url_obj.key, **kwargs)

    def categories_first(self, categories):

        best_url = self.best_url % self.domain
        self.load(best_url)
        # session = Session(autocommit=True)


        category_eles = self.lr.xpaths('//ul[@id="zg_browseRoot"]/ul/li/a')
        for category_ele in category_eles:
            if category_ele.text.strip() in categories:
                url = self.wrapped_url(urlparse.urljoin(best_url, category_ele.attrib['href']))

                key = category_ele.text.strip()
                if self.session.query(Url).filter_by(url=url).count() < 1:
                    self.session.add(Url(url=url, type=URL_TYPE.BEST_SELL_CATEGORY, name=category_ele.text.strip(), key=key))
                    # session.commit()


    def run(self):
        while 1:
            try:
                _url_obj = self.input.get(timeout=30)
                url_obj = DictDot(_url_obj)
                if url_obj.type == URL_TYPE.PRODUCT_URL:
                    self.product(url_obj=url_obj)
                if url_obj.type == URL_TYPE.BEST_SELL_CATEGORY:
                    self.categories(url_obj=url_obj)
                if url_obj.type == URL_TYPE.BEST_SELL_CATEGORY_NEXT:
                    self.category_next(url_obj=url_obj)

            except Empty:
                logger.info('Empty')
            except:
                logger.error(traceback.format_exc())
