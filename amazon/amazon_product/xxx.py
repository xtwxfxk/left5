# -*- coding: utf-8 -*-
__author__ = 'xtwxfxk'

import urllib.parse
from lutils.lrequest import LRequest

# url = 'https://www.amazon.com/Best-Sellers-Home-Kitchen/zgbs/home-garden/ref=zg_bs_nav_0'
url = 'https://www.amazon.com/Best-Sellers-Home-Kitchen-Décor-Products/zgbs/home-garden/1063278'
# url = urllib.parse.quote('https://www.amazon.com/Best-Sellers-Home-Kitchen-Décor-Products/zgbs/home-garden/1063278')
# url = urllib.parse.urlencode('https://www.amazon.com/Best-Sellers-Home-Kitchen-Décor-Products/zgbs/home-garden/1063278')
url = urllib.parse.quote(url, safe='https:/')
print(url)
lr = LRequest()

lr.load(url, is_decode=True)
eles = lr.xpaths('//ul[@id="zg_browseRoot"]/ul/ul/ul/li/a')

for ele in eles:
    print(ele.text.strip(), ele.attrib['href'])

# https://www.amazon.com/Best-Sellers-Home-Kitchen-D%C3%A9cor-Products/zgbs/home-garden/1063278/