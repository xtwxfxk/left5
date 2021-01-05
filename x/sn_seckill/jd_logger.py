import logging
import logging.handlers
'''
日志模块
'''
LOG_FILENAME = 'jd_seckill.log'
logger = logging.getLogger()


def set_logger():
    logger.setLevel(logging.INFO) # %(asctime)s %(levelname)s %(module)s %(process)d %(thread)d %(message)s
    # formatter = logging.Formatter('%(asctime)s - %(process)d-%(threadName)s - '
    #                               '%(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s')
    
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(module)s %(process)d %(thread)d %(message)s')
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    file_handler = logging.handlers.RotatingFileHandler(
        LOG_FILENAME, maxBytes=10485760, backupCount=5, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

set_logger()