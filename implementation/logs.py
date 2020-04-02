import logging


def get_logger(name, log_file=None):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    if log_file is not None:
        h = logging.FileHandler(log_file, mode="w")
        logger.addHandler(h)
    return logger
