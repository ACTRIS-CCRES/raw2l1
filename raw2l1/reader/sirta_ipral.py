#!/usr/bin/env python

"""
reader for raw data from SIRTA IPRAL LIDAR
the file format is based on LICEL file format
"""

import ast
import datetime as dt
import sys

import netCDF4 as nc
import numpy as np

LIST_LASER_TYPE = ["spectra", "brilliant", "qsmart"]


# brand and model of the LIDAR
BRAND = "Gordien Stratos"
MODEL = "IPRAL"

DATETIME_FMT = "{} {}"
DATE_FMT = "%d/%m/%Y %H:%M:%S"
TIME_FMT = "%H:%M:%S"

DEFAULT_ENCODING = "utf8"
N_HEADER_LINE = 3

MISSING_FLOAT = np.nan
MISSING_INT = -9

BCK_MIN_ALT_KEY = "bckgrd_min_alt"
BCK_MAX_ALT_KEY = "bckgrd_max_alt"
BCK_MIN_ALT = 50000
BCK_MAX_ALT = 60000

POLARIZATION = {"o": 0, "p": 1, "s": 2}

DEFAULT_RESOLUTION = 7.5

BCK_COMMENT_FMT = "calcultated between {:5d} m and {:5d} m"


def date_to_dt(date_num, date_units):
    """convert date np.array from datenum to datetime.datetime"""

    return nc.num2date(date_num, units=date_units, calendar="standard")


def get_channel_conf(conf, logger):
    """check configuration of channels and build the conf dict"""

    # associate channels to a number
    try:
        tmp_rcs = ast.literal_eval(conf["rcs"])
    except ValueError:
        logger.critical(
            "error parsing 'rcs' option in [reader_conf] in config file. quitting"
        )
        sys.exit(1)

    logger.debug("rcs %s %s", tmp_rcs)

    try:
        tmp_chan = ast.literal_eval(conf["channels"])
    except ValueError:
        logger.critical(
            "error parsing 'channels' option in [reader_conf] in config file. quitting"
        )
        sys.exit(1)

    logger.debug("channels id %s", tmp_chan)

    # check if the lists have the same number of elements
    if len(tmp_rcs) != len(tmp_chan):
        logger.critical(
            "error in configuration: 'channel' and 'rcs' options don't have the same number of elements. quitting"  # NOQA
        )
        sys.exit(1)

    # when we know the order of the variables in files we well need to add an index
    chan_conf = {
        "var_names": [f"rcs_{x:02d}" for x in tmp_rcs],
        "channels": tmp_chan,
        "index": [None] * len(tmp_rcs),
    }

    logger.debug("list of channels  : %s", chan_conf["channels"])
    logger.debug("list of variables : %s", chan_conf["var_names"])

    return chan_conf


def get_bck_alt(conf, logger):
    """get value of maximum and minimum altitude for background signal calculation
    if not define, use default value"""

    try:
        min_alt = ast.literal_eval(conf[BCK_MIN_ALT_KEY])
    except KeyError:
        min_alt = BCK_MIN_ALT
        logger.warning(
            "%s not defined in conf file using default value %d",
            BCK_MIN_ALT_KEY,
            BCK_MIN_ALT,
        )
    except ValueError:
        logger.critical(
            "error parsing '%s' option in [reader_conf] in config file. quitting",
            BCK_MIN_ALT_KEY,
            conf[BCK_MIN_ALT_KEY],
        )
        sys.exit(1)

    try:
        max_alt = ast.literal_eval(conf[BCK_MAX_ALT_KEY])
    except KeyError:
        min_alt = BCK_MAX_ALT
        logger.warning(
            "%s not defined in conf file using default value %d",
            BCK_MAX_ALT_KEY,
            BCK_MAX_ALT,
        )
    except ValueError:
        logger.critical(
            "error parsing '%s' option in [reader_conf] in config file. quitting",
            BCK_MAX_ALT_KEY,
            conf[BCK_MAX_ALT_KEY],
        )
        sys.exit(1)

    return min_alt, max_alt


