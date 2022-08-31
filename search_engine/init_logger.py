import logging
from datetime import datetime

def init_logger(logger, filename) -> logging.Logger:
    logger.setLevel(logging.NOTSET)
    formatter = logging.Formatter('%(asctime)s | %(name)s |  %(levelname)s: %(message)s')

    fh = logging.FileHandler('../log/' + filename)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    sh = logging.StreamHandler()
    sh.setLevel(logging.DEBUG)
    sh.setFormatter(formatter)
    logger.addHandler(sh)
    return logger
