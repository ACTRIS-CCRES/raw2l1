import logging
import logging.config
import os
import sys

from raw2l1.tools import utils

LOG_FMT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FMT = "%Y-%m-%d %H:%M:%S"
LOG_DIR = "logs"
LOG_FILENAME = "raw2l1.log"


def init(log_file: str, log_level: str, verbose: str, name: str):
    """
    Configure the logger and start it
    """
    # Check the logs directory
    log_dir = os.path.dirname(os.path.abspath(log_file))
    log_file = os.path.basename(log_file)
    dir_ok = utils.check_dir(log_dir)
    if not dir_ok:
        print("critical - " + log_dir + " doesn't exist or is not writable")
        print("quitting raw2l1")
        sys.exit(1)

    filename = os.path.join(log_dir, log_file)
    print(f"debug file : {filename}")
    print(f"console debug level : {verbose.upper()}")
    print(f"file debug level : {log_level.upper()}")

    log_dict = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {"simple": {"datefmt": LOG_DATE_FMT, "format": LOG_FMT}},
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": verbose.upper(),
                "formatter": "simple",
                "stream": "ext://sys.stdout",
            },
            "file_handler": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": log_level.upper(),
                "formatter": "simple",
                "filename": filename,
                "maxBytes": 10_485_760,
                "backupCount": 10,
                "encoding": "utf8",
            },
        },
        "root": {"level": "DEBUG", "handlers": ["console", "file_handler"]},
    }

    logger = logging.getLogger(name)
    logging.config.dictConfig(log_dict)

    return logger
