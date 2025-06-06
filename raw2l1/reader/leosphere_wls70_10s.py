#!/usr/bin/env python


import ast
import datetime as dt
import os
import re
import sys

import numpy as np

# brand and model of the LIDAR
BRAND = "leosphere"
MODEL = "WLS70 10 seconds"

# CONSTANTS
MIN_2_SEC = 60

# file format
DEFAULT_ENCODING = "ISO-8859-1"
FILE_SEP = "\t"
DEFAULT_INVERSE_VERT_WIND = False

# date format
DATE_FMT = ["%d/%m/%Y %H:%M", "%d/%m/%Y %H:%M:%S"]

HEADER_TAG = "HeaderSize"
HEADER_CHAR_VALUE = "="
HEADER_BAD_CHAR_RE = r"[()\[\]\/°%]"
# header value with special processing
HEADER_SPECIAL = ["GPS Localisation", "Altitudes(m)"]

LOCALIZATION_DELIMS = r":|N|E|°"

RAW_DATA_MISSING = ["NaN"]

# possible name of time var
VAR_TIME = ["Date", "Timestamp"]

VAR_1D = [
    ("wiper_count", ["Wiper"]),
    ("temp_int", ["Temperature_\xb0C", "Temperature_°C"]),
    ("laser_position", ["Position"]),
]
# variables which need to be merged
VAR_2D = [
    ("cnr", ["CNR"]),
    ("radial_ws_disp", ["RWSD"]),
    ("radial_ws", ["RWS"]),
    ("ws", ["Vh"]),
    ("wd", ["Azi", "Dir"]),
    ("x_wind", ["u"]),
    ("y_wind", ["v"]),
    ("w", ["w"]),
]


def merge_structured_arrays(list_arr):
    """merge structure array
    based on https://gist.github.com/astrofrog/2552867
    """

    # if list has only one element return array
    if len(list_arr) == 1:
        return list_arr[0]

    final = list_arr[0].copy()

    for arr in list_arr[1:]:
        final_size = final.size
        arr_size = arr.size
        final.resize(final_size + arr_size)
        final[final_size:] = arr

    return final


def convert_time_str(str_):
    """convert LEOSPHERE date format into datetime"""

    if "." in str_:
        tmp_date, millisec = str_.split(".")
        micro_sec = int(millisec) * 10000
    else:
        tmp_date = str_
        micro_sec = 0

    for date_fmt in DATE_FMT:
        try:
            date = dt.datetime.strptime(tmp_date, date_fmt)
        except ValueError:
            continue

    to_add = dt.timedelta(microseconds=micro_sec)
    date = date + to_add

    return date


def convert_wiper(str_):
    """Convert wiper string to integer."""
    if str_ == "Off":
        return 0.0
    elif str_ == "On":
        return 1.0
    else:
        return np.nan


def norm_value_name(name):
    """normalize name of values"""

    # remove multiple blank and replace by one
    name = re.sub(r"\s+", " ", name).strip()
    # remove unwanted caracters in name
    name = re.sub(HEADER_BAD_CHAR_RE, "", name)
    # capitalize first letter of words
    if " " in name:
        name = name.title()
    # remove all blank
    name = re.sub(r"\s+", "", name)

    return name


def get_localization(value_str, conf, logger):
    """extract latitude and longitude"""

    # check if value available
    if len(value_str) == 0:
        logger.warning("localization data unavailable")
        lat = conf["lat"]
        lon = conf["lon"]
        return lat, lon

    # we have to parse the line
    tmp = re.split(LOCALIZATION_DELIMS, value_str)
    try:
        lat = float(tmp[1]) / 100.0
        lon = float(tmp[3]) / 100.0
    except ValueError:
        lat = conf["lat"]
        lon = conf["lon"]

    return lat, lon


def get_altitude(value_str, logger):
    """extract list of alitudes"""

    alt = [float(val) for val in value_str.split()]

    logger.debug(f"list of altitudes: {alt}")

    return np.array(alt)