def get_channel_index(file_id, n_chan, chan_conf, logger):
    """associate id of channel with rcs_XX variable of channels"""

    # skip header
    for i in range(N_HEADER_LINE):
        line = file_id.readline()
        print(i, line.strip())

    for i_chan in range(n_chan):
        line = file_id.readline()
        line_id = line.split()[-1]

        try:
            index = chan_conf["channels"].index(line_id)
        except ValueError:
            logger.warning("id %s not found in raw data", line_id)
            continue

        chan_conf["index"][index] = i_chan

    # check if we found at least one channel:
    uniq_index = set(chan_conf["index"])

    if len(uniq_index) == 1 and list(uniq_index) == [None]:
        logger.critical(
            "No requested channels in conf file could be identified.stopping code"
        )
        sys.exit(1)

    return chan_conf


def get_data_size(list_files, logger):
    """determine size of data to read"""

    # create dimensions dict
    data_dim = {}
    data_dim["time"] = 0
    data_dim["range"] = 0
    data_dim["n_chan"] = 0
    data_dim["nv"] = 2  # size for time bounds

    # loop over list of files
    for i_file, file_ in enumerate(list_files):
        try:
            f_id = open(file_, "rb")
        except OSError:
            logger.error("error trying to open %s", file_)
            continue

        # line 1 : name of file, we don't need it
        f_id.readline()

        # line 2 : date and time, we need it
        line = f_id.readline()
        elts = line.decode(DEFAULT_ENCODING).split()
        datetime_str = DATETIME_FMT.format(elts[1], elts[2])

        # try to parse date to check file is valid
        try:
            dt.datetime.strptime(datetime_str, DATE_FMT)
        except ValueError:
            logger.error("wrong time format in " + file_)
            continue

        data_dim["time"] += 1

        # line 3 : number of channels, we need it
        line = f_id.readline()
        elts = line.split()

        # read or check number of channels in file
        if i_file == 0:
            data_dim["n_chan"] = int(elts[4])
            logger.info("number of channels : %d", data_dim["n_chan"])
        else:
            tmp = int(elts[4])
            if tmp != data_dim["n_chan"]:
                logger.critical(
                    "number of channels was %d in previous file and is now %d in %s",
                    data_dim["n_chan"],
                    tmp,
                    file_,
                )
                sys.exit(1)

        logger.info("data contains %d channels", data_dim["n_chan"])

        # line 4 : get range from first channel description
        line = f_id.readline()
        elts = line.split()

        if i_file == 0:
            data_dim["range"] = int(elts[3])
            logger.info("size of range : %d", data_dim["range"])
        else:
            tmp = int(elts[3])
            if tmp != data_dim["range"]:
                logger.critical(
                    "size of range was %d in previous file and is now %d in %s",
                    data_dim["range"],
                    tmp,
                    file_,
                )
                sys.exit(1)

        f_id.close()

    # log dimensions
    logger.debug("dim time     : %d", data_dim["time"])
    logger.debug("dim range    : %d", data_dim["range"])
    logger.debug("dim channels : %d", data_dim["n_chan"])
    logger.debug("dim nv       : %d", data_dim["nv"])

    return data_dim


