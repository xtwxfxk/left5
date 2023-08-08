# -*- coding: utf-8 -*-
import os, datetime, json, traceback, re
import threading, queue
# from multiprocessing import Process, Queue

import logging
import logging.config
from configparser import ConfigParser, MissingSectionHeaderError

data_queue = queue.Queue(maxsize=100)
# data_queue = Queue(maxsize=100)

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('verbose')

ROOT = os.getcwd()
LOG_DIR = os.path.join(ROOT, 'logs')
if not os.path.exists(LOG_DIR): os.makedirs(LOG_DIR)

config = ConfigParser()
try:
    config.read('settings.ini', encoding='utf-8')
except MissingSectionHeaderError:
    config.read('settings.ini', encoding='utf-8-sig')


FrontAddr = config['setting']['FrontAddr'] # "tcp://180.168.146.187:10211" # 行情
# FrontAddr='tcp://180.168.146.187:10130'
#LoginInfo
BROKERID = config['setting']['BROKERID']
USERID = config['setting']['USERID']
PASSWORD = config['setting']['PASSWORD']

AppID = config['setting']['AppID']
AuthCode = config['setting']['AuthCode']

TaskH5 = AuthCode = config['setting']['TaskH5']

SAVE_DIR = config['setting']['SaveDir']
if not os.path.exists(SAVE_DIR): os.makedirs(SAVE_DIR)

from ctp_datas import ctp_process
# from ctp_datas_writer import data_writer
from tasks import task_hdf



def main():
    ctp_thread = threading.Thread(target=ctp_process, args=(FrontAddr, BROKERID, USERID, PASSWORD, SAVE_DIR, data_queue,)) #, daemon=True)
    # data_thread = threading.Thread(target=data_writer, args=(SAVE_DIR, data_queue,)) #, daemon=True)
    task_thread = threading.Thread(target=task_hdf, args=(SAVE_DIR, TaskH5))
    
    # ctp_thread = Process(target=ctp_process, args=(FrontAddr, BROKERID, USERID, PASSWORD, data_queue,))
    # data_thread = Process(target=data_writer, args=(SAVE_DIR, data_queue,))
    # task_thread = Process(target=task_hdf, args=(SAVE_DIR, TaskH5))
    
    try:
        ctp_thread.start()
        # data_thread.start()
        task_thread.start()

        ctp_thread.join()
        logger.info('ctp process over')
        # data_thread.join()
        # logger.info('data process over')
        task_thread.join()
        logger.info('hdf process over')
    except KeyboardInterrupt:
        logger.info('并没用')
        ctp_thread.kill()
    except Exception as ex:
        logger.error(ex, exc_info=True)



if __name__ == '__main__':
    main()
