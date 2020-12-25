# -*- coding: utf-8 -*-
__author__ = 'xtwxfxk'

import os, logging, datetime
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, SmallInteger
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

from ... import config

Base = declarative_base()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger = logging.getLogger('verbose')

db = os.path.join(BASE_DIR,  config.DB_FILE) # 'data\\amazon.db')

engine = create_engine('sqlite:///%s' % db)


class Url(Base):
    __tablename__ = 'url'

    id = Column(Integer, primary_key=True)

    key = Column(String, unique=True, nullable=True)
    name = Column(String, nullable=True)

    url = Column(String, nullable=False)

    type = Column(SmallInteger) # URL_TYPE
    has_crawled = Column(Boolean, default=False)

Base.metadata.create_all(engine)
Session = sessionmaker()
Session.configure(bind=engine)



class URL_TYPE():

    PRODUCT_URL = 99

    BEST_SELL_CATEGORY = 2
    BEST_SELL_CATEGORY_NEXT = 3

