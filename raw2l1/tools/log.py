#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Compatibility with python 3
from __future__ import print_function, division, absolute_import

import logging
import logging.handlers
import os
import sys
from tools import utils

LOG_FMT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_DATE_FMT = '%Y-%m-%d %H:%M:%S'
LOG_DIR = 'logs'
LOG_FILENAME = 'raw2l1.log'


def init(opt, name):
    """
    Configure the logger and start it
    """

    # Check the logs directory
    dir_ok = utils.check_dir(LOG_DIR)
    if not dir_ok:
        print("critical - " + LOG_DIR + " doesn't exist or is not writable")
        print("quitting raw2l1")
        sys.exit(1)

    filename = os.path.join(LOG_DIR, LOG_FILENAME)

    # level of log file
    f_level = getattr(logging, opt['log_level'].upper(), None)
    # level of terminal log
    t_level = getattr(logging, opt['verbose'].upper(), None)

    # configuration of log
    logger = logging.getLogger(name)
    logger.setLevel(f_level)

    # create log file
    fh = logging.handlers.RotatingFileHandler(filename,
                                              maxBytes=1E6, backupCount=10)
    fh.setLevel(f_level)

    # Configuration of logs in terminal
    ch = logging.StreamHandler()
    ch.setLevel(t_level)
    ch.setLevel(logging.DEBUG)

    # Format of LOG
    formatter = logging.Formatter(LOG_FMT, datefmt=LOG_DATE_FMT)
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    # add the handlers to logger
    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger
