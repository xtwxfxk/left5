# -*- coding: utf-8 -*-
__author__ = 'xtwxfxk'

import os, logging
from peewee import *
from playhouse.sqlite_ext import SqliteExtDatabase
import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger = logging.getLogger('verbose')

db = SqliteExtDatabase(os.path.join(BASE_DIR,  'data\\amazon.db'))

class BaseModel(Model):
    class Meta:
        database = db

class Url(BaseModel):

    key = CharField(unique=True, null=True)
    name = CharField(null=True)

    url = CharField(unique=True)

    type = IntegerField() # URL_TYPE
    has_crawled = BooleanField(default=False)


db.connect()
db.create_tables([Url, ], safe=True)


class URL_TYPE():

    PRODUCT_URL = 99

    BEST_SELL_CATEGORY = 2