def read_file(file_, conf, logger):
    """read one file and return a list without newline character"""

    logger.debug(f"reading {os.path.basename(file_)}")
    with open(file_, encoding=conf["file_encoding"]) as f_id:
        raw_lines = f_id.readlines()

    # remove end of line character
    raw_lines = [line.strip() for line in raw_lines]

    return raw_lines


def get_header_size(lines, logger):
    """Extract value from header by identifying line with equal sign"""

    header_found = False
    for line in lines:
        # search for header marker
        if HEADER_TAG in line:
            header_found = True
            header_size = int(line.split("=")[1])
            logger.debug(f"size of header {header_size}")

            return header_size

    if not header_found:
        return None


def read_header_data(file_, conf, data, logger):
    """read data store in the header"""

    # read file
    raw_lines = read_file(file_, conf, logger)
    header_size = get_header_size(raw_lines, logger)
    if header_size is None:
        logger.critical("impossible to file header size. stopping reading")
        sys.exit(1)

    # automatically extract data from header
    for i_line in range(header_size):
        # we only want line with =
        if HEADER_CHAR_VALUE not in raw_lines[i_line]:
            continue

        # split name and value to process it
        value_name, value = raw_lines[i_line].split(HEADER_CHAR_VALUE)

        # case value contain ')'
        if ")" in value:
            logger.debug(f"unwanted parenthesis in {value_name} {value}")
            value = re.sub(r"\)", "", value)

        # special variable
        if value_name in HEADER_SPECIAL:
            if value_name == "GPS Localisation":
                data["latitude"], data["longitude"] = get_localization(
                    value, conf, logger
                )
            if value_name == "Altitudes(m)":
                data["range"] = get_altitude(value, logger)

            continue

        # others variables. clean name et convert value
        logger.debug(f"try parsing {value_name} {value}")
        value_name = norm_value_name(value_name)
        try:
            value = ast.literal_eval(value)
        except (SyntaxError, ValueError):
            pass
        data[value_name] = value

    return data


def read_columns(file_, data, conf, logger):
    """read the data store as columns"""
    # get the number of columns to fix types
    with open(file_, encoding=conf["file_encoding"]) as f_id:
        try:
            header = int(f_id.readline().strip().split("=")[1])
        except ValueError:
            header = data["HeaderSize"]
        count = 0
        while count <= header:
            line = f_id.readline()
            count += 1

    col_names = [col for col in line.strip().split(FILE_SEP)]
    col_dtypes = ["f4"] * (len(col_names) - 1)
    col_dtypes = [dt.datetime] + col_dtypes

    logger.debug(f"available columns {col_names}")
    logger.debug("reading columns")

    columns = np.genfromtxt(
        file_,
        encoding=conf["file_encoding"],
        skip_header=header + 2,
        delimiter=FILE_SEP,
        missing_values=RAW_DATA_MISSING,
        filling_values=conf["missing_float"],
        names=col_names,
        dtype=col_dtypes,
        converters={0: convert_time_str, 3: convert_wiper},
        invalid_raise=False,
    )

    logger.debug(f"columns read : {columns.dtype.names}")

    return columns


def create_1d_var(raw_data, data, var_names, conf, logger):
    """extract 1d var to store them into dict"""

    logger.debug("reading 1d variables")

    for var in var_names:
        name = var[0]
        col_names = var[1]

        logger.debug(f"reading {name}")

        for col in col_names:
            try:
                data[name] = raw_data[col]
            except ValueError:
                logger.debug(f"column {col} not found")
                continue

            logger.debug("column found")

        # case column was not found
        if name not in data:
            data[name] = np.ones((raw_data.size,)) * conf["missing_float"]

    return data


