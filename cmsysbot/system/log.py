import logging


def generate_log_config():

    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    logging.basicConfig(
        format=log_format,
        level=logging.INFO
    )

    formatter = logging.Formatter(log_format)

    # Error handler
    eh = logging.FileHandler('log/error.log')
    eh.setLevel(logging.ERROR)
    eh.setFormatter(formatter)

    # Warning handler
    wh = logging.FileHandler('log/warn.log')
    wh.setLevel(logging.WARNING)
    wh.setFormatter(formatter)

    # INFO handler
    ih = logging.FileHandler('log/info.log')
    ih.setLevel(logging.INFO)
    ih.setFormatter(formatter)

    # Logger
    logger = logging.getLogger(__name__)
    logger.addHandler(eh)
    logger.addHandler(wh)
    logger.addHandler(ih)

    return logger
