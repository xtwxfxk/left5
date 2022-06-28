# -*- coding: utf-8 -*-
__author__ = 'xtwxfxk'

import os, time, csv, traceback
from urllib.parse import urljoin, quote
import logging
import logging.config
from lutils.lrequests import LRequests
from concurrent.futures import ThreadPoolExecutor

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('verbose')

ROOT = os.getcwd()
KEYWORD_PATH = os.path.join(ROOT, 'keywords')

LOG_DIR = os.path.join(ROOT, 'logs')
if not os.path.exists(LOG_DIR): os.makedirs(LOG_DIR)

ASIN_DIR = os.path.join(ROOT, 'tmp', 'asin')
if not os.path.exists(ASIN_DIR): os.makedirs(ASIN_DIR)

PRODUCTS_DIR = os.path.join(ROOT, 'tmp', 'products')
if not os.path.exists(PRODUCTS_DIR): os.makedirs(PRODUCTS_DIR)

TRADEMARKIA_DIR = os.path.join(ROOT, 'tmp', 'trademarkia')
if not os.path.exists(TRADEMARKIA_DIR): os.makedirs(TRADEMARKIA_DIR)

USPTO_DIR = os.path.join(ROOT, 'tmp', 'uspto')
if not os.path.exists(USPTO_DIR): os.makedirs(USPTO_DIR)

CSV_DIR = os.path.join(ROOT, 'csv')
if not os.path.exists(CSV_DIR): os.makedirs(CSV_DIR)

