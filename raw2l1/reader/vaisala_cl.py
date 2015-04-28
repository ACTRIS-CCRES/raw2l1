# -*- coding: utf8 -*-

from __future__ import print_function, absolute_import, division

import numpy as np
import datetime as dt
import sys
from tools.utils import chomp

# brand and model of the LIDAR
BRAND = 'vaisala'
MODEL = 'CL31 & CL51'

# Parameters
FMT_DATE = "-%Y-%m-%d %H:%M:%S"
FILE_HEADERS = ["-Ceilometer Logfile", "-File created:"]
MSG_NB_LINES = {
    1: 6,
    2: 7,
}

# link between integer in acquisition configuration line and real values
# range resolution in meters
RANGE_RESOL = {
    1: 10,
    2: 20,
    3: 5,
    4: 5,
    5: -9,
    6: 10,
    8: -9
}
# number of vertical gates
RANGE_GATES = {
    1: 770,
    2: 385,
    3: 1500,
    4: 770,
    5: -9,
    6: 1540,
    8: -9,
}

# line of data according to data message type
STATE_MSG_LINE = {
    1: 3,
    2: 4,
}
RCS_MSG_LINE = {
    1: 4,
    2: 5,
}

# Fixed variables dimensions
CBH_DIM = 3
CLH_DIM = 5

# MISSING/FILLING values
MISSING_INT = -9
MISSING_FLT = np.nan

# constant
RCS_BYTES_SIZE = 5
RCS_FACTOR = 1e-8
DEG_TO_K = 273.15
CBH_ALT_FACTOR = 10.
SUM_BCKSCATTER_FACTOR = 1.E-4


def get_file_lines(filename, logger):
    """
    read all lines of a given file and remove carriage return from
    all lines
    """

    try:
        with open(filename, 'rb') as f_id:
            logger.debug("reading " + filename)
            lines = chomp(f_id.readlines())
    except:
        logger.error("Impossible to open file " + filename)
        return None

    return lines


def count_msg_to_read(list_files, logger):
    """
    to a first reading of the CL31 file to determine the number
    of data messages which need to be read
    """

    n_data_msg = 0

    # loop over filenames to read to count the number of messages
    # data message start with a date using the format "-%Y-%m-%d %H:%M:%S"
    for ifile in list_files:

        lines = get_file_lines(ifile, logger)
        for line in lines:
            try:
                dt.datetime.strptime(line, FMT_DATE)
                n_data_msg += 1
            except:
                continue

    logger.info("%d data messages to read" % n_data_msg)

    return n_data_msg


def get_range_resol(conf_msg, logger):
    """
    Extract vertical range resolution from configuration message line
    """
    try:
        int_coding = int(conf_msg[8:9])
        range_resol = RANGE_RESOL[int_coding]
        logger.debug("range resolution: %d m" % range_resol)
    except Exception, err:
        logger.warning("Problem reading range resolution: " + repr(err))
        return None

    return range_resol


def get_range_ngates(conf_msg, logger):
    """
    Extract the number of gates from configuration message line
    """

    try:
        int_coding = int(conf_msg[8:9])
        range_ngates = RANGE_GATES[int_coding]
        logger.debug("number of vertical gates: %d" % range_ngates)
    except Exception, err:
        logger.warning("Problem reading number of vertical gates " +
                       repr(err))
        return None

    return range_ngates


def get_msg_type(conf_msg, logger):
    """
    Extract from acquisition configuration line if the file contains
    message of type 1 or 2 (without or with sky state)
    """

    msg_type = int(conf_msg[7:8])

    if msg_type == 1:
        logger.info("file contains messages of type 1 (without sky state)")
    elif msg_type == 2:
        logger.info("file contains messages of type 2 (with sky state)")
    else:
        logger.error("problem determining type of message")
        msg_type = None

    return msg_type


def get_msg_nb_lines(msg_number):
    """
    based ont the configuration read return the number of lines of a data
    message
    """

    return MSG_NB_LINES[msg_number]


def calc_range(resol, n_gates):
    """
    calculate range variable based on resolution and number of gates
    """

    range_vect = np.array(range(n_gates), dtype=np.float)

    return range_vect * np.float(resol) + np.float(resol / 2)


def check_range(data, data_dim, logger):
    """
    check we determining range was a success
    """

    # Test if the msg contains retrodiffusion profiles
    if data_dim['range'] == -9 or data['range_resol'] == -9:
        logger.error("according to the configuration read " +
                     "the file doesn't contains retrodiffusion " +
                     "profiles. Trying next message")
        range_ok = False
        # Test if we manage to read resol anf number of gates
    elif data_dim['range'] is None or data['range_resol'] is None:
        logger.error("problem encountered reading range configuration." +
                     " Trying next message")
        range_ok = False
    else:
        range_ok = True

    return range_ok


def check_msg_type(data, logger):
    """
    check if determining message type was a success
    """

    # test if message type could be determine
    if data['msg_type'] is None:
        msg_ok = False
        logger.error("Could not determine type of message in file")
    else:
        msg_ok = True

    return msg_ok, data


