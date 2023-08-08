# -*- coding: utf-8 -*-
import os, datetime, json, traceback, re, time
import threading, queue
# from multiprocessing import Process, Queue

import json
import logging
import logging.config


# data_queue = Queue(maxsize=100)

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('verbose')

ROOT = os.getcwd()
LOG_DIR = os.path.join(ROOT, 'logs')
if not os.path.exists(LOG_DIR): os.makedirs(LOG_DIR)

config = json.load(open('config.json', 'r'))

ctp_config = config['ctp_config']
strategy_config = config['strategy_config']


from ctp_datas import ctp_process
from ctp_datas_process import data_process, data_strategy

# from x_ctp_test import data_test


def main():
    
    try:
        data_thread = threading.Thread(target=data_process, args=())
        data_thread.start()
        time.sleep(2)

        ctp_thread = threading.Thread(target=ctp_process, args=(ctp_config['md_server'], ctp_config['broker_id'], ctp_config['user_id'], ctp_config['password'], ))

        strategy_thread = threading.Thread(target=data_strategy, args=())

        ctp_thread.start()
        
        strategy_thread.start()

        # data_test_thread = threading.Thread(target=data_test, args=())
        # data_test_thread.start()
        # data_test_thread.join()

        ctp_thread.join()
        data_thread.join()

    except KeyboardInterrupt:
        pass
    except Exception as ex:
        logger.error(ex, exc_info=True)


# D:\code\python\left5\fin\option\parity
if __name__ == '__main__':
    main()
