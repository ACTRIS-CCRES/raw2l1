#!/usr/bin/env python

# Compatibility with python 3


import argparse
import datetime as dt
import glob
import os
import sys
from itertools import chain

from .utils import check_dir

PROG_DESC = "Raw LIDAR data to netCDF converter"
DATE_FMT = "%Y%m%d"
LOG_LEVEL = ["debug", "info", "warning", "error", "critical"]


def check_date_format(input_date):
    """
    Check the format of the date argument
    """

    try:
        dt_date = dt.datetime.strptime(input_date, DATE_FMT)
    except ValueError:
        msg = "%r has not the required format (YYYYMMDD)" % input_date
        raise argparse.ArgumentTypeError(msg)

    return dt_date


def check_anc_lists_files(input_files):
    """
    Check input files lists and return a list of each input.

    Parameters
    ----------
    input_files : list of str
        The list of input files given by SIRTA workflow.

    Returns
    -------
    list of list of str
        The list of list of input files

    """
    # check if files exist
    input_list = check_input_files(input_files)

    return input_list


def check_input_files(input_files):
    """
    check if the input files exist and return a list of the input files found
    """

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
    parser.add_argument(
        "date", type=check_date_format, help="Date to process (yyyymmdd)"
    )
    parser.add_argument(
        "conf_file",
        type=argparse.FileType("r"),
        help="Name of the INI configuration file to use",
    )
    parser.add_argument(
        "input_file",
        type=check_input_files,
        nargs="*",
        help="Name or pattern of the file(s) to convert",
    )
    parser.add_argument(
        "output_file",
        type=check_output_dir,
        help="Name of the output file (.nc extension)",
    )

    # additional input files
    parser.add_argument(
        "-anc",
        "--ancillary",
        type=check_anc_lists_files,
        action="append",
        nargs="*",
        dest="ancillary",
        help="Name or pattern of the ancillary file(s) needed to do the conversion",
    )

    # Real time related argument
    parser.add_argument(
        "-file_min_size",
        required=False,
        type=int,
        default=0,
        help="Minimum size of input files in bytes. Files with lower size will be rejected",  # NOQA
    )
    parser.add_argument(
        "--check_timeliness",
        required=False,
        action="store_true",
        default=False,
        help="Check if data in input file have any date in the future or are too old. "
        "See '-file_max_age' option to define the maximum age of data. "
        "Option only for realtime processing",
    )
    parser.add_argument(
        "-file_max_age",
        required=False,
        type=int,
        default=2,
        help="Maximum age of data in input files. Warning will be logged if older data are found."  # NOQA
        "Default value is 2 hours. Option only for realtime processing",
    )

    # reprocessing filter dates
    parser.add_argument(
        "--filter-day",
        required=False,
        action="store_true",
        default=False,
        help="Only keep timesteps of the processed day in output file",
    )

    # logs related arguments
    parser.add_argument(
        "-log",
        required=False,
        default="logs/raw2l1.log",
        help="File where logs will be saved",
    )
    parser.add_argument(
        "-log_level",
        required=False,
        choices=LOG_LEVEL,
        default="info",
        help="Level of logs store in the log file",
    )
    parser.add_argument(
        "-v",
        required=False,
        choices=LOG_LEVEL,
        default="info",
        help="Level of verbose in the terminal",
    )

    return parser


def get_input_args(argv):
    """
    return input arguments into a dictionnary
    """

    # init argument parser
    parser = init_args_parser()

    try:
        parse_args = parser.parse_args(argv)
        print(parse_args.ancillary)
    except argparse.ArgumentError as exc:
        print("\n", exc.argument)
        sys.exit(1)

    # check input file
    list_input = check_input_file_size(
        [f for f in chain.from_iterable(parse_args.input_file)],
        parse_args.file_min_size,
    )

    if len(list_input) == 0:
        err_msg = "CRITICAL - 102 No Usable data in any file. Quitting raw2l1"
        print(err_msg)
        sys.exit(1)

    # check ancillary files
    print("parse : ", parse_args.ancillary)
    list_anc = []
    if parse_args.ancillary:
        for anc_list in parse_args.ancillary:
            list_anc.append([f for f in chain.from_iterable(anc_list)])

    input_args = {}
    input_args["date"] = parse_args.date
    input_args["conf"] = parse_args.conf_file
    input_args["input"] = list_input
    input_args["output"] = parse_args.output_file
    input_args["ancillary"] = list_anc
    input_args["log"] = parse_args.log
    input_args["log_level"] = parse_args.log_level
    input_args["verbose"] = parse_args.v
    input_args["filter_day"] = parse_args.filter_day

    # real time
    input_args["input_min_size"] = parse_args.file_min_size
    input_args["input_check_time"] = parse_args.check_timeliness
    input_args["input_max_age"] = dt.timedelta(hours=parse_args.file_max_age)

    return input_args
