# -*- coding: utf-8 -*-
__author__ = 'xtwxfxk'

import os, time, csv, traceback, httplib2, re
from urllib.parse import urljoin, quote, quote_plus
import logging
import logging.config
from lutils.captcha import GsaCaptcha
from lutils.lrequests import LRequests
from concurrent.futures import ThreadPoolExecutor
from lxml import html
from bs4 import BeautifulSoup

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

exclude_cookie = ['domain', 'path', 'secure', 'version', 'max-age', 'expires']

class SpiderAmazon():

    def __init__(self):

        self.lr = LRequests()
        self.h = httplib2.Http(".cache")

        self.gsa = GsaCaptcha()
        self.key_asins = {}

        self.headers = {
            # ':authority': 'www.amazon.com',
            # ':method': 'GET',
            # ':path': '/s?k=Wallets',
            # ':scheme': 'https',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en;q=0.9',
            'sec-ch-ua': '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36',
        }
        self.cookies = {}

    def set_body(self, body, resp_headers):
        if(isinstance(body, bytes)):
            body = body.decode('utf-8')
        self.current_url = resp_headers['content-location']
        self.body = body
        self.tree = html.fromstring(str(BeautifulSoup(self.body, 'lxml')))

    def xpath(self, xpath):
        eles = self.tree.xpath(xpath)
        if eles and len(eles) > 0:
            return eles[0]
        return None

    def xpaths(self, xpath):
        return self.tree.xpath(xpath)

    def load_cookies(self, resp_headers):
        if 'set-cookie' in resp_headers:
            cookies_str = resp_headers['set-cookie']
            for cookie in re.split(';|,', cookies_str):
                cookie = cookie.strip().lower()
                if any([True if not cookie.startswith(e) and cookie.find('=') > 0 else False for e in exclude_cookie]):
                    name, value = cookie.split('=', 1)
                    self.cookies[name] = value

        if len(self.cookies.keys()) > 0:
            cookies = []
            for k, v in self.cookies.items():
                cookies.append('%s=%s' % (k, v))
            # logger.info('update cookies: %s' % '; '.join(cookies))
            self.headers['cookie'] = '; '.join(cookies)

    def load_amazon(self, url):
        # self.lr.load(url)
        time.sleep(1)
        logger.info('load url: %s' % url)
        (resp_headers, body) = self.h.request(url, method='GET', headers=self.headers)
        self.set_body(body, resp_headers)

        self.load_cookies(resp_headers)
        
        # if(url.find('ref=nb_sb_noss') > -1):
        #     open('xxx\\%s.html' % time.time(), 'w', encoding='utf-8').write(self.lr.body)

        # if self.lr.body.find('Something went wrong on our end') > 0:
        #     forms = BeautifulSoup(self.lr.body).find_all('form')
        #     for f in forms:
        #         print('=======-----')
        #         print('1111111 %s' % f.attrs.get('action'))
        #         for input_tag in f.find_all("input"):
        #             print('%s - %s' % (input_tag.attrs.get('name'), input_tag.attrs.get('value')))
        #         print('2222222 %s' % f.attrs.get('action'))
        #         for input_tag in f.find_all("select"):
        #             print('%s - %s' % (input_tag.attrs.get('name'), input_tag.attrs.get('value')))

        #     self.lr.load('https://www.amazon.com/ref=cs_503_link')
        #     time.sleep(1)
        #     self.lr.load(url)

        #     forms = BeautifulSoup(self.lr.body).find_all('form')
        #     for f in forms:
        #         print('=======')
        #         print('444444 %s' % f.attrs.get('action'))
        #         for input_tag in f.find_all("input"):
        #             print('%s - %s' % (input_tag.attrs.get('name'), input_tag.attrs.get('value')))

        #     open('xxx\\%s.html' % time.time(), 'w', encoding='utf-8').write(self.lr.body)

        while self.body.find('Enter the characters you see below') > 0:
            try:
                logger.error("Captcha!!!")

                captcha_path = os.path.join(CAPTCHA_DIR, '%s.jpg' % time.time())
                img_url = self.xpath('//img[contains(@src, "captcha")]').get('src')
                logger.info('load img: %s' % img_url)
                (resp_headers, body) = self.h.request(img_url, method='GET', headers=self.headers)
                with open(captcha_path, 'wb') as f:
                    f.write(body)
                code = self.gsa.decode(captcha_path)

                logger.info('Decode Captcha: %s' % code)
                amzn = self.xpath('//input[@name="amzn"]').get('value')
                amzn_r = self.xpath('//input[@name="amzn-r"]').get('value')

                captcha_url = 'https://www.amazon.com/errors/validateCaptcha?amzn=%s&amzn-r=%s&field-keywords=%s' % (quote_plus(amzn), quote_plus(amzn_r), code)
                # payload = {'amzn': amzn,
                #             'amzn-r': amzn_r,
                #             'field-keywords': code,}
                logger.info('load url: %s' % captcha_url)
                (resp_headers, body) = self.h.request(captcha_url, method='GET', headers=self.headers) #, data=payload)
                self.load_cookies(resp_headers)
                # open('xxx\\%s.html' % time.time(), 'w', encoding='utf-8').write(self.lr.body)
                (resp_headers, body) = self.h.request(url, method='GET', headers=self.headers)
                self.set_body(body, resp_headers)
                self.load_cookies(resp_headers)
            except Exception as ex:
                logger.error(ex, exc_info=True)



    def fetch_list(self, keyword):

        file = os.path.join(ASIN_DIR, '%s.txt' % keyword)
        if not os.path.exists(file):
            self.key_asins[keyword] = []

            # self.lr.load('https://www.amazon.com')
            # self.load_amazon('https://www.amazon.com')
            # self.load_amazon('https://www.amazon.com')
            # self.load_amazon('https://www.amazon.com')
            # open('xxx\\%s.html' % time.time(), 'w').write(self.lr.body)

            # print('cccccccccccccccc %s' % self.lr.body.find('crid'))
            # self.lr.load('https://www.amazon.com/s?k=%s' % quote(keyword))
            # self.load_amazon('https://www.amazon.com/s?k=%s' % quote(keyword))

            # form = BeautifulSoup(self.lr.body).find_all('form')[0]
            # for f in forms:
            #     print('33333333333333333')
            #     print('444444 %s' % f.attrs.get('action'))
            #     for input_tag in f.find_all("input"):
            #         print('%s - %s' % (input_tag.attrs.get('name'), input_tag.attrs.get('value')))
            # print('--------------------')
            # s_url = '%s?field-keywords=%s' % (urljoin('https://www.amazon.com/', form.attrs.get('action')), quote(keyword))
            # self.load_amazon('https://www.amazon.com/s/ref=nb_sb_noss_1?url=search-alias%%3Daps&field-keywords=%s' % quote(keyword))
            # self.load_amazon('https://www.amazon.com/s?field-keywords=%s&ref=cs_503_search' % quote(keyword))
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
        product_eles = self.xpaths('//div[contains(@class, "s-result-list")]/div[contains(@data-component-type, "s-search-result")]')
        for product_ele in product_eles:
            logger.info('asin: %s' % product_ele.get('data-asin'))
            self.key_asins[keyword].append(product_ele.get('data-asin'))


    def next_page(self):
        next_ele = self.xpath('//div[contains(@class, "s-pagination-container")]//a[contains(@aria-label, "next page")]')
        if next_ele is None:
            return False
        else:
            next_url = urljoin(self.current_url, next_ele.get('href'))
            self.load_amazon(next_url)
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

            title_ele = self.xpath('//span[@id="productTitle"]')
            title = ''.join(title_ele.itertext()).strip()

            brand = ''
            brand_ele = self.xpath('//a[@id="bylineInfo"]')
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


def do_keyword(keyword):
    try:
        sa = SpiderAmazon()
        sa.fetch_list(keyword)
        sa.fetch_products(keyword)
        sa.fetch_trademarkia(keyword)
        sa.fetch_uspto(keyword)

        sa.output_csv(keyword)
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


    executor = ThreadPoolExecutor(max_workers=5)

    for file in os.listdir(KEYWORD_PATH):
        try:
            for keyword in open(os.path.join(KEYWORD_PATH, file), 'r', encoding='utf-8').readlines():
                keyword = keyword.strip()
                if keyword:
                    executor.submit(do_keyword, keyword)
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