class SpiderAmazon():

    def __init__(self, keyword):

        self.lr = LRequests()
        self.asins = []
        self.keyword = keyword

    def load_amazon(self, url):
        self.lr.load(url)
        if self.lr.body.find('Enter the characters you see below') > 0:
            logger.error("Captcha!!!")
            time.sleep(10)
            self.lr = LRequests()
            self.lr.load(url)

    def fetch_list(self):
        file = os.path.join(ASIN_DIR, '%s.txt' % self.keyword)
        if not os.path.exists(file):
            self.lr.load('https://www.amazon.com/s?k=%s' % quote(self.keyword))

            while 1:
                self.fetch_asin()
                if not self.next_page():
                    break

            open(file, 'w', encoding='utf-8').write('\n'.join(self.key_asins[keyword]))
        else:
            logger.info('pass keyword: %s' % keyword)

    def fetch_asin(self):
        product_eles = self.lr.xpaths('//div[contains(@class, "s-result-list")]/div[contains(@data-component-type, "s-search-result")]')
        for product_ele in product_eles:
            self.asins.append(product_ele.get('data-asin'))


    def next_page(self):
        next_ele = self.lr.xpath('//div[contains(@class, "s-pagination-container")]//a[contains(@aria-label, "next page")]')
        if next_ele is None:
            return False
        else:
            next_url = urljoin(self.lr.current_url, next_ele.get('href'))
            self.lr.load(next_url)
            return True

    def fetch_asins(self):
        if not os.path.exists(os.path.join(PRODUCTS_DIR, self.keyword)): os.makedirs(os.path.join(PRODUCTS_DIR, self.keyword))
        
        for asin in self.asins:
            try:
                if not os.path.exists(os.path.join(PRODUCTS_DIR, self.keyword, '%s.txt' % asin)):
                    self.fetch_product(asin)
                    self.fetch_trademarkia(asin)
                    self.fetch_uspto(asin)
                else:
                    logger.info('pass %s' % asin)
            except Exception as ex:
                logger.error(ex, exc_info=True)

    def fetch_product(self, asin):
        try:
            # self.lr.load('https://www.amazon.com/dp/%s' % asin)
            self.load_amazon('https://www.amazon.com/dp/%s' % asin)

            title_ele = self.lr.xpath('//span[@id="productTitle"]')
            title = ''.join(title_ele.itertext()).strip()

            manufacturer = ''
            detail_name_eles = self.lr.xpaths('//table[contains(@id, "productDetails")]//th')
            detail_value_eles = self.lr.xpaths('//table[contains(@id, "productDetails")]//td')

            if detail_name_eles is None or len(detail_name_eles) < 1:
                detail_name_eles = self.lr.xpaths('//div[contains(@id, "detailBullets_feature_div")]/ul[contains(@class, "detail-bullet-list")]//li/span/span[1]')
                detail_value_eles = self.lr.xpaths('//div[contains(@id, "detailBullets_feature_div")]/ul[contains(@class, "detail-bullet-list")]//li/span/span[2]')


            manufacturer_index = -1
            for i, detail_name_ele in enumerate(detail_name_eles):
                detail_text = ''.join(detail_name_ele.itertext()).strip().lower()

                if detail_text.find('manufacturer') > -1 and detail_text.find('by') < 1:
                    manufacturer_index = i
                    break

            if manufacturer_index > -1:
                manufacturer = ''.join(detail_value_eles[manufacturer_index].itertext()).strip().strip('\\n').strip('‎').strip()

            self.product_info = [asin, manufacturer, title]
        except Exception as ex:
            open('xx\\%s.html' % time.time(), 'w', encoding='utf-8').write(str(self.lr.body))
            logger.error(ex, exc_info=True)

    def fetch_uspto(self, asin):
        self.lr.load('https://tmsearch.uspto.gov/')
        search_ele = self.lr.xpath('//a[contains(@href, "searchss")]')
        if search_ele is not None:
            self.lr.load(urljoin(self.lr.current_url, search_ele.get('href')))

            try:
                asin, manufacturer, title = self.product_info
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

                    self.lr.load('https://tmsearch.uspto.gov/bin/showfield', method='POST', data=payload)

                    eles = self.lr.xpaths('//table[@id="searchResultTable"]//tr')
                    if eles is not None and len(eles) > 1:
                        logger.info('Manufacturer %s: %s' % (manufacturer, len(eles)))
                        self.uspto_count = len(eles)
                    else:
                        logger.info('Manufacturer %s: None' % manufacturer)
                        self.uspto_count = 0
                else:
                    logger.info('Pass Empty Manufacturer %s' % asin)
            except Exception as ex:
                logger.error(ex, exc_info=True)


    def fetch_trademarkia(self, asin):
        try:
            asin, manufacturer, title = self.product_info
            if manufacturer:
                self.lr.load('https://www.trademarkia.com/trademarks-search.aspx?tn=%s' % quote(manufacturer))
                eles = self.lr.xpaths('//table[contains(@class, "tablesaw")]//tr')
                if eles is not None and len(eles) > 1:
                    logger.info('Manufacturer %s: %s' % (manufacturer, len(eles)))
                    self.trademarkia_count = len(eles)
                else:
                    logger.info('Manufacturer %s: None' % manufacturer)
                    self.trademarkia_count = 0
            else:
                logger.info('Pass Empty Manufacturer %s' % asin)

        except Exception as ex:
            logger.error(ex, exc_info=True)

    def output_csv(self, keyword):
        product_dir = os.path.join(PRODUCTS_DIR, keyword)

        products = []
        for file in os.listdir(product_dir):
            asin, manufacturer, title = open(os.path.join(product_dir, file), 'r', encoding='utf-8').read().strip().split('|||')

            t_m = '否'
            t_dir = os.path.join(TRADEMARKIA_DIR, '%s.txt' % asin)
            if os.path.exists(t_dir):
                if int(open(t_dir).read().strip()) > 0:
                    t_m = '是'

            u_m = '否'
            u_dir = os.path.join(USPTO_DIR, '%s.txt' % asin)
            if os.path.exists(u_dir):
                if int(open(u_dir).read().strip()) > 0:
                    u_m = '是'

            products.append([title, asin, manufacturer, t_m, u_m])

        fields = ['标题', 'asin', '品牌', 'TRADEMARKIA', 'USPTO']
        csv_path = os.path.join(CSV_DIR, '%s.csv' % keyword)

        with open(csv_path, 'w', encoding='utf-8', newline="") as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(fields)
            csvwriter.writerows(products)

    def start(self):
        self.fetch_list()


def do_keyword(keyword):
    try:
        sa = SpiderAmazon(keyword)
        sa.start()
    except Exception as ex:
        traceback.print_exc()

def start():
    # for file in os.listdir(KEYWORD_PATH):
    #     # print(open(os.path.join(KEYWORD_PATH, file)).readlines())
    #     keywords.extend([k.strip() for k in open(os.path.join(KEYWORD_PATH, file)).readlines() if k.strip()])
    # start_list()
    # start_asins()

    # sa.fetch_product('B09KWZXG2N')


    executor = ThreadPoolExecutor(max_workers=5)

    for file in os.listdir(KEYWORD_PATH):
        for keyword in open(os.path.join(KEYWORD_PATH, file), 'r', encoding='utf-8').readlines():
            keyword = keyword.strip()
            if keyword:
                executor.submit(do_keyword, keyword)



if __name__ == '__main__':
    start()
