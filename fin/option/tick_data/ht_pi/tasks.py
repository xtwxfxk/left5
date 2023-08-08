# -*- coding: utf-8 -*-

import schedule
import time
import os, datetime, json, traceback
import pandas as pd
import numpy as np
import h5py
import logging
import logging.config
from utils import zipfolder

import warnings
from tables import NaturalNameWarning
warnings.filterwarnings('ignore', category=NaturalNameWarning)

logger = logging.getLogger('verbose')


def convert_hdf(data_root, day_str):
    old_path = os.path.join(data_root, '%s_json' % day_str)
    zip_path = os.path.join(data_root, '%s_json.zip' % day_str)
    if os.path.exists(old_path):
        new_path = os.path.join(data_root, day_str)
        if not os.path.exists(new_path): os.makedirs(new_path)

        for file_name in os.listdir(old_path):
            new_file = os.path.join(new_path, '%s.h5' % file_name)
            file_path = os.path.join(old_path, file_name)

            logger.info('save hdf: %s' % file_name)
            datas = []
            for line in open(file_path):
                if line.strip():
                    datas.append(json.loads(line.strip()))
            df = pd.DataFrame.from_dict(datas)
            df.to_hdf(new_file, file_name, mode='w', format='table', complevel=8, data_columns=True)

        time.sleep(10)

        zipfolder(zip_path, old_path)


def do_task_hdf(data_root):
    try:
        today = datetime.datetime.today()

        day = today - datetime.timedelta(days=1)
        day_str = datetime.datetime.strftime(day, '%Y-%m-%d')
        convert_hdf(data_root, day_str)
        
        if today.weekday() == 5:
            convert_hdf(data_root, datetime.datetime.strftime(today, '%Y-%m-%d'))


    except KeyboardInterrupt:
        logger.info('Exit KeyboardInterrupt')
    except Exception as ex:
        logger.error(ex, exc_info=True)



def task_hdf(data_root, t):
    # schedule.every().day.at(t).do(do_task_hdf, data_root)

    schedule.every().tuesday.at(t).do(do_task_hdf, data_root)
    schedule.every().wednesday.at(t).do(do_task_hdf, data_root)
    schedule.every().thursday.at(t).do(do_task_hdf, data_root)
    schedule.every().friday.at(t).do(do_task_hdf, data_root)
    schedule.every().saturday.at(t).do(do_task_hdf, data_root)


    while 1:
        try:
            schedule.run_pending()
            time.sleep(1)
        except KeyboardInterrupt:
            logger.info('Exit KeyboardInterrupt hdf')
            return