# -*- coding: utf-8 -*-
__author__ = 'xtwxfxk'

import logging, traceback
from urllib.parse import urlparse
from urllib.parse import urljoin
from sqlalchemy import update

from .base import AmazonBase
from .base.models import Url, URL_TYPE, Session

logger = logging.getLogger('verbose')



def category(method):
    def wrapped(self, **kwargs):
        assert 'url_obj' in kwargs
        session = Session(autocommit=True)

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
                url = self.wrapped_url(urljoin(self.lr.current_url, category_ele.attrib['href']))
                text = category_ele.text.strip()

                key = '%s@@%s' % (url_obj.key, text)

                if session.query(Url).filter_by(key=key).count() < 1:
                    logger.info('Add Category: %s: %s' % (text, url))
                    urls.append(Url(url=url, type=URL_TYPE.BEST_SELL_CATEGORY, name=text, key=key))
                    # session.commit()

        session.bulk_save_objects(urls)
    return wrapped

def next_page(method):
    def wrapped(self, **kwargs):
        session = Session(autocommit=True)

        method(self, **kwargs)

        urls = []
        ele = self.lr.xpath('//li[@class="a-last"]/a'):
        page_url = urljoin(self.lr.current_url, ele.attrib['href'].strip())

        id = page_url.split('/ref', 1)[0].rsplit('/', 1)[-1]
        index = page_url.split('&pg=', 1)[-1]
        key = '%s_%s' % (id, index)

        if session.query(Url).filter_by(key=key).count() < 1:
            logger.info('Add Category Next: %s' % page_url)
            urls.append(Url(url=page_url, type=URL_TYPE.BEST_SELL_CATEGORY_NEXT, key=key))
                # session.commit()
        session.bulk_save_objects(urls)

    return wrapped

def product_url(method):
    def wrapped(self, **kwargs):
        session = Session(autocommit=True)

        method(self, **kwargs)

        urls = []
        product_eles = self.lr.xpaths('//span[contains(@class, "zg-item")]/a')
        for ele in product_eles:
            product_url = urljoin(self.lr.current_url, ele.attrib['href'].strip())
            asin = product_url.split('/dp/', 1)[1].split('/', 1)[0]

            u = urlparse(product_url)
            pu = '%s://%s/db/%s' % (u.scheme, u.netloc, asin)
            if session.query(Url).filter_by(key=asin).count() < 1:
                logger.info('Add Product: %s' % asin)
                urls.append(Url(url=product_url, type=URL_TYPE.PRODUCT_URL, key=asin))
                # session.commit()

        session.bulk_save_objects(urls)

    return wrapped

def url_over(method):
    def wrapped(self, **kwargs):
        session = Session(autocommit=True)

        method(self, **kwargs)

        url_obj = kwargs.get('url_obj')

        # url_obj.has_crawled = True
        # session.commit()

        session.query(Url).filter_by(id=url_obj.id).update({Url.has_crawled: True})
        # session.commit()

    return wrapped

