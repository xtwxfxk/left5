# -*- coding: utf-8 -*-
__author__ = 'xtwxfxk'


from .base.amazon_es import Amazon

class BestSellES(Amazon):

    def __init__(self, **kwargs):

        super(BestSellES, self).__init__(**kwargs)



