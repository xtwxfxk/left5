# -*- coding: utf-8 -*-
__author__ = 'xtwxfxk'

import os, time, re, json, math, traceback, xlwt
import pandas as pd
from datetime import datetime
from urllib.parse import urlparse

from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.common.keys import Keys

old_path = '客户文件'
new_path = '修改文件'
config = {'profile_dir': 'D:/profiles/xxxxxx'}

result_format = '''URL: %s
Product name: %s
50%% off code: %s
Reg.Price: $%s
Final Price: $%s
Expire Date: %s'''



class DocMaker(object):

    def __init__(self):

        options = Options()
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--ignore-ssl-errors')
        options.add_argument("user-data-dir=%s" % config['profile_dir']) # D:/profiles/xxx
        # if config.get('proxy', None) is not None and config.get('proxy'):
        #     options.add_argument('proxy-server=%s' % config['proxy']) # socks5://127.0.0.1:1080
        self.browser = webdriver.Chrome(options=options)

        self.wait = WebDriverWait(self.browser, 120)
        self.is_find_discount = False
        self.is_gp = False
        self.product_url = ''

        self.variation_over = False
        self.variation_list = []

        if not os.path.exists(new_path):
            os.mkdir(new_path)

    def browser_home(self):
        body = self.browser.find_element_by_xpath('//body')
        body.send_keys(Keys.HOME)
        time.sleep(1)
        body.send_keys(Keys.HOME)
        time.sleep(1)

    def browser_end(self):
        body = self.browser.find_element_by_xpath('//body')
        body.send_keys(Keys.END)
        time.sleep(1)
        body.send_keys(Keys.END)
        time.sleep(1)

    def browser_up(self):
        body = self.browser.find_element_by_xpath('//body')
        body.send_keys(Keys.PAGE_UP)
        time.sleep(1)
        body.send_keys(Keys.PAGE_UP)
        time.sleep(1)

    def browser_down(self):
        body = self.browser.find_element_by_xpath('//body')
        body.send_keys(Keys.PAGE_DOWN)
        time.sleep(1)
        body.send_keys(Keys.PAGE_DOWN)
        time.sleep(1)

    def make(self, path):

        for f in os.listdir(old_path):
            df = pd.read_excel(os.path.join(old_path, f), names=['old', 'new'], header=0)
            for i, p in enumerate(df['old']): # [-2:]
                for _ in range(2):
                    try:
                        output_str = self.do(p)
                        df['new'][i] = output_str
                    except:
                        traceback.print_exc()
                        print('redo')
                    else:
                        break

            # df.to_excel(os.path.join(new_path, f), index=False)
            self.write(df, f)

    def write(self, df, file_name):

        alignment = xlwt.Alignment()
        alignment.horz = xlwt.Alignment.HORZ_LEFT
        alignment.vert = xlwt.Alignment.VERT_CENTER
        alignment.wrap = 1
        style = xlwt.XFStyle()
        style.alignment = alignment

        # excel_for_write = df.reset_index()

        workbook = xlwt.Workbook(encoding='UTF-8')
        worksheet = workbook.add_sheet('sheet')
        worksheet.write(0, 0, '客户给的', style)
        worksheet.write(0, 1, '修改后的', style)
        worksheet.col(0).width = 256 * 70
        worksheet.col(1).width = 256 * 70
        # for i, line in enumerate(df):
        for index, row in df.iterrows():
            worksheet.write(index + 1, 0, row['old'], style)
            worksheet.write(index + 1, 1, row['new'], style)
            worksheet.row(index + 1).height_mismatch = True
            worksheet.row(index + 1).height = 120 * 20

        workbook.save(os.path.join(new_path, file_name))



    def do(self, p):
        print('############################')
        self.is_find_discount = False
        self.is_gp = False
        self.variation_over = False
        self.variation_list = []

        self.product_url = ''

        p = self.warp(p)

        discount_code = self.make_discount_code(p)
        expire_date = self.make_expire_date(p)
        self.get_product_page(p)
        #####
        current_url, product_name, reg_price, coupon_price = self.make_url_name_price(p)
        if self.is_gp:
            current_url = self.product_url

        variation_price = self.add_cart(p)
        discount_price = self.make_discount_price(p, discount_code)

        # print('#############\nurl: %s\nname: %s\nreg: %s\nvariation price: %s\ncoupon: %s\ndiscount price: %s\ndiscount coed: %s\nexpire: %s\n###########' % (
        #     current_url, product_name, reg_price, variation_price, coupon_price, discount_price, discount_code,
        #     expire_date))

        while discount_price == .0 and len(self.variation_list) > 0:
            variation_price = self.add_cart(p)
            discount_price = self.make_discount_price(p, discount_code)

            # print('#############\nurl: %s\nname: %s\nreg: %s\nvariation price: %s\ncoupon: %s\ndiscount price: %s\ndiscount coed: %s\nexpire: %s\n###########' % (current_url, product_name, reg_price, variation_price, coupon_price, discount_price, discount_code, expire_date))

        final_price = variation_price

        coupon_per = .0
        if coupon_price and coupon_price.startswith("$"):
            coupon_per = math.ceil(float(coupon_price[1:]) / variation_price * 100)
            final_price = final_price - float(coupon_price[1:])
        elif coupon_price and coupon_price.endswith("%"):
            coupon_per = float(coupon_price[:-1])
            coupon_price = coupon_per / 100 * variation_price
            final_price = final_price - coupon_price

        discount_per = .0
        if discount_price > .0:
            discount_per = math.ceil(discount_price / variation_price * 100)
            final_price = final_price - discount_price

        discount_str = discount_code
        dis_list = []
        if discount_per > .0: dis_list.append('%s%% off code' % discount_per)
        if coupon_per: dis_list.append('%s%% coupon' % coupon_per)
        if len(dis_list) > 0:
            discount_str = '%s%% (%s): %s' % (discount_per + coupon_per, ' + '.join(dis_list), discount_str)

        output_str = '''URL: %s
Product name: %s
%s%% off code: %s
Reg.Price: $%s
Final Price: $%.2f
Expire Date: %s''' % (
        current_url, product_name, coupon_per + discount_per, discount_str, variation_price, final_price,
        expire_date)

        print(output_str)
        print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
        return output_str

    def warp(self, p: str):
        chars = {' ': ' ', '：': ':'}
        for k, v in chars.items():
            p = p.replace(k, v)

        ppp = []
        p = '\n'.join(p.split('                   '))
        pp = p.splitlines()
        next_pass = False
        for i, _p in enumerate(pp):
            if next_pass:
                next_pass = False
                continue
            if _p.strip().endswith(':') and len(pp) > (i + 1):
                ppp.append('%s%s' % (_p, pp[i+1]))
                next_pass = True
            else:
                ppp.append(_p)

        return '\n'.join(ppp)

    def get_product_page(self, p):
        _product_url = 'http%s' % p.rsplit('http')[1].splitlines()[0]
        # print(self.lr.current_url)

        print("URL: %s" % _product_url)
        self.browser.get(_product_url)
        self.product_url = _product_url
        if self.browser.current_url.find('/gp/mpc/') > -1:
            self.is_gp = True
            self.browser.find_elements_by_xpath('//div[contains(@class, "a-column")]//div[contains(@class, "a-row")]')[0].click()


    def make_url_name_price(self, p):

        self.wait.until(lambda driver: driver.find_element_by_xpath('//span[@id="productTitle"]'))
        product_name = self.browser.find_element_by_xpath('//span[@id="productTitle"]').text.strip()
        current_url = self.browser.current_url

        if '/dp/' in current_url:
            domain, p = current_url.split('/dp/')
            current_url = 'https://%s/dp/%s' % (domain.split('/')[2], p[:10])

        self.wait.until(lambda driver: driver.find_element_by_xpath('//span[@id="priceblock_ourprice" or @id="priceblock_saleprice"]'))
        reg_price = self.browser.find_element_by_xpath('//span[@id="priceblock_ourprice" or @id="priceblock_saleprice"]').text.strip()

        coupon_price = ''
        if self.browser.page_source.find('couponFeature') > -1:
            for w in self.browser.find_element_by_xpath('//div[@id="unclippedCoupon"]//span[@class="a-color-success"]').text.strip().split():
                if w.startswith('$') or w.endswith('%'):
                    coupon_price = w

        return current_url, product_name, reg_price, coupon_price

    def add_cart(self, p):
        params = 'th=1&psc=1'

        if not self.is_variation() and self.browser.page_source.find('id="variation') > -1:
            variation_eles = self.browser.find_elements_by_xpath('//div[contains(@id, "variation")]')
            if len(self.variation_list) < 1:
                for variation_ele in variation_eles:
                    variation_id = variation_ele.get_attribute('id')
                    if variation_ele.get_attribute('class').find('dropdown') > -1:
                        variation_ele.click()
                        variation_a_eles = self.browser.find_elements_by_xpath('//li[contains(@class, "a-dropdown-item")]/a') # //div[@class="a-popover-inner"]//li[contains(@class, "dropdownAvailable")]/a
                        for variation_a_ele in variation_a_eles:
                            string_val = json.loads(variation_a_ele.get_attribute('data-value'))['stringVal']
                            if string_val != '-1':
                                variation_code = string_val.split(',')[-1]
                                if len(variation_code) == 10 and variation_code not in self.variation_list:
                                    self.variation_list.append(variation_code)
                    else:
                        variation_li_eles = variation_ele.find_elements_by_xpath('.//li')
                        for variation_li_ele in variation_li_eles:
                            variation_code = variation_li_ele.get_attribute('data-defaultasin')
                            if len(variation_code) == 10 and variation_code not in self.variation_list:
                                self.variation_list.append(variation_code)

        if self.is_variation():
            variation_code = self.variation_list.pop(0)
            url = 'https://%s/dp/%s?%s' % (urlparse(self.browser.current_url).netloc, variation_code, params)
            print('url: %s' % url)
            self.browser.get(url)
            time.sleep(1)

        variation_price = .0
        if self.browser.page_source.find('See All Buying Options') > -1:
            print('not add to cart')
            self.browser.find_element_by_xpath('//a[@title="See All Buying Options"]').click()
            self.wait.until(lambda driver: driver.find_element_by_xpath('//input[@id="add-to-cart-button"]'))
            time.sleep(1)

            self.wait.until(lambda driver: driver.find_element_by_xpath('//div[@id="aod-offer-price"]//span[@class="a-price"]/span[contains(@class, "a-offscreen")]'))
            time.sleep(1)
            variation_price = self.browser.find_element_by_xpath('//div[@id="aod-offer-price"]//span[@class="a-price"]/span[contains(@class, "a-offscreen")]').text.strip()
            if variation_price.startswith('$'):
                variation_price = float(variation_price[1:])

            self.browser_home()
            self.browser.find_element_by_xpath('//input[@id="add-to-cart-button"]').click()
            time.sleep(1)
        else:
            self.wait.until(lambda driver: driver.find_element_by_xpath('//input[@id="add-to-cart-button"]'))
            self.wait.until(lambda driver: driver.find_element_by_xpath('//span[@id="priceblock_ourprice" or @id="priceblock_saleprice"]'))
            time.sleep(1)
            variation_price = self.browser.find_element_by_xpath('//span[@id="priceblock_ourprice" or @id="priceblock_saleprice"]').text.strip()
            if variation_price.startswith('$'):
                variation_price = float(variation_price[1:])

            self.browser_home()
            self.browser.find_element_by_xpath('//input[@id="add-to-cart-button"]').click()
            time.sleep(1)

        return variation_price



    def make_discount_price(self, p, discount_code):

        self.browser.get('https://www.amazon.com/gp/cart/view.html?ref_=nav_cart')
        time.sleep(1)

        self.wait.until(lambda driver: driver.find_element_by_xpath('//span[@id="sc-buy-box-ptc-button"]'))
        ele_deletes = self.browser.find_elements_by_xpath('//form[@id="activeCartViewForm"]//input[@data-action="delete"]')
        while len(ele_deletes) > 1:
            if ele_deletes[1].is_displayed():
                ele_deletes[1].click()
                time.sleep(1)
            else:
                self.browser.get(self.browser.current_url)
                time.sleep(1)
            ele_deletes = self.browser.find_elements_by_xpath('//form[@id="activeCartViewForm"]//input[@data-action="delete"]')


        # for ele_delete in ele_deletes[1:]:
        #     if ele_delete.is_displayed():
        #         ele_delete.click()
        #         time.sleep(2)

        self.browser_home()

        self.browser.find_element_by_xpath('//span[@data-a-class="quantity"]').click()
        time.sleep(1)
        self.browser.find_elements_by_xpath('//ul[@role="listbox"]//li')[1].click()
        time.sleep(1)

        self.browser.find_element_by_xpath('//span[@id="sc-buy-box-ptc-button"]').click()
        time.sleep(1)

        # todo wait ele
        self.wait.until(lambda driver: driver.find_element_by_xpath('//a[contains(text(), "Deliver to this")]'))
        if 'addressselect' in self.browser.current_url:
            # ele_addresses = self.browser.find_element_by_xpath('//a[contains(text(), "Deliver to this")]')
            # if len(ele_addresses) > 0:
            #     ele_addresses[0].click()
            #     time.sleep(1)
            self.browser.find_element_by_xpath('//a[contains(text(), "Deliver to this")]').click()
            time.sleep(1)

        self.wait.until(lambda driver: driver.find_element_by_xpath('//input[@type="submit" and @value="Continue"]'))
        if 'shipoptionselect' in self.browser.current_url:
            # self.browser.find_element_by_xpath('//span[@class="free-shipping-background"]').click()
            # time.sleep(1)
            # self.browser.find_element_by_xpath('//div[contains(@class, "fake-label")]//input[@type="radio"]').click()
            # time.sleep(1)
            self.browser.find_element_by_xpath('//input[@type="submit" and @value="Continue"]').click()
            time.sleep(1)

        self.wait.until(lambda driver: driver.find_element_by_xpath('//span[contains(text(), "Enter a gift card")]'))
        if 'payselect' in self.browser.current_url:
            self.browser.find_element_by_xpath('//span[contains(text(), "Enter a gift card")]').click()
            time.sleep(1)

            discount_code_input = self.browser.find_element_by_xpath('//input[@type="text" and @placeholder="Enter Code"]')

            discount_code_input.clear()
            discount_code_input.send_keys(discount_code)
            discount_code_input.send_keys(Keys.ENTER)

            # time.sleep(10)
            # if 'The promotional code you entered is not valid' in self.browser.page_source:
            #     return .0

            # wait.until(lambda driver: driver.find_element_by_xpath('//span[@class="pmts-use-balance-value"]') or driver.find_element_by_xpath('//span[@class="a-list-item" and contains(text(), "The promotional code you entered is not valid")]'))

            if not self.is_gp:
                self.wait.until(lambda driver: driver.find_element_by_xpath('//span[(@class="a-list-item" and contains(text(), "The promotional code you entered is not valid")) or @class="pmts-use-balance-value"]'))
                if 'The promotional code you entered is not valid' in self.browser.page_source:
                    return .0
            if self.browser.page_source.find('Your available balance') > -1:
                discount_price = self.browser.find_element_by_xpath('//span[@class="pmts-use-balance-value"]').text
                if discount_price.startswith('$'):
                    return float(discount_price[1:])
                else:
                    return float(discount_price)
            else:
                return .0
        

    def make_discount_code(self, p):
        discount_list = ['优惠码', 'code', '折扣码', 'coupon', '折扣']
        exclude_list = ['price', '$']
        pass_matchs_list = ['discount']
        discount_reg = re.compile('[a-z0-9]{8}')

        _p = p.lower()
        for discount_key in discount_list:
            if discount_key in _p:
                dis_line = _p.rsplit(discount_key)[1].splitlines()[0]
                is_pass = any([True if exclude_str in dis_line else False for exclude_str in exclude_list])

                if is_pass:
                    continue

                matches_list = discount_reg.findall(dis_line)
                for m in matches_list:
                    if m not in pass_matchs_list:
                        return m.upper()


    
    def make_expire_date(self, p):
        expire_date_list = [e.lower() for e in ['Ending date', 'ExpireDate', 'Expire Date', 'End Date', '结束时间', 'Expiration Date', 'Code End Day', 'End Day']]
        _p = p.lower()
        expire = None
        for expire_date in expire_date_list:
            if expire_date in _p:
                expire = _p.rsplit(expire_date)[1].splitlines()[0]

            if expire is not None:
                break
        if expire is None:
            print("没有找到过期时间...")

        date_reg_exps = {'%Y-%m-%d': re.compile('\d{4}-\d{2}-\d{2}'),
                         '%Y.%m.%d': re.compile('\d{4}.\d{2}.\d{2}'),
                         '%Y/%m/%d': re.compile('\d{4}/\d{2}/\d{2}'),
                         '%m.%d': re.compile('\d{2}\.\d{2}'),
                         '%m-%d': re.compile('\d{2}\-\d{2}'), }

        for date_format, date_reg_exp in date_reg_exps.items():
            matches_list = date_reg_exp.findall(expire)
            if len(matches_list) > 0:
                d = datetime.strptime(matches_list[0], date_format)
                now = datetime.now()
                if d.year < now.year:
                    d = datetime(year=now.year, month=d.month, day=d.day)
                return d.strftime('%Y-%m-%d')

    def is_variation(self):
        if len(self.variation_list) > 0:
            return True
        return False

if __name__ == '__main__':

    docMaker = DocMaker()
    docMaker.make('ad.xlsx')
