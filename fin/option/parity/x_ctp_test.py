

import os, json, time, itertools
import logging

from queues import data_queue
from utils import target_call_put

logger = logging.getLogger('verbose')

root = 'D:/option_data/test'

tcp = target_call_put()
# columns = [c for c in list(itertools.chain.from_iterable(columns))]

f_dict = {}

# for column in columns:
#     f_dict[column] = open(os.path.join(root, 'SHFE.%s' % column), 'r', encoding='utf-8')


# def data_test():
#     while 1:
#         try:
#             for k, v in f_dict.items():
#                 x = v.readline().strip()
#                 if x:
#                     data_queue.put(json.loads(x))

#             # time.sleep(0.5)
#         except KeyboardInterrupt:
#             return
#         except Exception as ex:
#             logger.error(ex, exc_info=True)