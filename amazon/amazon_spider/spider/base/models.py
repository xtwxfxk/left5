# -*- coding: utf-8 -*-
__author__ = 'xtwxfxk'

import os, logging, datetime
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, SmallInteger
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import QueuePool

Base = declarative_base()


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger = logging.getLogger('verbose')

# db = os.path.join(BASE_DIR,  'data\\amazon.db')
db = 'I:\\amazon_data\\amazon.db'

engine = create_engine('sqlite:///%s' % db) #, poolclass=QueuePool)


class Url(Base):
    __tablename__ = 'url'

    id = Column(Integer, primary_key=True)

    key = Column(String, unique=True, nullable=True)
    name = Column(String, nullable=True)

    url = Column(String, nullable=False)

    type = Column(SmallInteger) # URL_TYPE
    has_crawled = Column(Boolean, default=False)

    tries = Column(SmallInteger, default=0) # try count


    def as_dict(self):
        return {'id': self.id, 'key': self.key,
                'name': self.name, 'url': self.url,
                'type': self.type, 'has_crawled': self.has_crawled,
                'tries': self.tries}


class DictDot(dict):
    """
    Example:
    m = DictDot({'first_name': 'Eduardo'}, last_name='Pool', age=24, sports=['Soccer'])
    """
    def __init__(self, *args, **kwargs):
        super(DictDot, self).__init__(*args, **kwargs)
        for arg in args:
            if isinstance(arg, dict):
                for k, v in arg.iteritems():
                    self[k] = v

        if kwargs:
            for k, v in kwargs.iteritems():
                self[k] = v

    def __getattr__(self, attr):
        return self.get(attr)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __setitem__(self, key, value):
        super(DictDot, self).__setitem__(key, value)
        self.__dict__.update({key: value})

    def __delattr__(self, item):
        self.__delitem__(item)

    def __delitem__(self, key):
        super(DictDot, self).__delitem__(key)
        del self.__dict__[key]



Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
# Session.configure(bind=engine)

# Session = scoped_session(sessionmaker(bind=engine))
# session = Session(autocommit=True)

class URL_TYPE():

    PRODUCT_URL = 99

    BEST_SELL_CATEGORY = 2
    BEST_SELL_CATEGORY_NEXT = 3

