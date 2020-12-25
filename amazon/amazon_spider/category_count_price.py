# -*- coding: utf-8 -*-
__author__ = 'xtwxfxk'

import logging
import logging.config
import urllib
import traceback
import threading
from Queue import Queue, Empty

from lutils.lrequest import LRequest
from lutils.captcha.gsa_captcha import GsaCaptcha

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('verbose')


string_proxies = [
    'socks4://192.168.1.188:1080',
    'socks4://192.168.1.188:1081',
    'socks4://192.168.1.188:1082',
    'socks4://192.168.1.188:1083',
    'socks4://192.168.1.188:1084',
    #'socks4://192.168.1.188:1085',
]

captcha = GsaCaptcha(ip='192.168.1.188', port=8000)

def check_captcha(lr):
    if captcha is not None:
        captcha_img_ele = lr.xpath('//form[contains(@action, "Captcha")]//img[contains(@src, "captcha")]')
        if captcha_img_ele is not None:
            while 1:
                try:
                    if captcha_img_ele is not None:
                        logger.info('Need Captcha')

                        form = lr.get_forms()[0]
                        lr.load(captcha_img_ele.attrib['src'])
                        cap = captcha.decode_stream(lr.body)
                        logger.info('Captcha: %s' % cap)

                        form['field-keywords'] = cap
                        lr.load(form.click())
                    else:
                        return True

                    captcha_img_ele = lr.xpath('//form[contains(@action, "Captcha")]//img[contains(@src, "captcha")]')

                except KeyboardInterrupt:
                    raise
                except IndexError:
                    lr.load(lr.current_url)
                    captcha_img_ele = lr.xpath('//form[contains(@action, "Captcha")]//img[contains(@src, "captcha")]')
                    if captcha_img_ele is None:
                        return True
                except:
                    logger.error(traceback.format_exc())

        return False
    else:
        raise RuntimeError('Not Captcha Server...')

f = open('cc.txt', 'w')
def do(queue, string_proxy):
    lr = LRequest(string_proxy=string_proxy)
    while 1:
        try:
            # https://www.amazon.com/s/ref=nb_sb_noss?url=search-alias%3Daps&field-keywords=sheets+silk
            category = queue.get(timeout=30)
            url = 'https://www.amazon.com/s/ref=nb_sb_noss?url=search-alias%%3Daps&field-keywords=%s' % urllib.quote_plus(category)

            lr.load(url)
            if check_captcha(lr):
                lr.load(url)

            total_price = 0.0
            count = 0.0
            price_eles = lr.xpaths('//span[contains(@class, "s-price a-text-bold")]')
            for price_ele in price_eles: # $49.99
                price = price_ele.text.replace('$', '').replace(',', '').split('-', 1)[0].strip()
                try:
                    float(price)
                except:
                    pass
                else:
                    total_price += float(price)
                    count += 1
            if count > 0:
                ave_price = total_price / count

            ele = lr.xpath('//h2[@id="s-result-count"]')

            f.write('%s\t%s\t%.2f\n' % (category, ele.text.split('result', 1)[0].split('of')[-1].strip().replace(',', ''), ave_price))
            f.flush()
            print '%s\t%s\t%.2f' % (category, ele.text.split('result', 1)[0].split('of')[-1].strip().replace(',', ''), ave_price)


        except Empty:
            print 'empty'
            break
        except Exception as e:
            traceback.print_exc()
            queue.put(category)
            print 'EEEEEEEEE %s' % e
            # traceback.print_exc()


queue = Queue()

ts = []
for i in range(len(string_proxies)*3):
    t = threading.Thread(target=do, args=(queue, string_proxies[i%len(string_proxies)]))
    t.start()
    ts.append(t)


for category in open('category.txt'):
    queue.put(category.strip())


for t in ts:
    t.join()
