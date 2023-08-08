import logging, time
import os
from datetime import datetime, timedelta
from typing import Union
# from concurrent.futures import ThreadPoolExecutor
# import concurrent.futures

import ray
import pandas as pd
from contextlib import closing
from pandas import Series, Timestamp, DataFrame

from tqsdk import TqApi, TqAuth
from tqsdk.tools import DataDownloader

USERNAME = 'ahaha'
PASSWORD = 'xxxx'

api = TqApi(auth=TqAuth('ahaha', 'xxxx'))

DCE.pg2306-C-4450