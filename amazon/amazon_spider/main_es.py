# -*- coding: utf-8 -*-
__author__ = 'xtwxfxk'

import logging, logging.config, time, traceback

from sqlalchemy.sql.expression import and_

# from multiprocessing.queues import Empty
# from multiprocessing.queues import Queue
from Queue import Empty, Queue

from threading import Thread
from lutils.futures.thread import LThreadPoolExecutor

from spider.best_sell import BestSell
from spider.base.models import Url, URL_TYPE, Session

logging.config.fileConfig('logging.conf')

logger = logging.getLogger('verbose')

multiple = 3

string_proxies = [
    'socks4://192.168.1.188:1080',
    'socks4://192.168.1.188:1081',
    'socks4://192.168.1.188:1082',
    'socks4://192.168.1.188:1083',
    'socks4://192.168.1.188:1084',
]


spider_categories=[u'Ropa y accesorios', u'Coche y moto', u'Deportes y aire libre', u'Electrónica', u'Hogar', u'Informática', u'Ropa y accesorios', u'Salud y cuidado personal', u'Zapatos y complementos']

num = multiple * len(string_proxies)



def urlopt(queue):

    session = Session(autocommit=True)

    while 1:
        try:
            opt, urls = queue.get(timeout=30)

            if opt == 'add':
                url_objs = []
                for url in urls:
                    if session.query(Url).filter_by(key=url.key).count() < 1:
                        logger.info('Opt: Add %s' % url.url)

                        url_objs.append(url)
                session.bulk_save_objects(url_objs)

            elif opt == 'error':
                for url in urls:
                    logger.info('Opt: Error %s' % url.url)

                    session.query(Url).filter_by(id=url.id).update({Url.tries: url.tries+1})

            elif opt == 'over':
                for url in urls:
                    logger.info('Opt: Over %s' % url.url)
                    session.query(Url).filter_by(id=url.id).update({Url.has_crawled: True})

            # session.commit()
        except Empty:
            logger.info('Empty')
        except:
            logger.error(traceback.format_exc())




def do():

    input = Queue(maxsize=2000)
    output = Queue(maxsize=2000)

    bs = []
    for i in range(num):
        string_proxy = string_proxies[i%len(string_proxies)]
        b = BestSell(string_proxy=string_proxy, input=input, output=output, domain='amazon.es', cache_root='I:\\cache_amazon_es')
        bs.append(b)
        b.start()

    t = Thread(target=urlopt, args=[output, ])
    t.start()

    session = Session()
    if session.query(Url).count() < 1:
        bs[0].categories_first(categories=spider_categories)
        session.commit()

    while session.query(Url).filter(and_(Url.has_crawled==False, Url.tries<3)).count() > 0:
        for url_obj in session.query(Url).filter(and_(Url.has_crawled==False, Url.tries<3)).limit(1000*len(string_proxies)):
            try:
                # m = Map(url_obj.as_dict())
                logger.info('put: %s' % url_obj.url)
                input.put(url_obj.as_dict())
            except:
                logger.error(traceback.format_exc())

        logger.info('wait 5 seconds...')
        time.sleep(5)

    logger.info('oooooooooooooooooooooooooooooooover')


if __name__ == '__main__':

    do()






