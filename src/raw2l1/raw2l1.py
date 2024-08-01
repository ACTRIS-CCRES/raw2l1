#!/usr/bin/env python
import datetime as dt
import io
import sys

from raw2l1.tools import arg_parser as ag
from raw2l1.tools import conf, log
from raw2l1.tools import create_netcdf as cnc
from raw2l1.tools import lidar_reader as lr
from raw2l1.tools.check_conf import check_conf
from raw2l1.version import __version__

NAME = "raw2l1"


def welcome_msg():
    """Print a welcome message in the terminal."""
    print()  # noqa: T201
    print(r"--------------------------------------------------")  # noqa: T201
    print(NAME)  # noqa: T201
    print(r" ___  __   _   _  ___ _   __  ")  # noqa: T201
    print(r"| _ \/  \ | | | |(_  | | /  | ")  # noqa: T201
    print(r"| v / /\ || 'V' | / /| |_`7 | ")  # noqa: T201
    print(r"|_|_\_||_|!_/ \_!|___|___||_| ")  # noqa: T201
    print()  # noqa: T201
    print(r"version: " + __version__)  # noqa: T201
    print(r"SIRTA IPSL/CNRS/EP 2014-2024")  # noqa: T201
    print(r"--------------------------------------------------")  # noqa: T201
    print()  # noqa: T201

    return


def raw2l1(
    date: dt.datetime,
    conf_file: io.TextIOWrapper,
    input_files: list[str],
    output_file: str,
    ancillary: list[list[str]] | None = None,
    file_min_size: int = 0,
    check_timeliness: bool = False,
    file_max_age: int = 2,
    filter_day: bool = False,
    log_file: str = "logs/raw2l1.log",
    log_file_level: str = "info",
    verbose: str = "info",
):
    """Run raw2l1 processing."""
    welcome_msg()

    # Start logger
    # -------------------------------------------------------------------------
    logger = log.init(log_file, log_file_level, verbose, "raw2l1")
    logger.info("logs are saved in %s", log_file)

    # reading configuration file
    # -------------------------------------------------------------------------
    logger.debug("reading configuration file %s", conf_file.name)
    setting = conf.init(
        date,
        conf_file,
        input_files,
        output_file,
        ancillary,
        file_min_size,
        check_timeliness,
        file_max_age,
        filter_day,
        log_file,
        log_file_level,
        verbose,
        __version__,
        logger,
    )
    logger.info("reading configuration file: OK")

    # check configuration file
    logger.debug("checking configuration file")
    setting = check_conf(setting, logger)

    # Add directory containing reader to path
    # -------------------------------------------------------------------------
    logger.debug("adding %s to path", setting.get("conf", "reader_dir"))
    sys.path.append(setting.get("conf", "reader_dir"))

    # Reading lidar data using user defined reader
    # -------------------------------------------------------------------------
    logger.info("reading lidar data")
    lidar_data = lr.RawDataReader(setting, logger)
    lidar_data.read_data()
    logger.info("reading data successed")

    # checking read data if needed
    # -------------------------------------------------------------------------
    if check_timeliness:
        time_ok = lidar_data.timeliness_ok(file_max_age, logger)

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

    return 0


def cli():
    # Read imput arguments
    # -------------------------------------------------------------------------
    input_args = ag.get_input_args(sys.argv[1:])

    raw2l1(
        input_args["date"],
        input_args["conf"],
        input_args["input"],
        input_args["output"],
        ancillary=input_args["ancillary"],
        file_min_size=input_args["input_min_size"],
        check_timeliness=input_args["input_check_time"],
        file_max_age=input_args["input_max_age"],
        filter_day=input_args["filter_day"],
        log_file=input_args["log"],
        log_file_level=input_args["log_level"],
        verbose=input_args["verbose"],
    )

    sys.exit(0)
