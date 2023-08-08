# -*- coding: utf-8 -*-

import datetime
from configparser import ConfigParser, MissingSectionHeaderError
from tasks import convert_hdf

config = ConfigParser()
try:
    config.read('settings.ini', encoding='utf-8')
except MissingSectionHeaderError:
    config.read('settings.ini', encoding='utf-8-sig')

SAVE_DIR = config['setting']['SaveDir']


if __name__ == '__main__':
    today = datetime.datetime.today()
    day_str = datetime.datetime.strftime(today, '%Y-%m-%d')
    convert_hdf(SAVE_DIR, day_str)