def init_data(data_dim, logger):
    """initialize dict containing ndarrays based on data dimension"""

    n_chan = data_dim["n_chan"]

    data = {}

    # dimensions
    data["time"] = np.empty((data_dim["time"],), dtype=np.dtype(dt.datetime))
    data["time_bounds"] = np.empty(
        (data_dim["time"], data_dim["nv"]), dtype=np.dtype(dt.datetime)
    )
    data["range"] = np.empty((data_dim["range"],), dtype=np.float32)

    # scalar values
    data["type1_shots"] = MISSING_FLOAT
    data["frequency"] = MISSING_FLOAT
    data["type2_shots"] = MISSING_FLOAT
    data["time_resol"] = MISSING_FLOAT
    data["zenith"] = MISSING_FLOAT
    data["range_resol"] = MISSING_FLOAT
    data["longitude"] = MISSING_FLOAT
    data["latitude"] = MISSING_FLOAT
    data["altitude"] = MISSING_FLOAT

    data["active"] = np.ones((n_chan,), dtype=int) * MISSING_INT
    data["detection_mode_ind"] = np.ones((n_chan,), dtype=int) * MISSING_INT
    data["detection_mode"] = np.array(["photocounting"] * n_chan)
    data["telescope"] = np.ones((n_chan,), dtype=int) * MISSING_INT
    data["n_range"] = np.ones((n_chan,), dtype=int) * MISSING_INT
    data["number_one"] = np.ones((n_chan,), dtype=int) * MISSING_INT
    data["voltage"] = np.ones((n_chan,), dtype=np.float32) * MISSING_FLOAT
    data["range_resol_vect"] = np.ones((n_chan,), dtype=np.float32) * MISSING_FLOAT
    data["wavelength"] = np.ones((n_chan,), dtype=np.float32) * MISSING_FLOAT
    data["polarization"] = np.array([str(MISSING_INT)] * n_chan, dtype=str)
    data["filter_wheel_position"] = (
        np.ones((n_chan,), dtype=int) * MISSING_INT
    )  # speficfic for IPRAL
    # unused column
    data["bin_shift"] = np.ones((n_chan,), dtype=int) * MISSING_INT
    data["bin_shift_dec"] = np.ones((n_chan,), dtype=int) * MISSING_INT
    data["adc_bits"] = np.ones((n_chan,), dtype=int) * MISSING_INT
    data["n_shots"] = np.ones((n_chan,), dtype=int) * MISSING_INT
    data["discriminator_level"] = np.ones((n_chan,), dtype=int) * MISSING_FLOAT
    data["adc_range"] = np.ones((n_chan,), dtype=np.float32) * MISSING_FLOAT

    # multi_dim vars
    for i_chan in range(data_dim["n_chan"]):
        data[f"rcs_{i_chan:02d}"] = (
            np.ones((data_dim["time"], data_dim["range"]), dtype=np.float32)
            * MISSING_FLOAT
        )
        data[f"bckgrd_rcs_{i_chan:02d}"] = (
            np.ones((data_dim["time"],), dtype=np.float32) * MISSING_FLOAT
        )

    return data