def get_acq_conf(filename, data, data_dim, logger):
    """
    extract acquisition configuration from a data message
    (range resolution and number of vertical gates)
    """

    lines = get_file_lines(filename, logger)
    n_lines = len(lines)
    i_line = 0
    range_ok = False
    msg_ok = False

    conf_msg = None
    while i_line <= n_lines:

        try:
            dt.datetime.strptime(lines[i_line], FMT_DATE)
            conf_msg = lines[i_line + 1]
        except:
            conf_msg = None
            i_line += 1
            continue

        data_dim['range'] = get_range_ngates(conf_msg, logger)
        data['range_resol'] = get_range_resol(conf_msg, logger)

        # check if reading of range was a success
        range_ok = check_range(data, data_dim, logger)
        if range_ok:
            data['range'] = calc_range(data['range_resol'], data_dim['range'])

        # Check if reading of message type is a success
        data['msg_type'] = get_msg_type(conf_msg, logger)
        msg_ok, data = check_msg_type(data, logger)

        if range_ok and msg_ok:
            break

    # Read instrument/sofware id
    data['instrument_id'] = conf_msg[1:4]
    data['software_id'] = conf_msg[4:7]

    # if we are not able to read range in the file
    if not range_ok:
        logger.critical("Impossible to read range configuration in " +
                        filename + ". Stopping Raw2L1")
        sys.exit(1)

    if not msg_ok:
        logger.critical("impossible to determine type of message in " +
                        filename + ". Stopping Raw2L1")
        sys.exit(1)

    return data, data_dim


def init_data(data, data_dim, logger):
    """
    declare size of the numpy arraies and initialiase it
    """

    # Dimension variables
    # -------------------------------------------------------------------------
    data['time'] = np.ones((data_dim['time'],),
                           dtype=np.dtype(dt.datetime)) * np.nan
    data['cbh_layer'] = np.array([x + 1 for x in xrange(CBH_DIM)])
    data['clh_layer'] = np.array([x + 1 for x in xrange(CLH_DIM)])

    # Time dependant variables
    # -------------------------------------------------------------------------
    data['scale'] = np.ones((data_dim['time'],),
                            dtype=np.float32) * MISSING_FLT
    data['laser_temp'] = np.ones((data_dim['time'],),
                                 dtype=np.float32) * MISSING_FLT
    data['laser_energy'] = np.ones((data_dim['time'],),
                                   dtype=np.float32) * MISSING_FLT
    data['bckgrd_rcs_0'] = np.ones((data_dim['time'],),
                                   dtype=np.float32) * MISSING_FLT
    data['window_transmission'] = np.ones((data_dim['time'],),
                                          dtype=np.float32) * MISSING_FLT
    data['integrated_rcs_0'] = np.ones((data_dim['time'],),
                                       dtype=np.float32) * MISSING_FLT

    # Time, layer dependant variables
    # -------------------------------------------------------------------------
    data['cbh'] = np.ones((data_dim['time'], CBH_DIM),
                          dtype=np.float32) * MISSING_FLT
    data['clh'] = np.ones((data_dim['time'], CLH_DIM),
                          dtype=np.float32) * MISSING_FLT
    data['cloud_amount'] = np.ones((data_dim['time'], CLH_DIM),
                                   dtype=np.int) * MISSING_INT

    # Time, range dependent variables
    # -------------------------------------------------------------------------
    data['rcs_0'] = np.ones((data_dim['time'], data_dim['range']),
                            dtype=np.float32) * MISSING_FLT
    data['pr2'] = np.ones((data_dim['time'], data_dim['range']),
                          dtype=np.float32) * MISSING_FLT

    return data


def get_state_line_nb_in_msg(msg_type):
    """
    based on the configuration of the message type return the
    line number in data message containing ceilometer state
    """

    return STATE_MSG_LINE[msg_type]


def get_rcs_line_nb_in_msg(msg_type):
    """
    based on the configuration of the message type return the
    line number in data message containing ceilometer state
    """

    return RCS_MSG_LINE[msg_type]


def read_scalar_vars(data, msg, msg_type, logger):
    """
    extract scalar variables from data message
    """

    line_to_read = get_state_line_nb_in_msg(data['msg_type'])
    line = msg[line_to_read]

    return np.float(line.split()[6])


def read_time_dep_vars(data, ind, msg, msg_type, logger):
    """
    read time only dependent variables
    """

    line_to_read = get_state_line_nb_in_msg(data['msg_type'])
    params = msg[line_to_read].split()

    data['scale'][ind] = np.float(params[0])
    data['laser_energy'][ind] = np.float(params[3])
    data['laser_temp'][ind] = np.float(params[4])
    data['window_transmission'][ind] = np.float(params[5])
    data['bckgrd_rcs_0'][ind] = np.float(params[7])
    data['integrated_rcs_0'][ind] = np.float(params[9]) * SUM_BCKSCATTER_FACTOR

    return data


