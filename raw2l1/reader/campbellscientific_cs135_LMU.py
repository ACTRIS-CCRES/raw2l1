# -*- coding: utf-8 -*-


import numpy as np
import datetime as dt
import sys
import re
import configparser
from tools.utils import chomp

# brand and model of the LIDAR
BRAND = "campbell scientific"
MODEL = "CS135"

CONF_MSG_REGEX = r"CS.\d{6}"
DEFAULT_ENCODING = "utf8"

MSG_TYPE_PROF = [2, 4, 6]
MSG_TYPE_NOPROF = [1, 3, 5]
MSG_TYPE_LINES = {1: 3, 2: 5, 3: 4, 4: 6, 5: 5, 6: 7}

RANGE_DIM = 2048
RANGE_RESOL = 5
CBH_DIM = 4
CLH_DIM = 5
MLH_DIM = 3

PULSE_FACTOR = 1000.0

RCS_BYTES_SIZE = 5
RCS_FACTOR = 1e-8
DEG_TO_K = 273.15
CLH_ALT_FACTOR = 10.0
SUM_BCKSCATTER_FACTOR = 1.0e-4

MSG_TIMESTAMP_FMT = (
    "can't read data without timestamp format"
    + " in conf file. Add timestamp_fmt value in "
    + "reader_conf section"
)


def check_input(conf, logger):
    """
    check if the required parameter are available
    """

    # check if the timestamp format in available in conf file
    try:
        timestamp_fmt = conf["timestamp_fmt"]
    except configparser.NoSectionError:
        logger.critical("101 configuration file MUST have a reader_conf section")
        sys.exit(2)
    except configparser.NoOptionError:
        logger.critical("101 reader_conf section MUST have a timestamp_fmt option")
        sys.exit(2)

    logger.info("using timestamp format: %s", timestamp_fmt)

    return timestamp_fmt


def get_file_lines(filename, conf, logger):
    """
    read all lines of a given file and remove carriage return from
    all lines
    """

    try:
        with open(filename, "r", encoding=conf["file_encoding"]) as f_id:
            logger.debug("reading %s", filename)
            lines = chomp(f_id.readlines())
    except IOError:
        logger.error("109 Impossible to open file %s", filename)
        return None

    return lines


def count_msg_to_read(list_files, date_fmt, conf, logger):
    """
    count the number of data message in all files to read
    """

    n_data_msg = 0

    # loop over filenames to read to count the number of messages
    # data message start with a date which format is define in the conf file
    for ifile in list_files:
        lines = get_file_lines(ifile, conf, logger)
        for line in lines:
            try:
                dt.datetime.strptime(line, date_fmt)
                n_data_msg += 1
            except ValueError:
                continue

    logger.info("%d data messages to read", n_data_msg)

    return n_data_msg


def init_data(data, time_dim, conf, logger):
    """
    Initialize the arraies in data dict where data are read
    """

    missing_int = conf["missing_int"]
    missing_float = conf["missing_float"]

    # scalar variables
    # data["instrument_id"] = ""
    # data["os"] = ""
    # data["msg_type"] = -1
    data["range_resol"] = -1
    data["range_dim"] = -1

    # dimension
    data["time"] = np.ones((time_dim), dtype=np.dtype(dt.datetime))
    data["range"] = RANGE_RESOL * np.arange(1, RANGE_DIM + 1)
    data["cbh_layer"] = np.arange(CBH_DIM)
    data["clh_layer"] = np.arange(CLH_DIM)
    data["mlh_layer"] = np.arange(MLH_DIM)

    # 1dim variables
    data["scale"] = np.ones((time_dim,), dtype=np.int) * missing_int
    data["laser_energy"] = np.ones((time_dim,), dtype=np.int) * missing_int
    data["laser_temp"] = np.ones((time_dim,), dtype=np.float32) * missing_float
    data["tilt_angle"] = np.ones((time_dim,), dtype=np.int) * missing_int
    data["bckgrd_rcs_0"] = np.ones((time_dim,), dtype=np.float32) * missing_float
    data["laser_pulse"] = np.ones((time_dim,), dtype=np.float32) * missing_float
    data["sample_rate"] = np.ones((time_dim,), dtype=np.int) * missing_int
    data["integrated_rcs_0"] = np.ones((time_dim,), dtype=np.float32) * missing_float
    data["window_transmission"] = np.ones((time_dim,), dtype=np.int) * missing_int
    data["vertical_visibility"] = np.ones((time_dim,), dtype=np.int) * missing_int
    data["highest_signal_received"] = np.ones((time_dim,), dtype=np.int) * missing_int
    data["alarm"] = np.ndarray((time_dim,), dtype="S1")
    data["info_flags"] = np.ndarray((time_dim,), dtype="S12")

    # 2dim variables
    data["cbh"] = np.ones((time_dim, CBH_DIM), dtype=np.int) * missing_int
    data["clh"] = np.ones((time_dim, CLH_DIM), dtype=np.int) * missing_int
    data["cloud_amount"] = np.ones((time_dim, CLH_DIM), dtype=np.int) * missing_int
    data["mlh"] = np.ones((time_dim, MLH_DIM), dtype=np.int) * missing_int
    data["mlh_qf"] = np.ones((time_dim, MLH_DIM), dtype=np.int) * missing_int
    data["rcs_0"] = np.ones((time_dim, RANGE_DIM), dtype=np.float32) * missing_float

    return data


