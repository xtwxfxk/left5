# -*- coding: utf-8 -*-
import os, datetime, json, traceback, re

import logging
import logging.config

from utils import EXCHANGE_REGEX

# logging.config.fileConfig('logging.conf')
# logger = logging.getLogger('verbose')

logger = logging.getLogger('verbose')


def data_writer(save_root, data_queue):

    while True:
        try:
            tick_data = data_queue.get()

            today = datetime.date.today().strftime('%Y-%m-%d')
            day_dir = os.path.join(save_root, '%s_json' % today)
            if not os.path.exists(day_dir):
                os.makedirs(day_dir)

            instrumentID = tick_data['InstrumentID']
            exchange = ''
            for _exchange, symbol_re in EXCHANGE_REGEX:
                if symbol_re.search(instrumentID):
                    exchange = _exchange

            file_path = os.path.join(day_dir, '%s.%s' % (exchange, tick_data['InstrumentID']))

            with open(file_path, 'a+', encoding='utf-8') as f:
                f.write('%s\n' % json.dumps(tick_data))

        except KeyboardInterrupt:
            logger.info('Exit KeyboardInterrupt save')
            return
        except Exception as ex:
            logger.error(ex, exc_info=True)

