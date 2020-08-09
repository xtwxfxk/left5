# -*- coding: utf-8 -*-
__author__ = 'xtwxfxk'

import os, time, csv, yaml
from io import BytesIO
from PIL import Image, ImageFilter
from docx import Document
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.common.keys import Keys

config = yaml.safe_load(open('config.yml').read())

def read_keywords():
    keywords = []
    for row in csv.reader(open('keyworkds.csv'), delimiter=','):
        if len(row) == 2 and row[1].isdigit():
            keywords.append([row[0], int(row[1])])
        else:
            keywords.append([row[0], int(config['pic_count'])])

    return keywords

def fetch_image(keywords):
    opts = Options()
    opts.add_argument("user-data-dir=%s" % config['profile_dir']) # D:/profiles/xxxxxx
    # opts.add_argument("profile-directory=%s" % config['profile_dir'])  # D:/profiles/xxxxxx
    if config.get('proxy', None) is not None and config.get('proxy'):
        opts.add_argument('proxy-server=%s' % config['proxy']) # socks5://127.0.0.1:1080
    browser = webdriver.Chrome(options=opts)

    wait = WebDriverWait(browser, 120)

    browser.get('http://www.facebook.com')

    if not os.path.exists('docx'):
        os.mkdir('docx')

    for keyword, pic_count in keywords:
        browser.get('http://www.facebook.com')
        doc = Document()

        # wait.until(lambda driver: driver.find_element_by_xpath('//input[@name="q"]'))
        time.sleep(5)
        search = browser.find_element_by_xpath('//input[@name="q"]')

        search.clear()
        search.send_keys(keyword)
        search.send_keys(Keys.ENTER)

        wait.until(lambda driver: driver.find_element_by_xpath('//span[text()="你的小组" or text()="Your Groups"]'))
        group = browser.find_element_by_xpath('//span[text()="你的小组" or text()="Your Groups"]')
        group.click()

        body = browser.find_element_by_xpath('//body')

        wait.until(lambda driver: driver.find_element_by_xpath('//div[@class="_4rmu"]'))

        eles = []
        for i in range(10):
            eles = browser.find_elements_by_xpath('//div[@class="_4rmu"]')
            if len(eles) < pic_count:
                if body:
                    for _ in range(2):
                        body.send_keys(Keys.PAGE_DOWN)
                        time.sleep(2)
                    time.sleep(2)
            else:
                break

        body.send_keys(Keys.HOME)
        time.sleep(2)
        for i, ele in enumerate(eles[:pic_count]):
            img = Image.open(BytesIO(ele.screenshot_as_png))

            blacks = ele.find_elements_by_xpath('./div/div[1]')

            url_localtion = blacks[0].location
            url_size = blacks[0].size
            url_box = [0, 0, url_size['width'], url_size['height']]

            hightNodes = []
            trs = ele.find_elements_by_xpath('.//span[@class="highlightNode"]')
            for t in trs:
                left = t.location['x'] - url_localtion['x']
                upper = t.location['y'] - url_localtion['y']
                right = left + t.size['width']
                lower = upper + t.size['height']
                box = [left, upper, right, lower]
                hightNodes.append([box, img.crop(box)])

            url_img = img.crop(url_box)
            if config.get('blur', None) and str(config.get('blur')).isdigit():
                url_img = url_img.filter(ImageFilter.BoxBlur(config.get('blur')))
            if config.get('watermark', None):
                watermark = Image.open(config.get('watermark'))
                url_img.paste(watermark, mask=watermark)

            img.paste(url_img, url_box)
            for box, im in hightNodes:
                img.paste(im, box)

            buf = BytesIO()
            img.save(buf, "PNG")

            doc.add_picture(buf)

        doc.save('docx/%s.docx' % keyword)


if __name__ == '__main__':

    keywords = read_keywords()
    fetch_image(keywords)
