# -*- coding: utf-8 -*-
__author__ = 'xtwxfxk'

import os, time, math, json, traceback, itertools, urllib, copy, logging, configparser, random
import lutils
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.common.keys import Keys

config = configparser.ConfigParser()
config.read('settings.ini')
DATA_PATH = config['setting']['data_path']
MESSAGE_INTERVAL = int(config['setting']['message_interval'])
USER_INTERVAL = int(config['setting']['user_interval'])
PROXY = config['setting']['proxy']
AUTO_REFRESH_PAGE = int(config['setting']['auto_refresh_page'])
USER_DATA_DIR = config['setting']['user_data_dir']
WORD_COUNT = int(config['setting']['word_count'])
WORD_INTERVAL = float(config['setting']['word_interval'])

logger = logging.getLogger('lutils')

class DataLoader():

    def __init__(self, data_path):
        self.data_path = data_path

    def load(self):
        datas = []
        for i in range(1, 99):
            messages_file = 'messages%02d.txt' % i
            users_links_file = 'users_links%02d.txt' % i
            messages_path = os.path.join(self.data_path, messages_file)
            users_path = os.path.join(self.data_path, users_links_file)
            if os.path.exists(messages_path) and os.path.exists(users_path):
                messages = [m.strip() for m in open(messages_path, 'r', encoding='utf-8').read().split('\n\n')]
                users = [u.strip() for u in open(users_path, 'r', encoding='utf-8').readlines()]

                datas.append([[users_links_file, messages_file], [users, messages]])
        return datas



class Messager():

    def __init__(self, user_data_dir=None):
        opts = Options()
        if user_data_dir:
            opts.add_argument("user-data-dir=%s" % user_data_dir)
        self.browser = webdriver.Chrome(options=opts)
        self.wait = WebDriverWait(self.browser, 120)

        while not self.check_login():
            time.sleep(120)

    def check_login(self):
        self.browser.get('http://www.facebook.com')
        time.sleep(5)
        if self.browser.page_source.find('featuredLogin') > -1:
            logger.info('你有 2 分钟时间登录...')
            return False
        return True

    def post_message(self, message):
        edit_div = self.browser.find_element_by_xpath('//div[@data-block="true"]/div')
        edit_div.click()
        time.sleep(1)

        for line in message.splitlines():
            chunks = line.strip()
            if WORD_COUNT > 1:
                chunks = [chunks[i:i+WORD_COUNT] for i in range(0, len(chunks), WORD_COUNT)]

            for chars in chunks:
                edit_div.send_keys(chars)
                if WORD_INTERVAL > 0: time.sleep(WORD_INTERVAL)

            edit_div.send_keys(Keys.ALT + Keys.ENTER)
            edit_div = self.browser.find_elements_by_xpath('//div[@data-block="true"]/div')[-1]
            edit_div.click()

        edit_div.send_keys(Keys.ENTER)
        time.sleep(3)
        last_ele = self.browser.find_elements_by_xpath('//span[@role="gridcell"]')[-1]
        if message.find(last_ele.text) > -1:
            return True
        else:
            return False
    def load_user(self, url):
        self.browser.get(url)
        time.sleep(10)
        self.wait.until(lambda driver: driver.find_element_by_xpath('//div[@data-block="true"]/div'))

    def post_messages(self, users, messages):
        for user_url in users:
            try:
                logger.info('加载用户: %s' % user_url)
                self.load_user(user_url)
                for message in messages:
                    if self.post_message(message):
                        logger.info('发送成功，等待 %s 秒...' % MESSAGE_INTERVAL)
                    else:
                        logger.info('无法确认信息是否发送成功，等待 %s 秒...' % MESSAGE_INTERVAL)

                    time.sleep(MESSAGE_INTERVAL)
                    if AUTO_REFRESH_PAGE:
                        logger.info('重新加载用户: %s' % user_url)
                        self.load_user(user_url)

                logger.info('用户: %s 发送完毕，等待 %s 秒后继续执行...' % (user_url, USER_INTERVAL * 60))
                time.sleep(USER_INTERVAL * 60)
            except Exception as ex:
                logger.error(traceback.format_exc())
                time.sleep(10)

def start():
    logger.info('开始加载数据...')
    datas = DataLoader(DATA_PATH).load()
    messager = Messager(USER_DATA_DIR)
    logger.info('开始发送数据...')
    for [[users_links_file, messages_file], [users, messages]] in datas:
        messager.post_messages(users, messages)

        logger.info('用户: %s, 消息: %s 发送完毕...' % (users_links_file, messages_file))
        # time.sleep(USER_INTERVAL * 60)

    logger.info('所有信息发送完毕...')

if __name__ == '__main__':
    start()
    
