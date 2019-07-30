import logging
import sys


def get_logger(name, formatter="default"):
    """
    This method returns a logger instance. If this method is called for the first time with a specific name
    a stream handler will be added to the logger so that the output of the logger will be displayed on the stdout.
    If this method is called multiple times, each time the same logger instance is returned.
    :param name: The name the logger should have. If the same as another these are two times the same loggers.
    :param formatter: Either 'default' (information: time, loglevel, filename, message) or 'simple' (only message)
    :return: The logger instance
    """
    logger = logging.getLogger(name)

    if len(logger.handlers) != 0:
        return logger

    # Stream Handler
    stream_handler = logging.StreamHandler(sys.stdout)

    if formatter is "default":
        stream_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(levelname)s - %(filename)s:\t%(message)s",
                datefmt="%b %d %Y %H:%M:%S %Z",
            )
        )
    elif formatter is "simple":
        stream_handler.setFormatter(logging.Formatter("%(message)s"))
    else:
        raise ValueError("Formatter must be simple or default")

    logger.setLevel(logging.DEBUG)
    logger.addHandler(stream_handler)

    return logger
