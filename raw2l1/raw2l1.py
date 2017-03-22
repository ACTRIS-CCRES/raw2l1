#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Compatibility with python 3
from __future__ import print_function, division, absolute_import

import sys
from tools import lidar_reader as lr
from tools import arg_parser as ag
from tools import log
from tools import conf
from tools.check_conf import check_conf
from tools import create_netcdf as cnc

__author__ = 'Marc-Antoine Drouin'
__version__ = '2.1.15'

NAME = 'raw2l1'


def welcome_msg():
    """
    print a welcome message in the terminal
    """

    print(r"")
    print(r"--------------------------------------------------")
    print(NAME)
    print(r" ___  __   _   _  ___ _   __  ")
    print(r"| _ \/  \ | | | |(_  | | /  | ")
    print(r"| v / /\ || 'V' | / /| |_`7 | ")
    print(r"|_|_\_||_|!_/ \_!|___|___||_| ")
    print(r"")
    print(r"version: " + __version__)
    print(r"SIRTA IPSL/CNRS/EP 2014-2016")
    print(r"--------------------------------------------------")
    print(r"")

    return None


def raw2l1(argv):
    """
    Main module of raw2l1
    """

    welcome_msg()

    # Read imput arguments
    # -------------------------------------------------------------------------
    input_args = ag.get_input_args(argv)

    # Start logger
    # -------------------------------------------------------------------------
    logger = log.init(input_args, 'raw2l1')
    logger.info('logs are saved in {!s}'.format(input_args['log']))

    # reading configuration file
    # -------------------------------------------------------------------------
    logger.debug('reading configuration file ' + input_args['conf'].name)
    setting = conf.init(input_args, __version__, logger)
    logger.info('reading configuration file: OK')

    # check configuration file
    logger.debug('checking configuration file')
    setting = check_conf(setting, logger)

    # Add directory containing reader to path
    # -------------------------------------------------------------------------
    logger.debug("adding " + setting.get('conf', 'reader_dir') + " to path")
    sys.path.append(setting.get('conf', 'reader_dir'))

    # Reading lidar data using user defined reader
    # -------------------------------------------------------------------------
    logger.info("reading lidar data")
    lidar_data = lr.RawDataReader(setting, logger)
    lidar_data.read_data()
    logger.info("reading data successed")

    # checking read data if needed
    # -------------------------------------------------------------------------
    if input_args['input_check_time']:
        time_ok = lidar_data.timeliness_ok(input_args['input_max_age'], logger)

        if not time_ok:
            logger.critical("104 Data timeliness Error. Quitting raw2l1")
            sys.exit(1)

    # write netCDF file
    # -------------------------------------------------------------------------
    logger.info("writing output file")
    cnc.create_netcdf(setting, lidar_data.data, logger)

    # end of the program
    # -------------------------------------------------------------------------
    logger.info("end of processing")
    sys.exit(0)

if __name__ == '__main__':
    raw2l1(sys.argv[1:])