def create_2d_var(raw_data, data, list_vars, conf, logger):
    """merge several columns of the ndarray into a 2d variable"""

    # get list of column names
    column_names = [col[0] for col in raw_data.dtype.descr]

    for var in list_vars:
        var_name = var[0]
        col_names = var[1]

        logger.debug(f"processing {var_name} variables (possible pattern {col_names})")

        # find corresponding columns
        # --------------------------------------------------------------------
        col_2_join = []
        for col_name in col_names:
            # get columns which have the string in their name
            col_2_join = col_2_join + [
                col for col in column_names if col.startswith(col_name)
            ]

        # create array and fill it
        # --------------------------------------------------------------------
        var_2d = (
            np.ones((raw_data.size, data["range"].shape[0])) * conf["missing_float"]
        )

        if len(col_2_join) != 0:
            logger.debug(f"corresponding columns found : {col_2_join}")
            for index, col in enumerate(col_2_join):
                var_2d[:, index] = raw_data[col]
                logger.debug(f"removing column {col} from processing")
                column_names.remove(col)

            # make sure the missing values are what we want
            var_2d[np.isnan(var_2d)] = conf["missing_float"]
        else:
            logger.error(f"no column found corresponding to {var_name} ({col_names})")

            logger.debug(f"remaining available columns {column_names}")

        data[var_name] = var_2d

    return data


def extract_time(raw_data, logger):
    """As the name of the time column could vary we search for the right one"""

    for time_var in VAR_TIME:
        try:
            data = raw_data[time_var]
            logger.debug(f"using {time_var} column for time")
            return data
        except ValueError:
            logger.debug(f"column {time_var} doesn't exists")
            continue

    # if we reach this point, it means we didn't
    # found the time, the reader should stop
    logger.critical("couldn't find time variable. Quitting")
    sys.exit(1)


def read_data(list_files, conf, logger):
    """main function"""

    data = {}

    # get specific configuration
    # ------------------------------------------------------------------------
    data["time_resol"] = 10

    # checking conf parameters
    # -------------------------------------------------------------------------
    # encoding of file, if not defined use utf8
    if "file_encoding" not in conf:
        logger.info("No encoding defined for using %s", DEFAULT_ENCODING)
        conf["file_encoding"] = DEFAULT_ENCODING
    if "inverse_vert_wind" not in conf:
        logger.info("No inverse_vert_wind defined using %s", DEFAULT_INVERSE_VERT_WIND)
        conf["inverse_vert_wind"] = DEFAULT_INVERSE_VERT_WIND
    if "lon" not in conf:
        logger.error("default lon should be provided in conf file")
        sys.exit(1)
    if "lat" not in conf:
        logger.error("default lat should be provided in conf file")
        sys.exit(1)

    # read data from file(s)
    # ------------------------------------------------------------------------
    tmp_list = []
    for i_file, file_ in enumerate(list_files):
        if i_file == 0:
            data = read_header_data(file_, conf, data, logger)

        tmp_list.append(read_columns(file_, data, conf, logger))

    # merge data
    raw_data = merge_structured_arrays(tmp_list)

    # extract and process time var
    # ------------------------------------------------------------------------
    data["time"] = extract_time(raw_data, logger)

    # time is at end of measurements, we want it at end
    if data["time"].size == 1:
        data["start_time"] = data["time"] - dt.timedelta(seconds=data["time_resol"])
    else:
        data["start_time"] = np.array(
            [d - dt.timedelta(seconds=data["time_resol"]) for d in data["time"]]
        )

    # time bounds
    data["nv"] = 2
    data["time_bounds"] = np.ones(
        (data["time"].size, data["nv"]), dtype=np.dtype(dt.datetime)
    )
    data["time_bounds"][:, 0] = data["start_time"]
    data["time_bounds"][:, 1] = data["time"]

    # extract 1d data
    # ------------------------------------------------------------------------
    data = create_1d_var(raw_data, data, VAR_1D, conf, logger)

    # merge data which need it into 2d array
    # ------------------------------------------------------------------------
    logger.debug("merging columns into 2d variables")
    data = create_2d_var(raw_data, data, VAR_2D, conf, logger)

    # calculate missing variables
    # ------------------------------------------------------------------------
    data["u"] = -1.0 * data["ws"] * np.sin(np.deg2rad(data["wd"]))
    data["v"] = -1.0 * data["ws"] * np.cos(np.deg2rad(data["wd"]))

    # W is given positive downward we prefer it upward
    # ------------------------------------------------------------------------
    data["w"] = -1.0 * data["w"]
    if conf["inverse_vert_wind"]:
        logger.debug("inverting vertical wind")
        data["w"] = -1.0 * data["w"]

    return data
