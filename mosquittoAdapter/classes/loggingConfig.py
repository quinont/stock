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
    # Arreglar el login para que mqtt y fastapi tengan el mismo formato
    logging.getLogger("uvicorn.access").addFilter(NoHealthCheckSuccessFilter())


class NoHealthCheckSuccessFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return record.args and \
            len(record.args) >= 3 and \
            record.args[2] != "/health"
