#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Compatibility with python 3
from __future__ import print_function, division, absolute_import

import argparse
import datetime as dt
import sys
import os
import glob
from itertools import chain
from tools.utils import check_dir

PROG_DESC = "Raw LIDAR data to netCDF converter"
DATE_FMT = "%Y%m%d"
LOG_LEVEL = ['debug', 'info', 'warning', 'error', 'critical']


def check_date_format(input_date):
    """
    Check the format of the date argument
    """

    try:
        dt_date = dt.datetime.strptime(input_date, DATE_FMT)
    except:
        msg = "%r has not the required format (YYYYMMDD)" % input_date
        raise argparse.ArgumentTypeError(msg)

    return dt_date


def check_input_files(input_files):
    """
    check if the input files exist and return a list of the input files found
    """

    print(input_files)

    list_files = glob.glob(input_files)

    if len(list_files) == 0:
        msg = "No input files found corresponding to the file pattern "
        msg += input_files
        raise argparse.ArgumentTypeError(msg)

    return sorted(list_files)


def check_output_dir(output_file):
    """
    check if the directory provided for the output file is writable
    """

    output_file = os.path.abspath(output_file)
    out_dir = os.path.dirname(output_file)

    if not check_dir(out_dir):
        msg = "output directory " + out_dir
        msg += " doesn't exist or is not writable"
        raise argparse.ArgumentTypeError(msg)

    return output_file


def check_input_file_size(list_files, size_limit):
    """
    check size of input files. If files have a lower size they are rejected
    """

    err_msg = "WARNING -102 No Usable data in the input file '{}'"

    final_list = []
    for f in list_files:
        if os.path.getsize(f) > size_limit:
            final_list.append(f)
        else:
            print(err_msg.format(f))

    return final_list


def init_args_parser():
    """
    Configure the argument parser to read and do basic check on input
    arguments
    """

    parser = argparse.ArgumentParser(description=PROG_DESC)

    # Data processing related arguments
    parser.add_argument('date',
                        type=check_date_format,
                        help='Date to process (yyyymmdd)')
    parser.add_argument('conf_file',
                        type=argparse.FileType('r'),
                        help='Name of the INI configuration file to use')
    parser.add_argument('input_file',
                        type=check_input_files,
                        nargs='*',
                        help='Name or pattern of the file(s) to convert')
    parser.add_argument('output_file',
                        type=check_output_dir,
                        help='Name of the output file (.nc extension)')

    # Real time related argument
    parser.add_argument('-file_min_size',
                        required=False,
                        type=int,
                        default=0,
                        help='Minimum size of input files in bytes. Files with lower size will be rejected')

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

    # check input file
    list_input = check_input_file_size(
        [f for f in chain.from_iterable(parse_args.input_file)],
        parse_args.file_min_size)

    if len(list_input) == 0:
        err_msg = "CRITICAL - 102 No Usable data in any file. Quitting raw2l1"
        print(err_msg)
        sys.exit(1)

    input_args = {}
    input_args['date'] = parse_args.date
    input_args['conf'] = parse_args.conf_file
    input_args['input'] = list_input
    input_args['output'] = parse_args.output_file
    input_args['log'] = parse_args.log
    input_args['log_level'] = parse_args.log_level
    input_args['verbose'] = parse_args.v
    input_args['input_min_size'] = parse_args.file_min_size

    return input_args
