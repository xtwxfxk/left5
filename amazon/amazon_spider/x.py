# -*- coding: utf-8 -*-
__author__ = 'xtwxfxk'

import json, time
from shove import Shove

from lutils.futures.thread import LThreadPoolExecutor

# # for i in json.loads(open('F:\\xxxcv.txt', 'r').read()):
# #     print i['hiRes']
#
#
# # for i, a in enumerate(['c', 'a']):
# #     print i, a
#
#
# executor = LThreadPoolExecutor(max_workers=5)
#
#
# def m():
#     print 'sss'
#     time.sleep(5)
#
#     return 'ccccc'
#
# a1 = executor.submit(m)
# a2 = executor.submit(m)
# a3 = executor.submit(m)
#
#
#
# print a1, a2, a3
# time.sleep(10)
# print a1.result(), a2.result(), a3.result()

# s = Shove('file:///I:\\amazon_url_info\\best_sell')
# for k, v in s.items():
#     print v

# class A():
#     d = 'sss'
#
#
# a1 = A()
# a2 = A()
#
# print a1.d
# print a2.d
#
# A.d = 'aaa'
#
# print a1.d
# print a2.d


import cPickle

a = cPickle.load(open('I:\\4aac7491d2c78a6bd9b07949589169b4'))
print a
open('sdfsdf.jpg', 'wb').write(a['page'])


