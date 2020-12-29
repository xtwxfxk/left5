# -*- coding: utf-8 -*-
__author__ = 'xtwxfxk'

from lutils.lrequest import LRequest

url = 'https://www.amazon.com/Best-Sellers-Home-Kitchen/zgbs/home-garden/ref=zg_bs_nav_0'

lr = LRequest()

lr.load(url, isdecode=True)
eles = lr.xpaths('//ul[@id="zg_browseRoot"]/ul/ul/li/a')

for ele in eles:
    print(ele.text.strip(), ele.attrib['href'])
