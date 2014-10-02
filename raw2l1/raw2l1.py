#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Compatibility with python 3
from __future__ import print_function, division, absolute_import

import sys
import argparse
import logging
import datetime as dt

__name__ = 'raw2l1'
__author__ = 'Marc-Antoine Drouin'
__version__ = '2.0.0'

PROG_DESC = "Raw LIDAR data to netCDF converter"

DATE_FMT = "%Y%m%d"

# logs
LOG_FMT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_DATE_FMT = '%Y-%m-%d %H:%M:%S'

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

def check_date_format(input_date):
    """
    Check the format of the date argument
    """

    try:
        dt_date = dt.datetime.strptime(input_date, DATE_FMT)
    except:
        msg = "%r has not the required format (YYYYMMDD)" %input_date
        raise argparse.ArgumentTypeError(msg)

    return dt_date

def init_args_parser():
    """
    Configure the argument parser to read and do basic check on input 
    arguments
    """

    LOG_LEVEL = ['debug', 'info', 'warning', 'error', 'critical']

    parser = argparse.ArgumentParser(description=PROG_DESC)

    # Data processing related arguments
    parser.add_argument('date', 
        type=check_date_format,
        help='Date to process (yyyymmdd)')
    parser.add_argument('conf_file',
        type=argparse.FileType('r'),
        help='Name of the INI configuration file to use')
    parser.add_argument('input_file',
        type=argparse.FileType('r'),
        help='Name or pattern of the file(s) to convert')
    parser.add_argument('output_file',
        type=argparse.FileType('w'),
        help='Name of the output file (.nc extension)')

    # logs related arguments
    parser.add_argument('-log',
        required=False,
        default='logs/raw2l1.log',
        help='File where logs will be saved')
    parser.add_argument('-log_level',
        required=False,
        choices=LOG_LEVEL,
        default='info',
        help='Level of logs store in the log file')
    parser.add_argument('-v',
        required=False,
        choices=LOG_LEVEL,
        default='info',
        help='Level of verbose in the terminal')

    return parser

def get_input_args(argv):
    """
    return input arguments into a dictionnary
    """

    # init argument parser
    parser = init_args_parser()

    try:
        parse_args = parser.parse_args(argv)
    except argparse.ArgumentError, exc:
        print('\n', exc.argument)
        sys.exit(1)

    input_args = {}
    input_args['date'] = parse_args.date
    input_args['conf'] = parse_args.conf_file
    input_args['input'] = parse_args.input_file
    input_args['output'] = parse_args.output_file
    input_args['log'] = parse_args.log
    input_args['log_level'] = parse_args.log_level
    input_args['verbose'] = parse_args.v

    return input_args

def init_logger(opt):
    """
    Configure the logger and start it
    """

    # level of log file
    f_level = getattr(logging, opt['log_level'].upper(), None)
    # level of terminal log
    t_level = getattr(logging, opt['verbose'].upper(), None)

    # configuration of log
    logger = logging.getLogger(__name__)
    logger.setLevel(f_level)

    # create log file
    fh = logging.FileHandler(opt['log'])
    fh.setLevel(f_level)

    # Configuration of logs in terminal
    ch = logging.StreamHandler()
    #ch.setLevel(t_level)
    ch.setLevel(logging.DEBUG)

    # Format of LOG
    formatter = logging.Formatter(LOG_FMT, datefmt=LOG_DATE_FMT)
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    # add the handlers to logger
    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger


def raw2l1(argv):
    """
    Main module of raw2l1
    """

    welcome_msg()

    # Read imput arguments
    input_args = get_input_args(argv)

    # Start logger
    logger = init_logger(input_args)
    logger.info('logs are saved in {!s}'.format(input_args['log']))

    logger.info("end of processing")

    sys.exit(0)

if __name__ == 'raw2l1':
    raw2l1(sys.argv[1:])


