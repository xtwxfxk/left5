# -*- coding: utf-8 -*-
import os

import logging
import logging.config
import zipfile

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('verbose')

def load_symbols():
    logger.info('开始读取代码文件...')
    symbols = []
    if os.path.exists('symbols.txt'):
        for line in open('symbols.txt', encoding='utf-8'):
            if line.strip():
                ds = line.split('|')
                c = ds[0].encode('utf-8')
                if c not in symbols:
                    symbols.append(c)
            if len(symbols) > 10:
                break
    logger.info('订阅数量 %s' % len(symbols))
    return symbols


def zipfolder(foldername, target_dir):
    logger.info('开始压缩目录 %s' % foldername)
    zipobj = zipfile.ZipFile(foldername, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=8)
    rootlen = len(target_dir) + 1
    for base, dirs, files in os.walk(target_dir):
        for file in files:
            fn = os.path.join(base, file)
            zipobj.write(fn, fn[rootlen:])
    logger.info('压缩结束 %s' % target_dir)