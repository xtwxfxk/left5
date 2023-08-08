# -*- coding: utf-8 -*-
import os, re

import logging
import logging.config
import zipfile


logger = logging.getLogger('verbose')


EXCHANGE_REGEX = (
    ('SHFE', re.compile('^zn\d+', re.IGNORECASE)),
    ('INE', re.compile('^sc\d+', re.IGNORECASE)),
    ('SHFE', re.compile('^ru\d+', re.IGNORECASE)),
    ('SHFE', re.compile('^rb\d+', re.IGNORECASE)),
    ('SHFE', re.compile('^cu\d+', re.IGNORECASE)),
    ('SHFE', re.compile('^au\d+', re.IGNORECASE)),
    ('SHFE', re.compile('^al\d+', re.IGNORECASE)),
    ('SHFE', re.compile('^ag\d+', re.IGNORECASE)),
    ('CZCE', re.compile('^ta\d+', re.IGNORECASE)),
    ('CZCE', re.compile('^sr\d+', re.IGNORECASE)),
    ('CZCE', re.compile('^rm\d+', re.IGNORECASE)),
    ('CZCE', re.compile('^pk\d+', re.IGNORECASE)),
    ('CZCE', re.compile('^oi\d+', re.IGNORECASE)),
    ('CZCE', re.compile('^ma\d+', re.IGNORECASE)),
    ('CZCE', re.compile('^cf\d+', re.IGNORECASE)),
    ('DCE', re.compile('^y\d+', re.IGNORECASE)),
    ('DCE', re.compile('^v\d+', re.IGNORECASE)),
    ('DCE', re.compile('^pp\d+', re.IGNORECASE)),
    ('DCE', re.compile('^pg\d+', re.IGNORECASE)),
    ('DCE', re.compile('^p\d+', re.IGNORECASE)),
    ('DCE', re.compile('^m\d+', re.IGNORECASE)),
    ('DCE', re.compile('^l\d+', re.IGNORECASE)),
    ('DCE', re.compile('^i\d+', re.IGNORECASE)),
    ('DCE', re.compile('^c\d+', re.IGNORECASE)),
    ('DCE', re.compile('^b\d+', re.IGNORECASE)),
    ('DCE', re.compile('^a\d+', re.IGNORECASE)),
)

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