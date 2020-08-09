# -*- coding: utf-8 -*-
__author__ = 'xtwxfxk'

import time, csv, yaml
from io import BytesIO
from PIL import Image
from docx import Document
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.common.keys import Keys

config = yaml.safe_load(open('config.yml').read())

def read_keywords():
    keywords = []
    for row in csv.reader(open('keyworkds.csv'), delimiter=','):
        if len(row) == 3 and row[1].isdigit() and row[2].isdigit():
            keywords.append([row[0], int(row[1]), float(row[1])])
        elif len(row) == 2 and row[1].isdigit():
            keywords.append([row[0], int(row[1]), config['pic_alpha']])
        else:
            keywords.append([row[0], int(config['pic_count']), float(config['pic_alpha'])])

    return keywords

def fetch_image(keywords):
    opts = Options()
    opts.add_argument("user-data-dir=%s" % config['profile_dir']) # D:/profiles/xxxxxx
    # opts.add_argument("profile-directory=%s" % config['profile_dir'])  # D:/profiles/xxxxxx
    if config.get('proxy', None) is not None and config.get('config'):
        opts.add_argument('proxy-server=%s' % config['proxy']) # socks5://127.0.0.1:1080
    browser = webdriver.Chrome(options=opts)

    wait = WebDriverWait(browser, 120)

    browser.get('http://www.facebook.com')

    for keyword, pic_count, pic_alpha in keywords:
        browser.get('http://www.facebook.com')
        doc = Document()

        # wait.until(lambda driver: driver.find_element_by_xpath('//input[@name="q"]'))
        time.sleep(5)
        search = browser.find_element_by_xpath('//input[@name="q"]')

        search.clear()
        search.send_keys(keyword)
        search.send_keys(Keys.ENTER)

        wait.until(lambda driver: driver.find_element_by_xpath('//span[text()="你的小组"]'))
        group = browser.find_element_by_xpath('//span[text()="你的小组"]')
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

            blacks = browser.find_elements_by_xpath('//div[@class="_4rmu"]/div/div[1]')
            for b in blacks:
                browser.execute_script('arguments[0].setAttribute("style", "background-color:#DCDCDC")', b)
            trs = ele.find_elements_by_xpath('//div[@class="_4rmu"]/div/div[1]//*')
            # browser.execute_script('arguments[0].setAttribute("style", "color: rgba(75, 79, 86, 1)")', t)
            for t in trs:
                if 'highlightNode' not in t.get_attribute("class"):
                    # browser.execute_script('arguments[0].setAttribute("style", "color: transparent;text-shadow: #111 0 0 4px;")', t)
                    browser.execute_script('arguments[0].setAttribute("style", "color: rgba(75, 79, 86, %s)")' % pic_alpha, t)
                    # browser.execute_script('arguments[0].setAttribute("style", "visibility: hidden;")', t)
                else:
                    # browser.execute_script('arguments[0].setAttribute("style", "font-weight:bold;color: black;text-shadow: #000 0 0 0px;")', t)
                    browser.execute_script('arguments[0].setAttribute("style", "color: rgba(75, 79, 86, 1)")', t)

            # hls = ele.find_elements_by_xpath('//div[@class="_4rmu"]//span[@class="highlightNode"]')
            # for h in hls:
            #     browser.execute_script('arguments[0].setAttribute("style", "color: transparent;text-shadow: none")', h)

            # img = Image.open(BytesIO(ele.screenshot_as_png))

            # img.save("D:/code/python/fb/%s.png" % i, "PNG")

            doc.add_picture(BytesIO(ele.screenshot_as_png))

        doc.save('%s.docx' % keyword)


if __name__ == '__main__':

    keywords = read_keywords()
    fetch_image(keywords)