def read_header(line, data, logger):
    """
    Read header of message:
    ex: \x01CS0008006\x02
    """

    msg_found = False

    # get conf string
    conf_str = re.search(CONF_MSG_REGEX, line)
    if conf_str is not None:
        msg_found = True
        conf_msg = conf_str.group()
        logger.debug("header message %s", conf_msg)
        data["instrument_id"] = conf_msg[0:3]
        data["os"] = conf_msg[3:6]
        data["msg_type"] = int(conf_msg[6:9])

    return msg_found, data


def read_cbh(line, data, ind, logger):
    """
    read the line containing alarm, cbh, window transmission and flags
    ex: 10 099 03733 ///// ///// ///// 000000000000
    """
    elts = line.split()
    data["alarm"][ind] = elts[0][1]
    nlayers = elts[0][0]
    if nlayers != "/":
        # print(elts[0][0])
        nlayers = int(elts[0][0])

        data["window_transmission"][ind] = np.int(elts[1])

        # number of CBH depends on nlayers value
        if 1 <= nlayers <= 4:
            data["cbh"][ind, 0] = float(elts[2])
        if 2 <= nlayers <= 4:
            data["cbh"][ind, 1] = float(elts[3])
        if 3 <= nlayers <= 4:
            data["cbh"][ind, 2] = float(elts[4])
        if nlayers == 4:
            data["cbh"][ind, 3] = float(elts[5])
        if nlayers == 5:
            data["vertical_visibility"][ind] = float(elts[2])
            data["highest_signal_received"][ind] = float(elts[3])

    # flags
    data["info_flags"][ind] = elts[6]

    return data


def read_laser(line, data, ind, logger):
    """
    read the line containing data about the laser
    ex: 00100 05 2048 100 +39 06 0028 0020 30 000
    """

    elts = line.split()

    data["scale"][ind] = np.int(elts[0])

    # range_dim and range_resol are read but they seems to always be
    # 5m and 2048 gates
    data["range_resol"] = np.int(elts[1])
    data["range_dim"] = np.int(elts[2])

    data["laser_energy"][ind] = np.int(elts[3])
    data["laser_temp"][ind] = float(elts[4]) + DEG_TO_K

    data["tilt_angle"] = np.int(elts[5])
    data["bckgrd_rcs_0"][ind] = float(elts[6])
    data["laser_pulse"][ind] = float(elts[7]) / PULSE_FACTOR
    data["sample_rate"][ind] = np.int(elts[8])
    data["integrated_rcs_0"][ind] = float(elts[9])

    return data


def read_profile(line, data, ind, logger):
    """
    read profile data line (2048 x 5 bytes) 20-bit HEX ASCII
    """

    tmp = np.array(
        [
            int(line[s * RCS_BYTES_SIZE : s * RCS_BYTES_SIZE + RCS_BYTES_SIZE], 16)
            for s in range(RANGE_DIM)
        ]
    )

    # Each sample is coded with a 20-bit HEX ASCII character set
    # msb nibble and bit first, 2's complement
    corr_2s_needed = tmp > 2**19
    if any(corr_2s_needed):
        tmp[corr_2s_needed] = -(2**20 - tmp[corr_2s_needed])

    # corr_2s_needed = tmp > 1048575
    # if any(corr_2s_needed):
    #     tmp[corr_2s_needed] = tmp[corr_2s_needed] - 2**40

    data["rcs_0"][ind, :] = np.array(tmp, dtype=np.float32)[:] * RCS_FACTOR

    return data


def read_sky_condition(line, data, ind, logger):
    """
    read sky condition line
    ex: 8 0037  0 ////  0 ////  0 ////  0 ////
    """

    elts = line.strip().split()

    data["cloud_amount"][ind] = np.array(elts[0::2], dtype=np.int)

    tmp = elts[1::2]

    for level, ca in enumerate(elts[0::2]):
        ca_int = int(ca)
        if 1 <= ca_int <= 8:
            data["clh"][ind, level] = float(tmp[level]) * CLH_ALT_FACTOR

    return data


def read_mlh(line, data, ind, logger):
    """
    read MLH line
    ex: 01076 00003 02740 00003 ///// 00000
    """

    elts = line.split()

    data["mlh_qf"] = elts[1::2]

    for i, mlh in enumerate(elts[0::2]):
        try:
            data["mlh"][ind, i] = mlh
        except ValueError:
            pass

    return data


def is_msg_type_ok(msg_type, filename, logger):
    """
    check type of message to read
    """

    if 101 <= msg_type <= 112:
        logger.error(
            "102 unable to read these data messages in '%s' You should able to read it with vaisala CL51 reader",
            filename,
        )
        return False
    elif 113 <= msg_type <= 114:
        logger.error(
            "102 unable to read these data messages in '%s'. You should able to read it with vaisala CL51 reader",
            filename,
        )
        return False
    elif 1 <= msg_type <= 6:
        return True
    else:
        logger.critical("103 data message type unknown in '%s'", filename)


