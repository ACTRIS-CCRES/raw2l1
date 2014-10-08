#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Compatibility with python 3
from __future__ import print_function, division, absolute_import

import sys
from tools import lidar_reader as lr
from tools import arg_parser as ag
from tools import log
from tools import conf

__name__ = 'raw2l1'
__author__ = 'Marc-Antoine Drouin'
__version__ = '2.0.0a'

def welcome_msg():
    """
    print a welcome message in the terminal
    """

    print("")
    print("--------------------------------------------------")
    print(__name__)
    print(" ___  __   _   _  ___ _   __  ")
    print("| _ \/  \ | | | |(_  | | /  | ")
    print("| v / /\ || 'V' | / /| |_`7 | ")
    print("|_|_\_||_|!_/ \_!|___|___||_| ")
    print("")
    print("version: " + __version__)
    print("SIRTA IPSL/CNRS/EP 2014")
    print("--------------------------------------------------")
    print("")

    return None

def raw2l1(argv):
    """
    Main module of raw2l1
    """

    welcome_msg()

    # Read imput arguments
    input_args = ag.get_input_args(argv)

    # Start logger
    logger = log.init(input_args, 'raw2l1')
    logger.info('logs are saved in {!s}'.format(input_args['log']))

    # reading configuration file
    logger.debug('reading configuration file {!s}'.format(input_args['conf'].name))
    setting = conf.init(input_args, logger)
    logger.info('reading configuration file: OK')

    # Add directory containing reader to path
    logger.debug("adding "+setting.get('conf', 'reader_dir')+" to path")
    sys.path.append(setting.get('conf', 'reader_dir'))

    # Reading lidar data using user defined reader
    logger.info("reading lidar data")
    lidar_data = lr.RawDataReader(setting, logger)
    lidar_data.read_data()
    logger.debug("test output : "+repr(lidar_data.data))
    logger.info("reading data successed")

    logger.info("end of processing")
    sys.exit(0)

if __name__ == 'raw2l1':
    raw2l1(sys.argv[1:])


