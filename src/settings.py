import logging
from logging import Formatter


def set_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.ERROR)
    formatter = Formatter("%(asctime)s %(levelname)s %(message)s")
    console = logging.StreamHandler()
    log_file = logging.FileHandler(filename="crawl.log")
    console.setFormatter(formatter)
    log_file.setFormatter(formatter)
    logger.addHandler(console)
    # logger.addHandler(log_file)
    return logger
