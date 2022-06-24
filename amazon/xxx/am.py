# -*- coding: utf-8 -*-
__author__ = 'xtwxfxk'

import os, time, csv, yaml
import logging
import logging.config
from lutils.lrequests import LRequests


logging.config.fileConfig('logging.conf')
logger = logging.getLogger('verbose')

ROOT = os.getcwd()
KEYWORD_PATH = os.path.join(ROOT, 'keywords')

def spider_amazon(keywords):

    print(keywords)




def start():
    keywords = []
    for file in os.path.listdir(KEYWORD_PATH):
        keywords.extend([k if k.strip() for k in open(os.path.join(KEYWORD_PATH, file)).readlines()])

    spider_amazon(keywords)



if __name__ == '__main__':
    start()
