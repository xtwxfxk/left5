# -*- coding: utf-8 -*-
__author__ = 'xtwxfxk'

import os, time, csv, traceback, random
from urllib.parse import urljoin, quote, quote_plus
import logging
import logging.config
from lutils.lrequests import LRequests
from lutils.captcha import GsaCaptcha
import multiprocessing
from multiprocessing import Process, queues, Queue
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import requests
from bs4 import BeautifulSoup

from selenium import webdriver

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait

import undetected_chromedriver.v2 as uc


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

CAPTCHA_DIR = os.path.join(ROOT, 'tmp', 'captcha')
if not os.path.exists(CAPTCHA_DIR): os.makedirs(CAPTCHA_DIR)

list_queue = Queue() # ctx=multiprocessing.get_context()
product_queue = Queue()
record_queue = Queue()
csv_queue = Queue()

class SpiderAmazonBrowser():

    def __init__(self, list_queue, product_queue, profile_dir=None):

        self.list_queue = list_queue
        self.product_queue = product_queue
        self.gsa = GsaCaptcha()
        self.key_asins = {}

        options = uc.ChromeOptions()
        if profile_dir:
            options.add_argument('--user-data-dir=%s' % profile_dir)

        # options.add_experimental_option('prefs', {'intl.accept_languages': 'en,en_US'})
        # chrome_options = webdriver.ChromeOptions()
        # prefs = {"profile.managed_default_content_settings.images": 2}
        prefs = {}
        prefs["profile.default_content_settings"] = {"images": 2}
        prefs["profile.managed_default_content_settings"] = {"images": 2}

        options.add_experimental_option("prefs", prefs)
        options.add_argument('--start-maximized')
        options.add_argument('--blink-settings=imagesEnabled=false')
        self.browser = uc.Chrome(options=options)
        self.wait = WebDriverWait(self.browser, 120)

    def fetch_list(self, keyword):
        try:
            file = os.path.join(ASIN_DIR, '%s.txt' % keyword)
            if not os.path.exists(file):
                self.key_asins[keyword] = []

                self.browser.get('https://www.amazon.com/s?k=%s' % quote(keyword))

                while 1:
                    self.fetch_asin(keyword)
                    if not self.next_page():
                        break

            else:
                logger.info('pass keyword: %s' % keyword)
        except Exception as ex:
            logger.error(ex, exc_info=True)

        open(file, 'w', encoding='utf-8').write('\n'.join(self.key_asins[keyword]))

    def fetch_asin(self, keyword):

        product_eles = self.browser.find_elements(by=By.XPATH, value='//div[contains(@class, "s-result-list")]/div[contains(@data-component-type, "s-search-result")]')
        for product_ele in product_eles:
            logger.info('asin: %s' % product_ele.get_attribute('data-asin'))
            self.key_asins[keyword].append(product_ele.get_attribute('data-asin'))


    def next_page(self):
        try:
            next_ele = self.browser.find_element(by=By.XPATH, value='//div[contains(@class, "s-pagination-container")]//a[contains(@class, "s-pagination-next")]')
            if next_ele is None:
                return False
            else:
                next_url = urljoin(self.browser.current_url, next_ele.get_attribute('href'))
                logger.info('Load Page: %s' % next_url)
                # time.sleep(random.randint(2000, 3000) / 1000)
                self.browser.get(next_url)
                return True
        except NoSuchElementException as ex:
            return False
        except Exception as ex:
            logger.error(ex, exc_info=True)
            return False

    def do_list(self):
        while True:
            try:
                keyword = self.list_queue.get(timeout=5)
                file = os.path.join(ASIN_DIR, '%s.txt' % keyword)
                if not os.path.exists(file):
                    self.fetch_list(keyword)
                self.product_queue.put(keyword)
            except queues.Empty:
                logger.info('list empty')
                return
            except Exception as ex:
                logger.error(ex, exc_info=True)

    def fetch_products(self, keyword):
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
            self.browser.get('https://www.amazon.com/dp/%s' % asin)

            title_ele = self.browser.find_element(By.XPATH, '//span[@id="productTitle"]')
            title = title_ele.text.strip()

            brand = ''
            try:
                brand_ele = self.browser.find_element(By.XPATH, '//a[@id="bylineInfo"]')
                if brand_ele is not None:
                    text = brand_ele.text.strip().lower()
                    if text.startswith('visit'):
                        brand = text[9:-5].strip()
                    elif text.startswith('brand'):
                        brand = text[6:].strip()
            except NoSuchElementException as ex:
                logger.info('not brand %s' % asin)

            open(os.path.join(PRODUCTS_DIR, keyword, '%s.txt' % asin), 'w', encoding='utf-8').write('|||'.join([asin, brand, title]))
            record_queue.put('%s|||%s|||%s' % (keyword, asin, brand))
        except KeyboardInterrupt:
            return
        except Exception as ex:
            # open('xx.html', 'w', encoding='utf-8').write(str(self.lr.body))
            logger.error(ex, exc_info=True)

    def do_products(self):
        while True:
            try:
                keyword = self.product_queue.get(timeout=5)
                # time.sleep(random.randint(1000, 2000) / 1000)
                self.fetch_products(keyword)
            except queues.Empty:
                logger.info('products empty')
                time.sleep(5)
            except Exception as ex:
                logger.error(ex, exc_info=True)