def read_cbh_msg(data, ind, msg, logger):
    """
    extract CBH
    """

    # get the number of cloud layer
    if msg[2][0] == '/':
        logger.warning("cloud data missing for message %d" % ind)
        return data
    else:
        layer_detected = int(msg[2][0])

    # get the altitude in the file
    cld_alt = msg[2].split(' ')[1:4]

    if layer_detected > 0 and layer_detected <= 4:
        data['cbh'][ind, 0] = np.float(cld_alt[0])
    if layer_detected > 1 and layer_detected <= 4:
        data['cbh'][ind, 1] = np.float(cld_alt[1])
    if layer_detected == 3:
        data['cbh'][ind, 2] = np.float(cld_alt[2])

    return data


def read_clh_msg(data, ind, msg, logger):
    """
    extract CLH
    """

    # get the number of cloud layer
    cld_line = msg[3]
    cld_detect = [int(x) for x in cld_line.split()[0::2]]
    cld_alt = cld_line.split()[1::2]

    for i_alt in xrange(CLH_DIM):
        if cld_detect[i_alt] >= 1 and cld_detect[i_alt] <= 8:
            data['clh'][ind][i_alt] = (np.float(cld_alt[i_alt]) *
                                       CBH_ALT_FACTOR)
            data['cloud_amount'] = cld_detect[i_alt]

    return data


def read_cbh_vars(data, ind, msg, logger):
    """
    Read the altitude of the 3 cloud layer in a data message
    """

    # reading of CBH depends on the kind of data message type
    data = read_cbh_msg(data, ind, msg, logger)
    if data['msg_type'] == 2:
        data = read_clh_msg(data, ind, msg, logger)

    return data


def read_rcs_var(data, ind, msg, logger):
    """
    read the rcs value in a data msg
    """

    # get line a of the message containing RCS based on CL31 conf
    line_to_read = get_rcs_line_nb_in_msg(data['msg_type'])
    # size of the profile to read
    rcs_size = data['range'].size
    # extract line containing rcs
    rcs_line = msg[line_to_read]

    tmp = [int(rcs_line[s * RCS_BYTES_SIZE:s * RCS_BYTES_SIZE +
               RCS_BYTES_SIZE], 16) for s in range(rcs_size)]

    data['rcs_0'][ind][:] = np.array(tmp, dtype=np.float32)

    return data


def read_vars(lines, data, time_ind, logger):
    """
    read all available variables in one file
    """

    n_lines = len(lines)
    i_line = 0
    msg_n_lines = get_msg_nb_lines(data['msg_type'])

    # loop over the lines
    while i_line < n_lines:

        # reject header lines
        if lines[i_line] in FILE_HEADERS:
            i_line += 1
            continue

        # Try finding line with time stamp
        try:
            data['time'][time_ind] = dt.datetime.strptime(lines[i_line],
                                                          FMT_DATE)
        except:
            i_line += 1
            continue

        msg = lines[i_line:i_line + msg_n_lines]
        logger.debug("processing data message %d" % (time_ind + 1))

        # read scalar variables (one time)
        if time_ind == 0:
            logger.debug("reading tilt angle")
            data['tilt_angle'] = read_scalar_vars(data, msg,
                                                  data['msg_type'], logger)

        # read time only dependent variables
        logger.debug("reading time only dependent variables")
        data = read_time_dep_vars(data, time_ind, msg,
                                  data['msg_type'], logger)

        # read CBH
        logger.debug("reading cbh/clh")
        data = read_cbh_vars(data, time_ind, msg, logger)

        # read rcs
        logger.debug("reading rcs")
        data = read_rcs_var(data, time_ind, msg, logger)

        # Add number of line of a message to lines counter
        i_line += msg_n_lines
        time_ind += 1

    return time_ind, data


def read_data(list_files, conf, logger):
    """
    Raw2L1 plugin to read data of the vaisala CL31
    """

    # analyse file to read to determine the size of the time variable
    # -------------------------------------------------------------------------
    data = {}
    data_dim = {}
    logger.info("analysing input files to get the configuration")
    data_dim['time'] = count_msg_to_read(list_files, logger)

    # Get range and vertical resolution from first file
    logger.info("analyzing first file to determine acquisition configuration")
    data, data_dim = get_acq_conf(list_files[0], data, data_dim, logger)

    logger.info("initialising data arraies")
    data = init_data(data, data_dim, logger)

    # Reading all the data
    # -------------------------------------------------------------------------
    logger.info("reading files")
    time_ind = 0
    nb_files_read = 0
    for ifile in list_files:

        # try reading the file
        lines = get_file_lines(ifile, logger)
        if lines is None:
            logger.warning("trying next file")
            continue

        nb_files_read += 1

        # reading data in the file
        time_ind, data = read_vars(lines, data, time_ind, logger)

    # Final calculation on whole profiles
    # -------------------------------------------------------------------------
    data['pr2'] = data['rcs_0']*RCS_FACTOR*data['range']

    return data