def read_header(file_id, data, data_dim, index, logger, date_only=False):
    """Extract data from file ASCII header"""

    # first line: filename (we don't need it)
    # ------------------------------------------------------------------------
    file_id.readline()

    # second line : datetime, localization and meteo
    # ------------------------------------------------------------------------
    logger.debug("reading header second line")
    line = file_id.readline().decode(DEFAULT_ENCODING)
    logger.debug("parsing : %s", line)
    elts = line.split()

    logger.debug("reading dates")
    datetime_start = DATETIME_FMT.format(elts[1], elts[2])
    datetime_end = DATETIME_FMT.format(elts[3], elts[4])

    data["time"][index] = dt.datetime.strptime(datetime_start, DATE_FMT)
    logger.debug("datetime: %s", data["time"][index])
    data["time_bounds"][index, 0] = data["time"][index]
    data["time_bounds"][index, 1] = dt.datetime.strptime(datetime_end, DATE_FMT)

    if date_only:
        logger.debug("reading only date")
        return data

    data["time_resol"] = (
        data["time_bounds"][index, 1] - data["time_bounds"][index, 0]
    ).total_seconds()
    data["altitude"] = float(elts[5])
    data["latitude"] = float(elts[6])
    data["longitude"] = float(elts[7])
    data["zenith"] = float(elts[8])

    # third line: nothing interesting to read ??
    # ------------------------------------------------------------------------
    line = file_id.readline().decode(DEFAULT_ENCODING)
    elts = line.split()
    data["type1_shots"] = float(elts[0])
    data["frequency"] = float(elts[1])
    data["type2_shots"] = float(elts[2])

    # channels description
    # ------------------------------------------------------------------------
    for i_chan in range(data_dim["n_chan"]):
        var_name = f"rcs_{i_chan:02d}"  # noqa: F841

        line = file_id.readline().decode(DEFAULT_ENCODING)
        logger.debug("parsing : %s", line.strip())
        elts = line.split()

        data["active"][i_chan] = int(elts[0])
        data["detection_mode_ind"][i_chan] = int(elts[1])
        # data['telescope'][i_chan] = int(elts[2]) # don't know what is this value
        data["n_range"][i_chan] = int(elts[3])
        data["number_one"][i_chan] = int(elts[4])
        data["voltage"][i_chan] = int(elts[5])
        data["range_resol_vect"][i_chan] = float(elts[6])
        data["wavelength"][i_chan] = int(elts[7].split(".")[0])
        data["polarization"][i_chan] = str(elts[7].split(".")[1])
        data["filter_wheel_position"][i_chan] = int(elts[8])
        # unused
        data["bin_shift"][i_chan] = float(elts[10])
        data["bin_shift_dec"][i_chan] = float(elts[11])
        data["adc_bits"][i_chan] = int(elts[12])
        data["n_shots"][i_chan] = int(elts[13])

        tmp = elts[15][0:2]
        if tmp == "BT":
            data["detection_mode"][i_chan] = "analog"
            data["adc_range"][i_chan] = float(elts[14])
        elif tmp == "BC":
            data["detection_mode"][i_chan] = "photocounting"
            data["discriminator_level"][i_chan] = float(elts[14])

        # telescope
        telescope_ind = int(elts[15][2::])
        if telescope_ind < 10:
            data["telescope"][i_chan] = 1
        else:
            data["telescope"][i_chan] = 2

    # check all range_resol is the same
    sort_range_resol = np.unique(data["range_resol_vect"])
    if len(sort_range_resol) == 1:
        data["range_resol"] = list(sort_range_resol)[0]
        logger.debug("range_resol: %s", data["range_resol"])
    else:
        logger.critical(
            "all channel don't have the same resolution : %s", sort_range_resol
        )
        sys.exit(1)

    return data


def read_profiles(file_id, data, data_dim, index, laser_type, logger):
    """read profile for each channel"""

    # skip header and channels descriptions
    active = {i_chan: True for i_chan in range(data_dim["n_chan"])}
    for i in range(N_HEADER_LINE):
        line = file_id.readline()

    for i in range(data_dim["n_chan"]):
        line = file_id.readline().decode(DEFAULT_ENCODING).strip()
        logger.debug("%2d %s", i, line)

        # check if some channel should be ignored
        if laser_type == "spectra" and "BT3 " in line:
            wheel_position = int(line.split()[8])
            if wheel_position != 6:  # noqa: PLR2004
                active[1] = False
                active[6] = False
                active[7] = False
                active[8] = False
                active[9] = False
        elif laser_type == "qsmart":
            # check if voltage is 0 meaning inactive channel
            voltage = int(line.split()[5])
            if voltage == 0:
                active[i] = False
        elif laser_type == "brilliant":
            active[2] = False
            active[3] = False
            active[4] = False
            active[5] = False
            active[6] = False
            active[7] = False
            active[8] = False
            active[9] = False
            active[12] = False
            active[13] = False
            active[14] = False
            active[15] = False

            voltage = int(line.split()[5])
            if voltage == 0:
                active[i] = False

    # skip empty line
    _ = file_id.readline()

    for i_chan in range(data_dim["n_chan"]):
        # check of channel is active
        if data["active"][i_chan] == 0:
            continue

        tmp_data = np.fromfile(file_id, dtype="i4", count=data_dim["range"])

        if active[i_chan] is False:
            continue

        shots = data["n_shots"][i_chan]

        if data["detection_mode"][i_chan] == "analog":
            max_range = data["adc_range"][i_chan]
            adc = data["adc_bits"][i_chan]
            data[f"rcs_{i_chan:02d}"][index, :] = (
                tmp_data / shots * max_range * 1000 / (2**adc - 1)
            )
            data[f"units_{i_chan:02d}"] = "mV"
        else:
            # It coincides with the ASCII converted by the Advanced Licel.exe
            # but it has no sense.
            # See Licel programming manual.pdf. Bins-per-microseconds number
            # from technical specifications 20 bins/microsec.
            reduction_factor = data["range_resol"] / DEFAULT_RESOLUTION
            data[f"rcs_{i_chan:02d}"][index, :] = tmp_data / (
                shots / (20 / reduction_factor)
            )
            data[f"units_{i_chan:02d}"] = "MHz"

        # jump over space between profiles
        _ = file_id.seek(file_id.tell() + 2)

    return data


