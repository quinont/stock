import logging
import os

def setupLogging():
    level_debug = os.environ.get("LEVELDEBUG", "DEBUG").upper()

    level_mapping = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }

    logging.basicConfig(
        level=level_mapping.get(level_debug, logging.DEBUG),
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

setupLogging()
