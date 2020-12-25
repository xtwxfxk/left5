# -*- coding: utf-8 -*-
__author__ = 'xtwxfxk'

# import urlparse
import threading
from Queue import Queue, Empty
from lutils.lrequest import LRequest

string_proxies = [
    # 'socks4://192.168.1.188:1080',
    # 'socks4://192.168.1.188:1081',
    # 'socks4://192.168.1.188:1082',
    # 'socks4://192.168.1.188:1083',
    # # 'socks4://192.168.1.188:1084',
    # 'socks4://192.168.1.188:1085',
]

url = 'https://www.amazon.com/Best-Sellers/zgbs/ref=zg_bs_unv_ac_0_ac_1'

urls = [
    'https://www.amazon.com/Best-Sellers-Automotive/zgbs/automotive/ref=zg_bs_nav_0',
    'https://www.amazon.com/Best-Sellers-Beauty/zgbs/beauty/ref=zg_bs_nav_0',
    'https://www.amazon.com/best-sellers-camera-photo/zgbs/photo/ref=zg_bs_nav_0',
    'https://www.amazon.com/Best-Sellers-Cell-Phones-Accessories/zgbs/wireless/ref=zg_bs_nav_0',
    'https://www.amazon.com/Best-Sellers-Electronics/zgbs/electronics/ref=zg_bs_nav_0',
    'https://www.amazon.com/Best-Sellers-Health-Personal-Care/zgbs/hpc/ref=zg_bs_nav_0',
    'https://www.amazon.com/Best-Sellers-Home-Kitchen/zgbs/home-garden/ref=zg_bs_nav_0',
    'https://www.amazon.com/Best-Sellers-Home-Improvement/zgbs/hi/ref=zg_bs_nav_0',
    'https://www.amazon.com/Best-Sellers-Sports-Outdoors/zgbs/sporting-goods/ref=zg_bs_nav_0',
    'https://www.amazon.com/Best-Sellers-Sports-Collectibles/zgbs/sports-collectibles/ref=zg_bs_nav_0',


        ]

categories = set()

def iter_name(string_proxy, queue):
    lr = LRequest(string_proxy)

    while 1:
        try:
            url, deep = queue.get(timeout=30)
            xp = '//ul[@id="zg_browseRoot"]/%s/li/a' % '/'.join(['ul' for i in range(deep)])
            # print xp
            lr.load(url.encode('utf-8'))

            next_deep = deep + 1
            for ele in lr.xpaths(xp):
                name = ele.text.strip()
                if name not in categories:
                    categories.add(name)
                    print name.encode('utf-8')
                    queue.put([ele.attrib['href'], next_deep])

        except Empty:
            print 'Empty'


queue = Queue()

ts = []
for string_proxy in string_proxies:
    t = threading.Thread(target=iter_name, args=(string_proxy, queue))
    t.start()
    ts.append(t)


for u in urls:
    queue.put([u, 2])

for t in ts:
    t.join()
