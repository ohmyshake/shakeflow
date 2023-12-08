import logging


def get_logger(logpath, level=logging.INFO):
    logging.getLogger().handlers = []
    logging.basicConfig(
        filename=logpath,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger()

    return logger