class BestSell(AmazonBase):

    best_url = 'https://www.amazon.com/Best-Sellers/zgbs'

    def __init__(self, **kwargs):
        super(BestSell, self).__init__(**kwargs)


    @category
    @next_page
    @product_url
    @url_over
    def categories(self, url_obj=None, **kwargs):
        self.load(url_obj.url)

    @product_url
    @url_over
    def category_next(self, url_obj=None, **kwargs):
        self.load(url_obj.url)

    @url_over
    def product(self, url_obj=None, **kwargs):
        super(BestSell, self).product(asin=url_obj.key, **kwargs)

    def categories_first(self, categories):
        self.load(self.best_url)
        session = Session(autocommit=True)

        category_eles = self.lr.xpaths('//ul[@id="zg_browseRoot"]/ul/li/a')
        for category_ele in category_eles:
            if category_ele.text.strip() in categories:
                url = self.wrapped_url(urljoin(self.best_url, category_ele.attrib['href']))

                key = category_ele.text.strip()
                if session.query(Url).filter_by(url=url).count() < 1:
                    session.add(Url(url=url, type=URL_TYPE.BEST_SELL_CATEGORY, name=category_ele.text.strip(), key=key))
                    # session.commit()



    def categories_first2(self, categories):
        self.load(self.best_url)

        category_eles = self.lr.xpaths('//ul[@id="zg_browseRoot"]/ul/li/a')
        for category_ele in category_eles:
            if category_ele.text.strip() in categories:
                url = self.wrapped_url(urljoin(self.best_url, category_ele.attrib['href']))

                key = category_ele.text.strip()
                if session.query(Url).filter_by(url=url).count() < 1:
                    session.add(Url(url=url, type=URL_TYPE.BEST_SELL_CATEGORY, name=category_ele.text.strip(), key=key))
                    session.commit()


        while session.query(Url).filter_by(type=URL_TYPE.BEST_SELL_CATEGORY, has_crawled=False).count() > 0:
            for url_obj in session.query(Url).filter_by(type=URL_TYPE.BEST_SELL_CATEGORY, has_crawled=False):
                self.load(url_obj.url)

                # sub category
                p_categories = url_obj.key.split('@@')
                floor_ul = '/'.join(['ul' for i in range(len(p_categories))])

                category_xpaths = '//ul[@id="zg_browseRoot"]/ul/li/a'
                if floor_ul: category_xpaths = '//ul[@id="zg_browseRoot"]/ul/%s/li/a' % floor_ul

                category_eles = self.lr.xpaths(category_xpaths)
                if category_eles is not None and len(category_eles) > 0:
                    for category_ele in category_eles:
                        url = self.wrapped_url(urljoin(self.lr.current_url, category_ele.attrib['href']))
                        text = category_ele.text.strip()

                        key = '%s@@%s' % (url_obj.key, text)

                        if session.query(Url).filter_by(key=key).count() < 1:
                            session.add(Url(url=url, type=URL_TYPE.BEST_SELL_CATEGORY, name=text, key=key))
                            session.commit()

                # enc sub category

                # pager
                for ele in self.lr.xpaths('//div[@id="zg_paginationWrapper"]//a'):
                    page_url = urljoin(self.lr.current_url, ele.attrib['href'].strip())
                    session.add(Url(url=page_url, type=URL_TYPE.BEST_SELL_CATEGORY_NEXT))
                    session.commit()

                # end pager

                # product
                product_eles = self.lr.xpaths('//div[@class="zg_itemImageImmersion"]/a')
                for ele in product_eles:
                    product_url = urljoin(self.lr.current_url, ele.attrib['href'].strip())
                    asin = product_url.split('/dp/', 1)[1].split('/', 1)[0]

                    if session.query(Url).filter_by(key=asin).count() < 1:
                        session.add(Url(url=product_url, type=URL_TYPE.PRODUCT_URL, key=asin))
                        session.commit()
                # end product

                url_obj.has_crawled = True
                session.commit()

            session.commit()

        while session.query(Url).filter_by(type=URL_TYPE.BEST_SELL_CATEGORY_NEXT, has_crawled=False).count() > 0:
            for url_obj in session.query(Url).filter_by(type=URL_TYPE.BEST_SELL_CATEGORY_NEXT, has_crawled=False):
                self.load(url_obj.url)

                # product
                product_eles = self.lr.xpaths('//div[@class="zg_itemImageImmersion"]/a')
                for ele in product_eles:
                    product_url = urljoin(self.lr.current_url, ele.attrib['href'].strip())
                    asin = product_url.split('/dp/', 1)[1].split('/', 1)[0]

                    if session.query(Url).filter_by(key=asin).count() < 1:
                        session.add(Url(url=product_url, type=URL_TYPE.PRODUCT_URL, key=asin))
                        session.commit()
                # end product

                url_obj.has_crawled = True
                session.commit()
