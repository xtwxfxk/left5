# -*- coding: utf-8 -*-
__author__ = 'xtwxfxk'

import os, time, csv
from urllib.parse import urljoin, quote
import logging
import logging.config
from lutils.lrequests import LRequests


logging.config.fileConfig('logging.conf')
logger = logging.getLogger('verbose')

ROOT = os.getcwd()
KEYWORD_PATH = os.path.join(ROOT, 'keywords')

LOG_DIR = os.path.join(ROOT, 'logs')
if not os.path.exists(LOG_DIR): os.makedirs(LOG_DIR)

ASIN_DIR = os.path.join(ROOT, 'asin')
if not os.path.exists(ASIN_DIR): os.makedirs(ASIN_DIR)

PRODUCTS_DIR = os.path.join(ROOT, 'products')
if not os.path.exists(PRODUCTS_DIR): os.makedirs(PRODUCTS_DIR)

TRADEMARKIA_DIR = os.path.join(ROOT, 'trademarkia')
if not os.path.exists(TRADEMARKIA_DIR): os.makedirs(TRADEMARKIA_DIR)

USPTO_DIR = os.path.join(ROOT, 'uspto')
if not os.path.exists(USPTO_DIR): os.makedirs(USPTO_DIR)


class SpiderAmazon():

    def __init__(self, keywords=[]):
        self.keywords = keywords
        self.lr = LRequests()
        self.key_asins = {}


    def fetch_list(self):
        for keyword in self.keywords:
            self.key_asins[keyword] = []

            self.lr.load('https://www.amazon.com/s?k=%s' % keyword)

            while 1:
                self.fetch_asin(keyword)
                if not self.next_page():
                    break

            open(os.path.join(ASIN_DIR, '%s.txt' % keyword), 'w').write('\n'.join(self.key_asins[keyword]))

    def fetch_asin(self, keyword):
        product_eles = self.lr.xpaths('//div[contains(@class, "s-result-list")]/div[contains(@data-component-type, "s-search-result")]')
        for product_ele in product_eles:
            print(product_ele.get('data-asin'))
            self.key_asins[keyword].append(product_ele.get('data-asin'))


    def next_page(self):
        next_ele = self.lr.xpath('//div[contains(@class, "s-pagination-container")]//a[contains(@aria-label, "next page")]')
        if next_ele is None:
            return False
        else:
            next_url = urljoin(self.lr.current_url, next_ele.get('href'))
            self.lr.load(next_url)
            return True

    def fetch_asins(self):
        for file in os.listdir(ASIN_DIR):
            keyword = file[:-4]
            if not os.path.exists(os.path.join(PRODUCTS_DIR, keyword)): os.makedirs(os.path.join(PRODUCTS_DIR, keyword))
            for asin in open(os.path.join(ASIN_DIR, file)).readlines():
                asin = asin.strip()
                if not os.path.exists(os.path.join(PRODUCTS_DIR, keyword, '%s.txt' % asin)):
                    self.fetch_product(keyword, asin)
                else:
                    logger.info('pass %s' % asin)

    def fetch_product(self, keyword, asin):
        self.lr.load('https://www.amazon.com/dp/%s' % asin)

        title_ele = self.lr.xpath('//span[@id="productTitle"]')
        title = ''.join(title_ele.itertext()).strip()

        detail_name_eles = self.lr.xpaths('//table[contains(@id, "productDetails")]//th')
        detail_value_eles = self.lr.xpaths('//table[contains(@id, "productDetails")]//td')

        manufacturer_index = -1
        for i, detail_name_ele in enumerate(detail_name_eles):
            detail_text = ''.join(detail_name_ele.itertext()).strip().lower()

            if detail_text == 'manufacturer':
                manufacturer_index = i
                break

        manufacturer = ''
        if manufacturer_index > -1:
            manufacturer = ''.join(detail_value_eles[manufacturer_index].itertext()).strip().strip('‎')

        open(os.path.join(PRODUCTS_DIR, keyword, '%s.txt' % asin), 'w').write('|||'.join([asin, manufacturer, title]))

    def fetch_uspto(self):
        self.lr.load('https://tmsearch.uspto.gov/')
        search_ele = self.lr.xpath('//a[contains(@href, "searchss")]')
        if search_ele is not None:
            self.lr.load(urljoin(self.lr.current_url, search_ele.get('href')))
            # form = self.lr.get_forms()[0]
            # form = self.lr.getForms(urljoin(self.lr.current_url, search_ele.get('href')))[0]

            for keyword in os.listdir(PRODUCTS_DIR):
                key_path = os.path.join(PRODUCTS_DIR, keyword)
                if os.path.isdir(key_path):
                    for file in os.listdir(key_path):
                        asin, manufacturer, title = open(os.path.join(key_path, file)).read().strip().split('|||')
                        if manufacturer:
                            state_ele = self.lr.xpath('//input[@name="state"]')
                            state = state_ele.get('value')

                            payload = {'f': 'toc', 
                            'state': state,
                            'p_search': 'search',
                            'p_s_All': '',
                            'p_s_ALL': manufacturer,
                            'a_default': 'search',
                            'a_search': 'Submit',}
                            # self.lr.post('https://tmsearch.uspto.gov/bin/showfield', data=payload)

                            self.lr.load('https://tmsearch.uspto.gov/bin/showfield', method='POST', data=payload)

                            # self.lr.load('https://tmsearch.uspto.gov/bin/showfield?f=toc&state=%s&p_search=searchss&p_L=50&BackReference=&p_plural=yes&p_s_PARA1=&p_tagrepl%%7E%%3A=PARA1%%24LD&expr=PARA1+AND+PARA2&p_s_PARA2=%s&p_tagrepl%%7E%%3A=PARA2%%24COMB&p_op_ALL=AND&a_default=search&a_search=Submit+Query&a_search=Submit+Query' % (quote(state), quote(manufacturer)))
                            # form['p_s_PARA2'] = manufacturer
                            # self.lr.load(form.click())
                            eles = self.lr.xpaths('//table[@id="searchResultTable"]//tr')
                            print(len(eles))
                            open('xx.html', 'w').write(str(self.lr.body))
                            if eles is not None and len(eles) > 1:
                                logger.info('Manufacturer %s: %s' % (manufacturer, len(eles)))
                                open(os.path.join(USPTO_DIR, '%s.txt' % asin), 'w').write(str(len(eles)))
                            else:
                                logger.info('Manufacturer %s: None' % manufacturer)
                                open(os.path.join(USPTO_DIR, '%s.txt' % asin), 'w').write("0")
                        else:
                            logger.info('Pass Empty Manufacturer %s' % asin)


    def fetch_trademarkia(self):
        for keyword in os.listdir(PRODUCTS_DIR):
            key_path = os.path.join(PRODUCTS_DIR, keyword)
            if os.path.isdir(key_path):
                for file in os.listdir(key_path):
                    asin, manufacturer, title = open(os.path.join(key_path, file)).read().strip().split('|||')

                    if manufacturer:
                        self.lr.load('https://www.trademarkia.com/trademarks-search.aspx?tn=%s' % quote(manufacturer))
                        eles = self.lr.xpaths('//table[contains(@class, "tablesaw")]//tr')
                        if eles is not None and len(eles) > 1:
                            logger.info('Manufacturer %s: %s' % (manufacturer, len(eles)))
                            open(os.path.join(TRADEMARKIA_DIR, '%s.txt' % asin), 'w').write(str(len(eles)))
                        else:
                            logger.info('Manufacturer %s: None' % manufacturer)
                            open(os.path.join(TRADEMARKIA_DIR, '%s.txt' % asin), 'w').write("0")
                    else:
                        logger.info('Pass Empty Manufacturer %s' % asin)


def start_list():
    keywords = []
    for file in os.listdir(KEYWORD_PATH):
        # print(open(os.path.join(KEYWORD_PATH, file)).readlines())
        keywords.extend([k.strip() for k in open(os.path.join(KEYWORD_PATH, file)).readlines() if k.strip()])

    sa = SpiderAmazon(keywords)
    sa.fetch_list()

def start_asins():

    sa = SpiderAmazon()
    sa.fetch_asins()

def start():
    # start_list(keywords)
    # start_asins()


    # sa.fetch_product('B09KWZXG2N')

    sa = SpiderAmazon()
    # sa.fetch_trademarkia()
    sa.fetch_uspto()



if __name__ == '__main__':
    start()
