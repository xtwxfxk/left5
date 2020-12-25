# -*- coding: utf-8 -*-
__author__ = 'xtwxfxk'


for line in open('cc.txt'):
    category, count, price = line.strip().rsplit('\t')
    price = float(price)

    if count.isdigit():
        if int(count) < 5000 and price > 80.0:
            print category
