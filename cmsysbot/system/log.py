import logging
import os

from utils import states


def generate_log_config():

    log_dir = states.config_file.log_dir

    if not os.path.isdir(log_dir):
        os.makedirs(log_dir)

    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    logging.basicConfig(format=log_format, level=logging.INFO)

    formatter = logging.Formatter(log_format)

    # Error handler
    eh = logging.FileHandler(f'{log_dir}/error.log')
    eh.setLevel(logging.ERROR)
    eh.setFormatter(formatter)

    # Warning handler
    wh = logging.FileHandler(f'{log_dir}/warn.log')
    wh.setLevel(logging.WARNING)
    wh.setFormatter(formatter)

    # INFO handler
    ih = logging.FileHandler(f'{log_dir}/info.log')
    ih.setLevel(logging.INFO)
    ih.setFormatter(formatter)

    # Logger
    logger = logging.getLogger("CMSysBot")
    logger.addHandler(eh)
    logger.addHandler(wh)
    logger.addHandler(ih)

    return logger