def read_data(list_files, conf, logger):
    """Raw2L1 plugin to read raw data of SIRTA IPRAL LIDAR"""

    logger.info("Start reading of data using reader for %s %s", BRAND, MODEL)

    # get conf parameters
    # ------------------------------------------------------------------------
    missing_flt = conf["missing_float"]
    missing_int = conf["missing_int"]
    laser_type = conf["laser_type"]
    remove_bckgrd = False
    if "remove_bckgrd" in conf:
        if conf["remove_bckgrd"].lower() in ("true", "t", "yes", "y", "1"):
            remove_bckgrd = True
        else:
            remove_bckgrd = False

    # check type of laser
    if laser_type not in LIST_LASER_TYPE:
        logger.warning("unknown laser type %s", laser_type)

    # min and max alt for background signal calculation
    bck_min_alt, bck_max_alt = get_bck_alt(conf, logger)

    # associate channels and var_names
    # chan_conf = get_channel_conf(conf, logger)

    # determine size of data to read
    # ------------------------------------------------------------------------
    logger.info("determining size of var to read")
    data_dim = get_data_size(list_files, logger)

    for ind, file_ in enumerate(list_files):
        try:
            f_id = open(file_, "rb")
        except OSError:
            logger.error("error trying to open %s", file_)
            continue

        # identify line of channel in file
        # --------------------------------------------------------------------
        if ind == 0:
            # chan_conf = get_channel_index(f_id, data_dim['n_chan'], chan_conf, logger)
            # initialize data array
            logger.info("initializing data output array")
            data = init_data(data_dim, logger)
            # f_id.seek(0)

        # read header
        # --------------------------------------------------------------------
        date_only = False
        if ind != 0:
            date_only = True

        data = read_header(f_id, data, data_dim, ind, logger, date_only=date_only)

        # read data
        # --------------------------------------------------------------------
        logger.info("read data")

        # go back to start of file
        f_id.seek(0)

        # read profiles
        data = read_profiles(f_id, data, data_dim, ind, laser_type, logger)

        # end of reading
        # --------------------------------------------------------------------
        f_id.close()

    # final calculations
    # --------------------------------------------------------------------

    # determine range
    data["range"] = np.arange(1, data_dim["range"] + 1) * data["range_resol"]

    # add necessary dimensions
    data["n_chan"] = data_dim["n_chan"]
    data["nv"] = data_dim["nv"]  # for time bounds

    # convert polarization in values
    data["polarization"] = [POLARIZATION[val_] for val_ in data["polarization"]]

    # bacground alt filter
    bck_filter = (data["range"] > bck_min_alt) & (data["range"] < bck_max_alt)
    data["bckgrd_rcs_comment"] = BCK_COMMENT_FMT.format(bck_min_alt, bck_max_alt)

    # PR2 and background
    for i_chan in range(data_dim["n_chan"]):
        profiles = data[f"rcs_{i_chan:02d}"]
        square = np.square(data["range"])

        data[f"bckgrd_rcs_{i_chan:02d}"] = np.mean(profiles[:, bck_filter], axis=1)
        # remove background is needed
        if remove_bckgrd:
            logger.debug("removing bckgrd for chan %d", i_chan)
            profiles = (profiles.T - data[f"bckgrd_rcs_{i_chan:02d}"]).T

        data[f"rcs_{i_chan:02d}"] = profiles * square
        data[f"units_rcs_{i_chan:02d}"] = data[f"units_{i_chan:02d}"] + ".m^2"

    return data
