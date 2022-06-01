# -*- coding: utf-8 -*-
__author__ = 'xtwxfxk'

import os, time, csv, yaml
from io import BytesIO
from PIL import Image, ImageFilter
from docx import Document
from docx.shared import Inches
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

    if not os.path.exists('docx'):
        os.mkdir('docx')

    for keyword, pic_count in keywords:
        browser.get('http://www.facebook.com')
        doc = Document()


        # group_tab_xpath = '//a[@aria-label="小组"]/parent::div'
        # wait.until(lambda driver: driver.find_element_by_xpath(group_tab_xpath))
        # group_tab = browser.find_element_by_xpath(group_tab_xpath)
        # group_tab.click()

        wait.until(lambda driver: driver.find_element_by_xpath('//input[@type="search"]'))
        search = browser.find_element_by_xpath('//input[@type="search"]')
        search.clear()
        search.send_keys(keyword)
        time.sleep(1)
        search.send_keys(Keys.ENTER)
        time.sleep(2)

        group_span_xpath = '//div[@role="region"]//span[contains(text(), "帖子")]'
        wait.until(lambda driver: driver.find_element_by_xpath(group_span_xpath))
        group = browser.find_element_by_xpath(group_span_xpath)
        group.click()
        time.sleep(1)

        group_source_xpath = '//span[contains(text(), "帖子来源")]'
        wait.until(lambda driver: driver.find_element_by_xpath(group_source_xpath))
        group_source = browser.find_element_by_xpath(group_source_xpath)
        group_source.click()
        time.sleep(1)

        group_my_xpath = '//span[@dir="auto"]/span[contains(text(), "你的小组和主页")]'
        wait.until(lambda driver: driver.find_element_by_xpath(group_my_xpath))
        group_my = browser.find_element_by_xpath(group_my_xpath)
        group_my.click()
        time.sleep(1)

        body = browser.find_element_by_xpath('//body')

        pic_box_xpath = '//div[@role="article"]/div/div/div/div/div/a[@role="link"]'
        wait.until(lambda driver: driver.find_element_by_xpath(pic_box_xpath))

        eles = []
        for i in range(10):
            eles = browser.find_elements_by_xpath(pic_box_xpath)
            if len(eles) < pic_count:
                if body:
                    for _ in range(3):
                        body.send_keys(Keys.PAGE_DOWN)
                        time.sleep(2)
                    time.sleep(2)
            else:
                break

        body.send_keys(Keys.HOME)
        time.sleep(2)

        eles = browser.find_elements_by_xpath(pic_box_xpath)
        for ele in eles[:pic_count]:
            browser.execute_script('arguments[0].setAttribute("style", "padding-top: 5px;")', ele)

            highlight_eles = ele.find_elements_by_xpath('.//span[@dir="auto"]/span')
            for highlight_ele in highlight_eles:
                text = highlight_ele.text.upper()
                new_text = text.replace(keyword.upper(), '''<span class="ccccxxxxccc">%s</span>''' % keyword.upper())
                aa = 'arguments[0].innerHTML = `%s`;' % new_text.replace('"', '\\"')
                browser.execute_script(aa, highlight_ele)

        eles = browser.find_elements_by_xpath(pic_box_xpath)

        for i, ele in enumerate(eles[:pic_count]):
            img = Image.open(BytesIO(ele.screenshot_as_png))

            if len(ele.find_elements_by_xpath('./div')) > 1:
                blacks = ele.find_elements_by_xpath('./div[1]')

                url_localtion = blacks[0].location
                url_size = blacks[0].size
                url_box = [0, 5, url_size['width'], url_size['height'] + 5]

                hightNodes = []
                trs = ele.find_elements_by_xpath('.//span[@class="ccccxxxxccc"]')
                for t in trs:
                    left = t.location['x'] - url_localtion['x']
                    upper = t.location['y'] - url_localtion['y']
                    right = left + t.size['width']
                    lower = upper + t.size['height']
                    box = [left - 5, upper - 5, right + 5, lower + 5]
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

            doc.add_picture(buf, width=Inches(5.2))

        doc.save('docx/%s.docx' % keyword)


if __name__ == '__main__':

    keywords = read_keywords()
    fetch_image(keywords)
