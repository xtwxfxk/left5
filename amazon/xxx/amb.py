# -*- coding: utf-8 -*-
__author__ = 'xtwxfxk'

import os, time, csv, traceback, queue
from urllib.parse import urljoin, quote, quote_plus
import logging
import logging.config
from lutils.lrequests import LRequests
from lutils.captcha import GsaCaptcha
from concurrent.futures import ThreadPoolExecutor
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


class SpiderAmazon():

    def __init__(self, q, profile_dir=None):

        self.lr = LRequests()
        self.gsa = GsaCaptcha()
        self.key_asins = {}

        self.q = q

        options = uc.ChromeOptions()
        if profile_dir is not None:
            options.add_argument('--user-data-dir=%s' % profile_dir)

        prefs = {}
        # prefs["profile.default_content_settings"] = {"images": 2}
        # prefs["profile.managed_default_content_settings"] = {"images": 2}
        prefs["intl.accept_languages"] = 'en,en_US'

        options.add_experimental_option("prefs", prefs)
        options.add_argument('--start-maximized')
        options.add_argument('--blink-settings=imagesEnabled=false')
        options.add_argument('--lang=en')
        
        self.browser = uc.Chrome(options=options)
        self.wait = WebDriverWait(self.browser, 120)

    def load_amazon(self, url):
        logger.info('load url %s' % url)
        self.browser.get(url)

        # while self.lr.body.find('Enter the characters you see below') > 0:
        #     try:
        #         logger.error("Captcha!!!")

        #         captcha_path = os.path.join(CAPTCHA_DIR, '%s.jpg' % time.time())
        #         self.lr.load_img(self.lr.xpath('//img[contains(@src, "captcha")]').get('src'))
        #         with open(captcha_path, 'wb') as f:
        #             f.write(self.lr.body)
        #         code = self.gsa.decode(captcha_path)

        #         logger.info('Decode Captcha: %s' % code)
        #         amzn = self.lr.xpath('//input[@name="amzn"]').get('value')
        #         amzn_r = self.lr.xpath('//input[@name="amzn-r"]').get('value')

        #         captcha_url = 'https://www.amazon.com/errors/validateCaptcha?amzn=%s&amzn-r=%s&field-keywords=%s' % (quote_plus(amzn), quote_plus(amzn_r), code)
        #         # payload = {'amzn': amzn,
        #         #             'amzn-r': amzn_r,
        #         #             'field-keywords': code,}

        #         self.lr.load(captcha_url, method='GET') #, data=payload)
        #         # open('xxx\\%s.html' % time.time(), 'w', encoding='utf-8').write(self.lr.body)
        #         # self.lr.load(url)
        #     except Exception as ex:
        #         logger.error(ex, exc_info=True)



    def fetch_list(self, keyword):

        file = os.path.join(ASIN_DIR, '%s.txt' % keyword)
        if not os.path.exists(file):
            self.key_asins[keyword] = []

            self.load_amazon('https://www.amazon.com/s?k=%s' % quote(keyword))

            while 1:
                self.fetch_asin(keyword)
                if not self.next_page():
                    break

            if len(self.key_asins[keyword]) > 0:
                open(file, 'w', encoding='utf-8').write('\n'.join(self.key_asins[keyword]))
            else:
                logger.info("empty asin: %s" % keyword)
        else:
            logger.info('pass keyword: %s' % keyword)

    def fetch_asin(self, keyword):
        product_eles = self.browser.find_elements_by_xpath('//div[contains(@class, "s-result-list")]/div[contains(@data-component-type, "s-search-result")]')
        for product_ele in product_eles:
            logger.info('asin: %s' % product_ele.get_attribute('data-asin'))
            self.key_asins[keyword].append(product_ele.get_attribute('data-asin'))


    def next_page(self):
        next_ele = self.browser.find_element_by_xpath('//div[contains(@class, "s-pagination-container")]//a[contains(@aria-label, "next page")]')
        if next_ele is None:
            return False
        else:
            next_ele.click()
            return True

    def fetch_products(self, keyword):
        asins_file = os.path.join(ASIN_DIR, '%s.txt' % keyword)
        if os.path.exists(asins_file):
            if not os.path.exists(os.path.join(PRODUCTS_DIR, keyword)): os.makedirs(os.path.join(PRODUCTS_DIR, keyword))
            for asin in open(asins_file, 'r', encoding='utf-8').readlines():
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

            title_ele = self.browser.find_element_by_xpath('//span[@id="productTitle"]')
            title = title_ele.text.strip()

            brand = ''
            try:
                brand_ele = self.browser.find_element_by_xpath('//a[@id="bylineInfo"]')
                if brand_ele is not None:
                    text = brand_ele.text.strip().lower()
                    if text.startswith('visit'):
                        brand = text[9:-5].strip()
                    elif text.startswith('brand'):
                        brand = text[6:].strip()
            except NoSuchElementException as ex:
                logger.info('not brand %s' % asin)

            open(os.path.join(PRODUCTS_DIR, keyword, '%s.txt' % asin), 'w', encoding='utf-8').write('|||'.join([asin, brand, title]))
        except KeyboardInterrupt:
            return
        except Exception as ex:
            # open('xx.html', 'w', encoding='utf-8').write(str(self.lr.body))
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

        if os.path.exists(product_dir):
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

    def do(self):
        try:
            while 1:
                try:
                    keyword = self.q.get(timeout=5)
                    self.fetch_list(keyword)
                    self.fetch_products(keyword)
                    self.fetch_trademarkia(keyword)
                    self.fetch_uspto(keyword)

                    self.output_csv(keyword)
                except queue.Empty:
                    logger.info('Empty')
                    time.sleep(5)
                except Exception as ex:
                    logger.error(ex, exc_info=True)

        except Exception as ex:
            logger.error(ex, exc_info=True)



def start():
    # for file in os.listdir(KEYWORD_PATH):
    #     # print(open(os.path.join(KEYWORD_PATH, file)).readlines())
    #     keywords.extend([k.strip() for k in open(os.path.join(KEYWORD_PATH, file)).readlines() if k.strip()])
    # start_list()
    # start_asins()

    # sa.fetch_product('B09KWZXG2N')

    try:
        q = queue.Queue(10)
        thread_num = 3

        executor = ThreadPoolExecutor(max_workers=thread_num)

        for i in range(thread_num):
            executor.submit(SpiderAmazon(q, 'D:\\profiles\\amazon%s' % i).do)

        for file in os.listdir(KEYWORD_PATH):
            try:
                for i, keyword in enumerate(open(os.path.join(KEYWORD_PATH, file), 'r', encoding='utf-8').readlines()):
                    keyword = keyword.strip()
                    if keyword:
                        q.put(keyword)
            except Exception as ex:
                logger.error(ex, exc_info=True)
    except Exception as ex:
        logger.error(ex, exc_info=True)

# https://www.trademarkia.com/trademarks-search.aspx?tn=GreenLife
# https://tmsearch.uspto.gov/
if __name__ == '__main__':
    start()

    # gsa = GsaCaptcha()
    # print(gsa.decode('D:\\code\\python\\left5\\amazon\\xxx\\tmp\\captcha\\Captcha_fbcjbbjtal.jpg'))

    # lr = LRequests()
    # r = lr.load_img('https://images-na.ssl-images-amazon.com/captcha/rhnrlggh/Captcha_rsoyrzxybz.jpg')

    # with open('D:\\code\\python\\left5\\amazon\\xxx\\tmp\\captcha\\xxx.jpg', 'wb') as f:
    #     # shutil.copyfileobj(r, f)
    #     f.write(lr.body)