class SpiderAmazon():

    def __init__(self, list_queue, product_queue, record_queue, csv_queue):

        self.list_queue = list_queue
        self.product_queue = product_queue
        self.record_queue = record_queue
        self.csv_queue = csv_queue

        self.lr = LRequests()
        self.gsa = GsaCaptcha()
        self.key_asins = {}


    def load_amazon(self, url):
        self.lr.load(url)
        # if(url.find('ref=nb_sb_noss') > -1):
        open('xx\\%s.html' % time.time(), 'w', encoding='utf-8').write(self.lr.body)

        while self.lr.body.find('Enter the characters you see below') > 0:
            try:
                logger.error("Captcha!!!")

                captcha_path = os.path.join(CAPTCHA_DIR, '%s.jpg' % time.time())
                self.lr.load_img(self.lr.xpath('//img[contains(@src, "captcha")]').get('src'))
                with open(captcha_path, 'wb') as f:
                    f.write(self.lr.body)
                code = self.gsa.decode(captcha_path)

                logger.info('Decode Captcha: %s' % code)
                amzn = self.lr.xpath('//input[@name="amzn"]').get('value')
                amzn_r = self.lr.xpath('//input[@name="amzn-r"]').get('value')

                captcha_url = 'https://www.amazon.com/errors/validateCaptcha?amzn=%s&amzn-r=%s&field-keywords=%s' % (quote_plus(amzn), quote_plus(amzn_r), code)
                # payload = {'amzn': amzn,
                #             'amzn-r': amzn_r,
                #             'field-keywords': code,}

                self.lr.load(captcha_url, method='GET') #, data=payload)
                # open('xxx\\%s.html' % time.time(), 'w', encoding='utf-8').write(self.lr.body)
                # self.lr.load(url)
            except Exception as ex:
                logger.error(ex, exc_info=True)


    def fetch_products(self, keyword):
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
            record_queue.put('%s|||%s|||%s' % (keyword, asin, brand))
        except KeyboardInterrupt:
            return
        except Exception as ex:
            # open('xx.html', 'w', encoding='utf-8').write(str(self.lr.body))
            logger.error(ex, exc_info=True)

    def fetch_uspto(self, keyword, brand, asin):
        uspth_path = os.path.join(USPTO_DIR, keyword)
        if not os.path.exists(uspth_path):
            os.makedirs(uspth_path)
        self.lr.load('https://tmsearch.uspto.gov/')
        search_ele = self.lr.xpath('//a[contains(@href, "searchss")]')
        if search_ele is not None:
            self.lr.load(urljoin(self.lr.current_url, search_ele.get('href')))
            # form = self.lr.get_forms()[0]
            # form = self.lr.getForms(urljoin(self.lr.current_url, search_ele.get('href')))[0]

            try:
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


    def fetch_trademarkia(self, keyword, brand, asin):
        trademarkia_path = os.path.join(TRADEMARKIA_DIR, keyword)
        if not os.path.exists(trademarkia_path):
            os.makedirs(trademarkia_path)

        try:
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


    def do_products(self):
        while True:
            try:
                keyword = self.product_queue.get(timeout=5)

                self.fetch_products(keyword)
            except queues.Empty:
                logger.info('products empty')
                time.sleep(5)
            except Exception as ex:
                logger.error(ex, exc_info=True)

    def do_records(self):
        while True:
            try:
                keyword, asin, brand = self.record_queue.get(timeout=5).split('|||')

                self.fetch_trademarkia(keyword, asin, brand)
                self.fetch_uspto(keyword, asin, brand)

                self.csv_queue.put('%s|||%s' % (keyword, asin))
            except queues.Empty:
                logger.info('records empty')
                time.sleep(5)
            except Exception as ex:
                logger.error(ex, exc_info=True)

    def do_csv(self):
        while True:
            try:
                keyword, asin = self.csv_queue.get(timeout=5).split('|||')

                self.output_csv(keyword, asin)
            except queues.Empty:
                logger.info('csv empty')
                time.sleep(5)
            except Exception as ex:
                logger.error(ex, exc_info=True)

    def output_csv(self, keyword, asin):

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
        if os.path.exists(csv_path):
            with open(csv_path, 'w', encoding='utf-8', newline="") as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow(fields)
                csvwriter.writerows(products)
        else:
            with open(csv_path, 'a', encoding='utf-8', newline="") as csvfile:
                csvwriter.writerows(products)


def do_keyword(keyword):
    try:
        sa = SpiderAmazon()
        sa.fetch_products(keyword)
        sa.fetch_trademarkia(keyword)
        sa.fetch_uspto(keyword)

        sa.output_csv(keyword)
    except Exception as ex:
        # traceback.print_exc()
        logger.error(ex, exc_info=True)

def do_list():
    try:
        sab = SpiderAmazonBrowser(list_queue, product_queue, 'D://profiles//amazon')
        sab.do_list()

    except Exception as ex:
        # traceback.print_exc()
        logger.error(ex, exc_info=True)

def do_product(p):
    try:
        sab = SpiderAmazonBrowser(list_queue, product_queue, p)
        sab.do_products()

    except Exception as ex:
        # traceback.print_exc()
        logger.error(ex, exc_info=True)

def start():
    # for file in os.listdir(KEYWORD_PATH):
    #     # print(open(os.path.join(KEYWORD_PATH, file)).readlines())
    #     keywords.extend([k.strip() for k in open(os.path.join(KEYWORD_PATH, file)).readlines() if k.strip()])
    # start_list()
    # start_asins()

    # sa.fetch_product('B09KWZXG2N')

    list_p = Process(target=do_list)
    list_p.start()

    product1_p = Process(target=do_product, args=(('D://profiles//amazon_product'),))
    product1_p.start()
    product2_p = Process(target=do_product, args=(('D://profiles//amazon_product1'),))
    product2_p.start()

    sa1 = SpiderAmazon(list_queue, product_queue, record_queue, csv_queue)
    record_p = Process(target=sa1.do_records)
    record_p.start()

    sa2 = SpiderAmazon(list_queue, product_queue, record_queue, csv_queue)
    csv_p = Process(target=sa2.do_csv)
    csv_p.start()


    # executor = ProcessPoolExecutor(max_workers=5)
    # executor.submit(do_list)

    # sa = SpiderAmazon(list_queue, product_queue, record_queue, csv_queue)
    # executor.submit(do_product, 'D://profiles//amazon_product')
    # executor.submit(do_product, 'D://profiles//amazon_product1')
    # executor.submit(sa.do_records)
    # executor.submit(sa.do_csv)


    for file in os.listdir(KEYWORD_PATH):
        try:
            for keyword in open(os.path.join(KEYWORD_PATH, file), 'r', encoding='utf-8').readlines():
                list_queue.put(keyword.strip())
        except Exception as ex:
            logger.error(ex, exc_info=True)

    list_p.join()
    product1_p.join()
    product2_p.join()
    record_p.join()
    csv_p.join()

# https://www.trademarkia.com/trademarks-search.aspx?tn=GreenLife
# https://tmsearch.uspto.gov/
if __name__ == '__main__':
    start()

