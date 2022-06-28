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

    def __init__(self):

        self.lr = LRequests()
        self.key_asins = {}

    def load_amazon(self, url):
        self.lr.load(url)

        if self.lr.body.find('Enter the characters you see below') > 0:
            logger.error("Captcha!!!")
            time.sleep(10)
            self.lr = LRequests()
            self.lr.load(url)

    def fetch_list(self, keyword):

        file = os.path.join(ASIN_DIR, '%s.txt' % keyword)
        if not os.path.exists(file):
            self.key_asins[keyword] = []

            self.lr.load('https://www.amazon.com/s?k=%s' % quote(keyword))

            while 1:
                self.fetch_asin(keyword)
                if not self.next_page():
                    break

            open(file, 'w', encoding='utf-8').write('\n'.join(self.key_asins[keyword]))
        else:
            logger.info('pass keyword: %s' % keyword)

    def fetch_asin(self, keyword):
        product_eles = self.lr.xpaths('//div[contains(@class, "s-result-list")]/div[contains(@data-component-type, "s-search-result")]')
        for product_ele in product_eles:
            self.key_asins[keyword].append(product_ele.get('data-asin'))


    def next_page(self):
        next_ele = self.lr.xpath('//div[contains(@class, "s-pagination-container")]//a[contains(@aria-label, "next page")]')
        if next_ele is None:
            return False
        else:
            next_url = urljoin(self.lr.current_url, next_ele.get('href'))
            self.lr.load(next_url)
            return True

    def fetch_asins(self, keyword):
        if not os.path.exists(os.path.join(PRODUCTS_DIR, keyword)): os.makedirs(os.path.join(PRODUCTS_DIR, keyword))
        for asin in open(os.path.join(ASIN_DIR, '%s.txt' % keyword), 'r', encoding='utf-8').readlines():
            try:
                asin = asin.strip()
                if not os.path.exists(os.path.join(PRODUCTS_DIR, keyword, '%s.txt' % asin)):
                    self.fetch_product(keyword, asin)
                else:
                    logger.info('pass %s' % asin)
            except KeyboardInterrupt:
                return
            except Exception as ex:
                logger.error(ex, exc_info=True)

    def fetch_product(self, keyword, asin):
        try:
            # self.lr.load('https://www.amazon.com/dp/%s' % asin)
            self.load_amazon('https://www.amazon.com/dp/%s' % asin)

            title_ele = self.lr.xpath('//span[@id="productTitle"]')
            title = ''.join(title_ele.itertext()).strip()

            brand = ''
            brand_ele = self.lr.xpath('//a[@id="bylineInfo"]')
            if brand_ele is not None:
                text = brand_ele.text.strip().lower()
                if text.startswith('visit'):
                    brand = text[9:-5].strip()
                elif text.startswith('brand'):
                    brand = text[6:].strip()

            open(os.path.join(PRODUCTS_DIR, keyword, '%s.txt' % asin), 'w', encoding='utf-8').write('|||'.join([asin, brand, title]))
        except KeyboardInterrupt:
            return
        except Exception as ex:
            open('xx.html', 'w', encoding='utf-8').write(str(self.lr.body))
            logger.error(ex, exc_info=True)

    def fetch_uspto(self, keyword):
        uspth_path = os.path.join(USPTO_DIR, keyword)
        if not os.path.exists(uspth_path):
            os.makedirs(uspth_path)
        self.lr.load('https://tmsearch.uspto.gov/')
        search_ele = self.lr.xpath('//a[contains(@href, "searchss")]')
        if search_ele is not None:
            self.lr.load(urljoin(self.lr.current_url, search_ele.get('href')))
            # form = self.lr.get_forms()[0]
            # form = self.lr.getForms(urljoin(self.lr.current_url, search_ele.get('href')))[0]

            key_path = os.path.join(PRODUCTS_DIR, keyword)
            if os.path.isdir(key_path):
                for file in os.listdir(key_path):
                    try:
                        asin, brand, title = open(os.path.join(key_path, file), 'r', encoding='utf-8').read().strip().split('|||')
                        uspto_file = os.path.join(uspth_path, '%s.txt' % asin)
                        if not os.path.exists(uspto_file):
                            if brand:
                                state_ele = self.lr.xpath('//input[@name="state"]')
                                state = state_ele.get('value')

                                payload = {'f': 'toc', 
                                'state': state,
                                'p_search': 'search',
                                'p_s_All': '',
                                'p_s_ALL': brand,
                                'a_default': 'search',
                                'a_search': 'Submit',}

                                self.lr.load('https://tmsearch.uspto.gov/bin/showfield', method='POST', data=payload)

                                eles = self.lr.xpaths('//table[@id="searchResultTable"]//tr')
                                if eles is not None and len(eles) > 1:
                                    logger.info('Brand %s: %s' % (brand, len(eles)))
                                    open(uspto_file, 'w', encoding='utf-8').write(str(len(eles)))
                                else:
                                    logger.info('Brand %s: None' % brand)
                                    open(uspto_file, 'w', encoding='utf-8').write("0")
                            else:
                                logger.info('Pass Empty Brand %s' % asin)
                        else:
                            logger.info('Pass Empty Uspto %s' % asin)
                    except KeyboardInterrupt:
                        return
                    except Exception as ex:
                        logger.error(ex, exc_info=True)


    def fetch_trademarkia(self, keyword):
        trademarkia_path = os.path.join(TRADEMARKIA_DIR, keyword)
        if not os.path.exists(trademarkia_path):
            os.makedirs(trademarkia_path)
        key_path = os.path.join(PRODUCTS_DIR, keyword)
        if os.path.isdir(key_path):
            for file in os.listdir(key_path):
                try:
                    asin, brand, title = open(os.path.join(key_path, file), 'r', encoding='utf-8').read().strip().split('|||')
                    trademarkia_file = os.path.join(trademarkia_path, '%s.txt' % asin)
                    if not os.path.exists(trademarkia_file):
                        if brand:
                            self.lr.load('https://www.trademarkia.com/trademarks-search.aspx?tn=%s' % quote(brand))
                            eles = self.lr.xpaths('//table[contains(@class, "tablesaw")]//tr')
                            if eles is not None and len(eles) > 1:
                                logger.info('Brand %s: %s' % (brand, len(eles)))
                                open(trademarkia_file, 'w', encoding='utf-8').write(str(len(eles)))
                            else:
                                logger.info('Brand %s: None' % brand)
                                open(trademarkia_file, 'w', encoding='utf-8').write("0")
                        else:
                            logger.info('Pass Empty Brand %s' % asin)
                    else:
                        logger.info('Pass Trademarkia %s' % asin)
                except KeyboardInterrupt:
                    return
                except Exception as ex:
                    logger.error(ex, exc_info=True)

    def output_csv(self, keyword):
        product_dir = os.path.join(PRODUCTS_DIR, keyword)

        products = []
        for file in os.listdir(product_dir):
            asin, brand, title = open(os.path.join(product_dir, file), 'r', encoding='utf-8').read().strip().split('|||')

            t_m = '否'
            t_dir = os.path.join(TRADEMARKIA_DIR, keyword, '%s.txt' % asin)
            if os.path.exists(t_dir):
                if int(open(t_dir).read().strip()) > 0:
                    t_m = '是'

            u_m = '否'
            u_dir = os.path.join(USPTO_DIR, keyword, '%s.txt' % asin)
            if os.path.exists(u_dir):
                if int(open(u_dir).read().strip()) > 0:
                    u_m = '是'

            products.append([title, asin, brand, t_m, u_m])

        fields = ['标题', 'asin', '品牌', 'TRADEMARKIA', 'USPTO']
        csv_path = os.path.join(CSV_DIR, '%s.csv' % keyword)

        with open(csv_path, 'w', encoding='utf-8', newline="") as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(fields)
            csvwriter.writerows(products)


def do_keyword(keyword):
    try:
        sa = SpiderAmazon()
        sa.fetch_list(keyword)
        sa.fetch_asins(keyword)
        sa.fetch_trademarkia(keyword)
        sa.fetch_uspto(keyword)

        sa.output_csv(keyword)
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


# https://www.trademarkia.com/trademarks-search.aspx?tn=GreenLife
# https://tmsearch.uspto.gov/
if __name__ == '__main__':
    start()
