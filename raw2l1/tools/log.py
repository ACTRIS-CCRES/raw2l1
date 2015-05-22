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
    log_dir = os.path.dirname(os.path.abspath(opt['log']))
    log_file = os.path.basename(opt['log'])
    dir_ok = utils.check_dir(log_dir)
    if not dir_ok:
        print("critical - " + log_dir + " doesn't exist or is not writable")
        print("quitting raw2l1")
        sys.exit(1)

    filename = os.path.join(log_dir, log_file)

    # level of log file
    f_level = getattr(logging, opt['log_level'].upper(), None)
    # level of terminal log
    t_level = getattr(logging, opt['verbose'].upper(), None)

    # configuration of log
    logger = logging.getLogger(name)
    logger.setLevel(f_level)

    # create log file
    f_handler = logging.handlers.RotatingFileHandler(
        filename,
        maxBytes=1E6,
        backupCount=10)
    f_handler.setLevel(f_level)

    # Configuration of logs in terminal
    t_handler = logging.StreamHandler()
    t_handler.setLevel(t_level)
    t_handler.setLevel(logging.DEBUG)

    # Format of LOG
    formatter = logging.Formatter(LOG_FMT, datefmt=LOG_DATE_FMT)
    f_handler.setFormatter(formatter)
    t_handler.setFormatter(formatter)

    # add the handlers to logger
    logger.addHandler(f_handler)
    logger.addHandler(t_handler)

    return logger