def get_msg_type(data, list_files, date_fmt, conf, logger):
    """
    try to determine the type of data message
    """

    # tmp = {}
    msg_type_found = False
    for f in list_files:
        lines = get_file_lines(f, conf, logger)

        for i, line in enumerate(lines):
            try:
                dt.datetime.strptime(line, date_fmt)
            except ValueError:
                continue

            msg_found, tmp = read_header(lines[i + 1], data, logger)
            msg_type = tmp["msg_type"]

            if msg_found and is_msg_type_ok(msg_type, f, logger):
                msg_type_found = True
                break

    if msg_type_found:
        return msg_type, data
    else:
        logger.critical(
            "106 impossible to determine data messages type in any input file"
        )
        sys.exit(2)


def read_msg_001(msg, data, ind, logger):
    """
    read data message 001
    """

    data = read_cbh(msg[1], data, ind, logger)

    return data


def read_msg_002(msg, data, ind, logger):
    """
    read data message 002
    """

    data = read_cbh(msg[1], data, ind, logger)
    data = read_laser(msg[2], data, ind, logger)
    data = read_profile(msg[3], data, ind, logger)

    return data


def read_msg_003(msg, data, ind, logger):
    """
    read data message 003
    """

    data = read_cbh(msg[1], data, ind, logger)
    data = read_sky_condition(msg[2], data, ind, logger)

    return data


def read_msg_004(msg, data, ind, logger):
    """
    read data message 004
    """

    data = read_cbh(msg[1], data, ind, logger)
    logger.debug("cbh read")
    data = read_sky_condition(msg[2], data, ind, logger)
    logger.debug("sky condition read")
    data = read_laser(msg[3], data, ind, logger)
    logger.debug("laser read")
    data = read_profile(msg[4], data, ind, logger)
    logger.debug("profile read")

    return data


def read_msg_005(msg, data, ind, logger):
    """
    read data message 005
    """

    data = read_cbh(msg[1], data, ind, logger)
    data = read_sky_condition(msg[2], data, ind, logger)
    data = read_mlh(msg[3], data, ind, logger)

    return data


def read_msg_006(msg, data, ind, logger):
    """
    read data message 006
    """

    data = read_cbh(msg[1], data, ind, logger)
    data = read_sky_condition(msg[2], data, ind, logger)
    data = read_laser(msg[3], data, ind, logger)
    data = read_mlh(msg[4], data, ind, logger)
    data = read_profile(msg[5], data, ind, logger)

    return data


def read_data(list_files, conf, logger):
    """
    Raw2L1 plugin to read data of the campbell scientific CS135
    """

    MSG_TYPE_READER = {
        1: read_msg_001,
        2: read_msg_002,
        3: read_msg_003,
        4: read_msg_004,
        5: read_msg_005,
        6: read_msg_006,
    }

    # check inputs in conf variable and timestamp format
    t_stamp_fmt = check_input(conf, logger)

    # encoding of file, if not defined use utf8
    if "file_encoding" not in conf:
        logger.info("No encoding defined for using %s", DEFAULT_ENCODING)
        conf["file_encoding"] = DEFAULT_ENCODING

    logger.info("counting number of data messages to read")
    time_dim = count_msg_to_read(list_files, t_stamp_fmt, conf, logger)

    data = {}

    msg_type, data = get_msg_type(data, list_files, t_stamp_fmt, conf, logger)
    logger.debug("message type : %d", msg_type)
    msg_len = MSG_TYPE_LINES[msg_type]
    logger.debug("message len : %d", msg_len)

    # initialize dict containing data
    logger.debug("initializing data arrays")
    data = init_data(data, time_dim, conf, logger)

    # loop over the list of files
    time_ind = 0
    for file_nb, filename in enumerate(list_files):
        logger.debug("reading file %02d", file_nb + 1)
        lines = get_file_lines(filename, conf, logger)
        logger.debug("number of lines : %d", len(lines))

        i_line = 0
        while i_line < len(lines):
            logger.debug("i_line : %d", i_line)

            try:
                timestamp = dt.datetime.strptime(lines[i_line], t_stamp_fmt)
            except ValueError:
                i_line += 1
                continue

            logger.debug("reading timestep: %s", repr(timestamp))
            logger.debug("reading message: %d", time_ind)

            # reading one data message
            data["time"][time_ind] = timestamp
            msg = lines[i_line + 1 : i_line + msg_len + 1]
            data = MSG_TYPE_READER[msg_type](msg, data, time_ind, logger)
            logger.debug("message read")

            # incrementing line number and timestep
            i_line += MSG_TYPE_LINES[msg_type] + 1
            time_ind += 1
    data["time_resolution"] = int(conf["time_resolution"])
    data["start_time"] = data["time"] - dt.timedelta(
        seconds=int(conf["time_resolution"])
    )
    return data
