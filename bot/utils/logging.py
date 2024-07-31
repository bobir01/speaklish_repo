import logging


def setup_logger(name, log_file=None, level=logging.DEBUG, mode='w'):
    # Create a file handler for output file

    formatter = logging.Formatter('[%(asctime)s]  %(filename)s -> %(funcName)s:%(lineno)d - %(levelname)s \n---> %(message)s')

    if log_file:
        file_handler = logging.FileHandler(log_file, mode=mode)
        file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    # Set the formatter for the console and file handlers
    console_handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Add the console and file handlers to the logger
    logger.addHandler(console_handler)
    if log_file:
        logger.addHandler(file_handler)

    return logger

