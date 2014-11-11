# -*- coding: utf8 -*-

from __future__ import print_function, absolute_import, division

import numpy as np
import datetime as dt
import sys
from tools.utils import chomp

# brand and model of the LIDAR
BRAND = 'vaisala'
MODEL = 'CL31'

# Parameters
FMT_DATE = "-%Y-%m-%d %H:%M:%S"
FILE_HEADERS = ["-Ceilometer Logfile", "-File created:"]

# link between integer in acquisition configuration line and real values
# range resolution in meters
RANGE_RESOL = {
    1: 10,
    2: 20,
    3: 5,
    4: 5,
    5: -9,
}
# number of vertical gates
RANGE_GATES = {
    1: 770,
    2: 385,
    3: 1500,
    4: 770,
    5: -9,
}


def get_file_lines(filename, logger):
    """
    read all lines of a given file and remove carriage return from
    all lines
    """

    with open(filename, 'rb') as f_id:
        logger.debug("reading " + filename)
        lines = chomp(f_id.readlines())

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


def calc_range(resol, n_gates):
    """
    calculate range variable based on resolution and number of gates
    """

    range_vect = np.array(range(n_gates), dtype=np.float)

    return range_vect * np.float(resol) + np.float(resol / 2)


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

        if lines[i_line] in FILE_HEADERS:
            i_line += 1
            continue

        try:
            dt.datetime.strptime(lines[i_line], FMT_DATE)
            conf_msg = lines[i_line + 1]
        except:
            conf_msg = None
            i_line += 1
            continue

        data_dim['range'] = get_range_ngates(conf_msg, logger)
        data['range_resol'] = get_range_resol(conf_msg, logger)

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
            data['range'] = calc_range(data['range_resol'], data_dim['range'])

        data['msg_type'] = get_msg_type(conf_msg, logger)

        # test if message type could be determine
        if data['msg_type'] is None:
            msg_ok = False
            logger.error("Could not determine type of message in file")
        else:
            msg_ok = True

        if range_ok and msg_ok:
            break

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


def read_data(list_files, conf, logger):
    """
    Raw2L1 plugin to read data of the vaisala CL31
    """

    # analyse file to read to determine the size of the time variable
    #-------------------------------------------------------------------------
    data = {}
    data_dim = {}
    logger.info("analysing input files to get the configuration")
    data_dim['time'] = count_msg_to_read(list_files, logger)

    # Get range and vertical resolution from first file
    logger.info("analyzing first file to determine acquisition configuration")
    data, data_dim = get_acq_conf(list_files[0], data, data_dim, logger)

    sys.exit(1)

    return data
