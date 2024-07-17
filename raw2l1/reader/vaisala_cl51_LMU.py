# -*- coding: utf8 -*-


import numpy as np
import datetime as dt
import sys
import re
from tools.utils import chomp, to_bool

# brand and model of the LIDAR
BRAND = "vaisala"
MODEL = "CL31 & CL51"

# Parameters
FMT_DATE = "-%Y-%m-%d %H:%M:%S"
FILE_HEADERS = ["-Ceilometer Logfile", "-File created:"]
CONF_MSG_REGEX = r"CL.\d{5}"
MSG_NB_LINES = {1: 6, 2: 7}
DEFAULT_ENCODING = "utf8"

# link between integer in acquisition configuration line and real values
# range resolution in meters
RANGE_RESOL = {1: 10, 2: 20, 3: 5, 4: 5, 5: -9, 6: 10, 8: -9}
# number of vertical gates
RANGE_GATES = {1: 770, 2: 385, 3: 1500, 4: 770, 5: -9, 6: 1540, 8: -9}

# line of data according to data message type
STATE_MSG_LINE = {1: 3, 2: 4}
RCS_MSG_LINE = {1: 4, 2: 5}

# Fixed variables dimensions
CBH_DIM = 3
CLH_DIM = 5

# constant
RCS_BYTES_SIZE = 5
RCS_FACTOR = 1e-8
DEG_TO_K = 273.15
FEET_TO_METERS = 0.3048
CLH_ALT_METERS_FACTOR = 10.0
CLH_ALT_FEET_FACTOR = 100.0
SUM_BCKSCATTER_FACTOR = 1.0e-4
OK_SCALE_VALUE = 100.0

# hexadecimal encoding of internal message, warning and error
ERR_HEX_MSG = [
    {"hex": 0x000000000001, "level": "STATUS", "msg": "undefined"},
    {"hex": 0x000000000002, "level": "STATUS", "msg": "undefined"},
    {"hex": 0x000000000004, "level": "STATUS", "msg": "undefined"},
    {"hex": 0x000000000008, "level": "STATUS", "msg": "undefined"},
    {"hex": 0x000000000010, "level": "STATUS", "msg": "undefined"},
    {"hex": 0x000000000020, "level": "STATUS", "msg": "Polling mode is on"},
    {"hex": 0x000000000040, "level": "STATUS", "msg": "Manual blower control"},
    {
        "hex": 0x000000000080,
        "level": "STATUS",
        "msg": "Units are meters if on, else feet",
    },
    {"hex": 0x000000000100, "level": "STATUS", "msg": "undefined"},
    {
        "hex": 0x000000000200,
        "level": "STATUS",
        "msg": "Manual data acquisition settings are effective",
    },
    {"hex": 0x000000000400, "level": "STATUS", "msg": "Self test in progress"},
    {"hex": 0x000000000800, "level": "STATUS", "msg": "Standby mode is on"},
    {"hex": 0x000000001000, "level": "STATUS", "msg": "Working from battery"},
    {"hex": 0x000000002000, "level": "STATUS", "msg": "Internal heater is on"},
    {"hex": 0x000000004000, "level": "STATUS", "msg": "Blower heater is on"},
    {"hex": 0x000000008000, "level": "STATUS", "msg": "Blower is on"},
    {"hex": 0x000000010000, "level": "WARNING", "msg": "undefined"},
    {
        "hex": 0x000000020000,
        "level": "WARNING",
        "msg": "Tilt angle > 45 degrees warning",
    },
    {"hex": 0x000000040000, "level": "WARNING", "msg": "Receiver warning"},
    {"hex": 0x000000080000, "level": "WARNING", "msg": "Laser monitor failure"},
    {"hex": 0x000000100000, "level": "WARNING", "msg": "Battery failure"},
    {
        "hex": 0x000000200000,
        "level": "WARNING",
        "msg": "Ceilometer engine board failure",
    },
    {"hex": 0x000000400000, "level": "WARNING", "msg": "High background radiance"},
    {"hex": 0x000000800000, "level": "WARNING", "msg": "Heater fault"},
    {"hex": 0x000001000000, "level": "WARNING", "msg": "Humidity sensor failure"},
    {"hex": 0x000002000000, "level": "WARNING", "msg": "undefined"},
    {"hex": 0x000004000000, "level": "WARNING", "msg": "Blower failure"},
    {"hex": 0x000008000000, "level": "WARNING", "msg": "undefined"},
    {"hex": 0x000010000000, "level": "WARNING", "msg": "High humidity"},
    {"hex": 0x000020000000, "level": "WARNING", "msg": "Transmitter expires"},
    {"hex": 0x000040000000, "level": "WARNING", "msg": "Battery voltage low"},
    {"hex": 0x000080000000, "level": "WARNING", "msg": "Window contamination"},
    {"hex": 0x000100000000, "level": "ALARM", "msg": "Ceilometer engine board failure"},
    {"hex": 0x000200000000, "level": "ALARM", "msg": "Coaxial cable failure"},
    {"hex": 0x000400000000, "level": "ALARM", "msg": "undefined"},
    {"hex": 0x000800000000, "level": "ALARM", "msg": "undefined"},
    {"hex": 0x001000000000, "level": "ALARM", "msg": "undefined"},
    {"hex": 0x002000000000, "level": "ALARM", "msg": "undefined"},
    {"hex": 0x004000000000, "level": "ALARM", "msg": "undefined"},
    {"hex": 0x008000000000, "level": "ALARM", "msg": "undefined"},
    {"hex": 0x010000000000, "level": "ALARM", "msg": "Receiver saturation"},
    {"hex": 0x020000000000, "level": "ALARM", "msg": "Light path obstruction"},
    {"hex": 0x040000000000, "level": "ALARM", "msg": "Memory error"},
    {"hex": 0x080000000000, "level": "ALARM", "msg": "undefined"},
    {"hex": 0x100000000000, "level": "ALARM", "msg": "Voltage failure"},
    {"hex": 0x200000000000, "level": "ALARM", "msg": "Receiver failure"},
    {"hex": 0x400000000000, "level": "ALARM", "msg": "Transmitter failure"},
    {"hex": 0x800000000000, "level": "ALARM", "msg": "Transmitter shut-off"},
]


def convert_str_to_int(array):
    """
    Convert status strings to integer to be compatible between fw 1.1.0 and 1.2.7
    """
    int_array = np.zeros(len(array))
    conversion_dict = {"0": 0, "I": 1, "W": 2, "A": 3}
    for i in range(len(array)):
        int_array[i] = conversion_dict[array[i]]

    return int_array.astype(int)


def get_error_index(err_msg, logger):
    """
    based on error message read in file. return all indices of related msg and level
    """

    err_ind = []
    err_int = int(err_msg, 16)
    for i, d in enumerate(ERR_HEX_MSG):
        if bool(err_int & d["hex"]):
            err_ind.append(i)

    return err_ind


def store_error(data, err_msg, logger):
    """store errors msg and their count by type"""

    err_ind = get_error_index(err_msg, logger)

    for i in err_ind:
        if ERR_HEX_MSG[i]["msg"] in data["list_errors"]:
            data["list_errors"][ERR_HEX_MSG[i]["msg"]]["count"] += 1
        else:
            data["list_errors"][ERR_HEX_MSG[i]["msg"]] = {}
            data["list_errors"][ERR_HEX_MSG[i]["msg"]]["count"] = 1
            data["list_errors"][ERR_HEX_MSG[i]["msg"]]["level"] = ERR_HEX_MSG[i][
                "level"
            ]

    return data


def log_error_msg(data, logger):
    msg_format = "{} : {:d} message(s)"

    if len(data["list_errors"]) > 0:
        logger.info("summary of instruments messages")

    for msg in data["list_errors"]:
        if data["list_errors"][msg]["level"] == "STATUS":
            logger.info(msg_format.format(msg, data["list_errors"][msg]["count"]))
        elif data["list_errors"][msg]["level"] == "WARNING":
            logger.warning(msg_format.format(msg, data["list_errors"][msg]["count"]))
        elif data["list_errors"][msg]["level"] == "ALARM":
            logger.error(msg_format.format(msg, data["list_errors"][msg]["count"]))


def are_units_meters(err_msg, logger):
    """
    based on status message, determine what are the units of CLH and CBH
    """

    err_ind = get_error_index(err_msg, logger)

    for i in err_ind:
        if ERR_HEX_MSG[i]["msg"] == "Units are meters if on, else feet":
            logger.debug("units are in meters")
            return True

    logger.debug("units are in feet")

    return False


def get_conversion_coeff(are_units_meters):
    """
    based on the status message return the coefficient to convert feet to meters
    """

    coeff = 1.0
    if not are_units_meters:
        coeff = FEET_TO_METERS

    return coeff


def check_scale_value(data, conf, ind, f_name, logger):
    """
    check scale value. If value is not 100%, message is voided.
    """

    msg = "101 Instrument Calibration Issues in '{}'. "
    msg += "Values for {:%Y-%m-%d %H:%M:%S} will be replaced by missing value"

    if data["scale"][ind] != OK_SCALE_VALUE:
        logger.warning(msg.format(f_name, data["time"][ind]))

        if conf["check_scale"]:
            data["rcs_0"][ind, :] = conf["missing_float"]
            data["pr2"][ind, :] = conf["missing_float"]


def get_file_lines(filename, conf, logger):
    """
    read all lines of a given file and remove carriage return from
    all lines
    """

    try:
        with open(filename, "r", encoding=conf["file_encoding"]) as f_id:
            logger.debug("reading " + filename)
            lines = chomp(f_id.readlines())
    except IOError:
        logger.error("109 Impossible to open file " + filename)
        return None

    return lines


def count_msg_to_read(list_files, conf, logger):
    """
    to a first reading of the CL31 file to determine the number
    of data messages which need to be read
    """

    n_data_msg = 0

    # loop over filenames to read to count the number of messages
    # data message start with a date using the format "-%Y-%m-%d %H:%M:%S"
    for ifile in list_files:
        lines = get_file_lines(ifile, conf, logger)
        for line in lines:
            try:
                dt.datetime.strptime(line, FMT_DATE)
                n_data_msg += 1
            except ValueError:
                continue

    logger.info("%d data messages to read" % n_data_msg)

    return n_data_msg


def get_conf_msg(line, logger):
    """
    Extract conf message
    """

    conf_str = re.search(CONF_MSG_REGEX, line)
    if conf_str is not None:
        conf_msg = conf_str.group()
        logger.debug("conf message %s" % conf_msg)
    else:
        conf_msg = None

    return conf_msg


def get_range_resol(conf_msg, logger):
    """
    Extract vertical range resolution from configuration message line
    """
    try:
        int_coding = int(conf_msg[7:8])
        range_resol = RANGE_RESOL[int_coding]
        logger.debug("range resolution: %d m" % range_resol)
    except Exception as err:
        logger.warning("105 Problem reading range resolution: " + repr(err))
        return None

    return range_resol


def get_range_ngates(conf_msg, logger):
    """
    Extract the number of gates from configuration message line
    """

    try:
        int_coding = int(conf_msg[7:8])
        range_ngates = RANGE_GATES[int_coding]
        logger.debug("number of vertical gates: %d" % range_ngates)
    except Exception as err:
        logger.warning("105 Problem reading number of vertical gates " + repr(err))
        return None

    return range_ngates


def get_msg_type(conf_msg, filename, logger):
    """
    Extract from acquisition configuration line if the file contains
    message of type 1 or 2 (without or with sky state)
    """

    msg_type = int(conf_msg[6:7])

    if msg_type == 1:
        logger.info("file contains messages of type 1 (without sky state)")
    elif msg_type == 2:
        logger.info("file contains messages of type 2 (with sky state)")
    else:
        logger.error("106 problem determining type of message '{}'".format(filename))
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

    range_vect = np.array(list(range(1, n_gates + 1)), dtype=float)

    return range_vect * float(resol)


def check_range(data, data_dim, filename, logger):
    """
    check we determining range was a success
    """

    # Test if the msg contains retrodiffusion profiles
    if data_dim["range"] == -9 or data["range_resol"] == -9:
        logger.error(
            "101 according to the configuration read "
            + "the file {} doesn't contains retrodiffusion ".format(filename)
            + "profiles. Trying next message"
        )
        range_ok = False
        # Test if we manage to read resol anf number of gates
    elif data_dim["range"] is None or data["range_resol"] is None:
        logger.error(
            "101 problem encountered reading range configuration."
            + " from {} Trying next message".format(filename)
        )
        range_ok = False
    else:
        range_ok = True

    return range_ok


def check_msg_type(data, logger):
    """
    check if determining message type was a success
    """

    # test if message type could be determine
    if data["msg_type"] is None:
        msg_ok = False
        logger.error("Could not determine type of message in file")
    else:
        msg_ok = True

    return msg_ok, data


def get_acq_conf(filename, data, data_dim, conf, logger):
    """
    extract acquisition configuration from a data message
    (range resolution and number of vertical gates)
    """

    lines = get_file_lines(filename, conf, logger)
    n_lines = len(lines)
    i_line = 0
    range_ok = False
    msg_ok = False

    logger.debug(n_lines)

    conf_msg = None
    while i_line <= n_lines:
        try:
            dt.datetime.strptime(lines[i_line], FMT_DATE)
        except:
            conf_msg = None
            i_line += 1
            continue

        conf_msg = get_conf_msg(lines[i_line + 1], logger)
        if conf_msg is None:
            continue

        data_dim["range"] = get_range_ngates(conf_msg, logger)
        data["range_resol"] = get_range_resol(conf_msg, logger)

        # check if reading of range was a success
        range_ok = check_range(data, data_dim, filename, logger)
        if range_ok:
            data["range"] = calc_range(data["range_resol"], data_dim["range"])

        # Check if reading of message type is a success
        data["msg_type"] = get_msg_type(conf_msg, filename, logger)
        msg_ok, data = check_msg_type(data, logger)

        if range_ok and msg_ok:
            break

    # if we are not able to read range in the file
    if not range_ok:
        logger.critical(
            "107 Impossible to read range configuration in '"
            + filename
            + "'. Stopping Raw2L1"
        )
    if not msg_ok:
        logger.critical(
            "106 impossible to determine type of message in '"
            + filename
            + "'. Stopping Raw2L1"
        )

    if not range_ok or not msg_ok:
        sys.exit(1)

    # Read instrument/sofware id
    data["instrument_id"] = conf_msg[0:3]
    data["software_id"] = f"{(float(conf_msg[3:6])/100):.3f}"

    return data, data_dim


def init_data(data, data_dim, conf, logger):
    """
    declare size of the numpy arraies and initialiase it
    """

    # get missing values
    missing_int = conf["missing_int"]
    missing_float = conf["missing_float"]

    # Dimension variables
    # -------------------------------------------------------------------------
    data["time"] = np.ones((data_dim["time"],), dtype=np.dtype(dt.datetime)) * np.nan
    data["cbh_layer"] = np.array([x + 1 for x in range(CBH_DIM)])
    data["clh_layer"] = np.array([x + 1 for x in range(CLH_DIM)])

    # Time dependant variables
    # -------------------------------------------------------------------------
    data["scale"] = np.ones((data_dim["time"],), dtype=np.float32) * missing_float
    data["laser_temp"] = np.ones((data_dim["time"],), dtype=np.float32) * missing_float
    data["hkd_state_laser"] = (
        np.ones((data_dim["time"],), dtype=np.float32) * missing_float
    )
    data["bckgrd_rcs_0"] = (
        np.ones((data_dim["time"],), dtype=np.float32) * missing_float
    )
    data["hkd_state_optics"] = (
        np.ones((data_dim["time"],), dtype=np.float32) * missing_float
    )
    data["tilt_angle"] = np.ones((data_dim["time"],), dtype=np.float32) * missing_float
    data["beta_att_sum"] = (
        np.ones((data_dim["time"],), dtype=np.float32) * missing_float
    )
    data["vertical_visibility"] = (
        np.ones((data_dim["time"],), dtype=np.int32) * missing_int
    )
    data["status_self_check"] = (
        np.ones((data_dim["time"],), dtype=np.int16) * missing_int
    )
    data["info_flags"] = np.ndarray((data_dim["time"],), dtype="S12")

    # Time, layer dependant variables
    # -------------------------------------------------------------------------
    data["cbh"] = np.ones((data_dim["time"], CBH_DIM), dtype=np.int32) * missing_int
    data["clh"] = np.ones((data_dim["time"], CLH_DIM), dtype=np.int32) * missing_int
    data["cloud_amount"] = (
        np.ones((data_dim["time"], CLH_DIM), dtype=np.int16) * missing_int
    )

    # Time, range dependent variables
    # -------------------------------------------------------------------------
    data["rcs_0"] = (
        np.ones((data_dim["time"], data_dim["range"]), dtype=np.float32) * missing_float
    )
    data["pr2"] = (
        np.ones((data_dim["time"], data_dim["range"]), dtype=np.float32) * missing_float
    )

    # Special variable to store for each message the unit of CBH and CLH
    # -------------------------------------------------------------------------
    data["are_unit_meter"] = np.ones((data_dim["time"],), dtype=bool)
    data["list_errors"] = {}

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

    line_to_read = get_state_line_nb_in_msg(data["msg_type"])
    line = msg[line_to_read]

    return float(line.split()[6])


def read_time_dep_vars(data, ind, msg, msg_type, logger):
    """
    read time only dependent variables
    ex: 00100 10 0770 098 +34 099 12 621 L0112HN15 139↵
    """

    line_to_read = get_state_line_nb_in_msg(data["msg_type"])
    params = msg[line_to_read].split()

    data["scale"][ind] = float(params[0])
    data["hkd_state_laser"][ind] = float(params[3])
    data["laser_temp"][ind] = float(params[4]) + DEG_TO_K
    data["hkd_state_optics"][ind] = float(params[5])
    data["tilt_angle"][ind] = float(params[6])
    try:
        data["bckgrd_rcs_0"][ind] = float(params[7])
    except IndexError:
        data["bckgrd_rcs_0"][ind] = np.nan
    try:
        data["beta_att_sum"][ind] = float(params[9]) * SUM_BCKSCATTER_FACTOR
    except IndexError:
        data["beta_att_sum"][ind] = np.nan

    return data


def read_cbh_msg(data, ind, msg, logger):
    """
    extract CBH
    ex: 30 01230 12340 23450 FEDCBA987654↵
    """

    elts = msg[2].split()

    # get the number of cloud layer
    if elts[0][0] == "/":
        logger.warning("105 cloud data missing for message %d" % ind)
        nlayers = 0
    else:
        nlayers = int(elts[0][0])

    data["status_self_check"][ind] = convert_str_to_int(elts[0][1])

    # flags
    data["info_flags"][ind] = elts[4]
    # get unit of CBH
    data["are_unit_meter"][ind] = are_units_meters(elts[4], logger)

    coeff = get_conversion_coeff(data["are_unit_meter"][ind])

    data = store_error(data, elts[4], logger)

    # number of CBH depends on nlayers value
    if 1 <= nlayers < 4:
        data["cbh"][ind, 0] = float(elts[1]) * coeff
    if 2 <= nlayers < 4:
        data["cbh"][ind, 1] = float(elts[2]) * coeff
    if 3 <= nlayers < 4:
        data["cbh"][ind, 2] = float(elts[3]) * coeff
    # vertical visibility
    if nlayers == 4:
        data["vertical_visibility"][ind] = float(elts[1]) * coeff

    return data


def read_clh_msg(data, ind, msg, logger):
    """
    extract CLH, cloud amount and visibility
    """

    # split lines to get each elements
    # even elements are cloud amount
    # odd elements are CLH
    line = msg[3]
    elts = line.strip().split()
    octas = [int(octa) for octa in elts[0::2]]
    clh_str = elts[1::2]

    # depending on configuration a different factor need to be applied
    # if value are in meters or feets
    coeff = get_conversion_coeff(data["are_unit_meter"][ind])
    if data["are_unit_meter"][ind]:
        coeff = coeff * CLH_ALT_METERS_FACTOR
    else:
        coeff = coeff * CLH_ALT_FEET_FACTOR

    # get cloud amount
    for level, octa in enumerate(octas):
        if 1 <= octa <= 8:
            data["cloud_amount"][ind, level] = int(octa)
            data["clh"][ind, level] = float(clh_str[level]) * coeff
        elif octa == 0:
            data["cloud_amount"][ind, level] = int(octa)

    return data


def read_cbh_vars(data, ind, msg, logger):
    """
    Read the altitude of the 3 cloud layer in a data message
    """

    # reading of CBH depends on the kind of data message type
    data = read_cbh_msg(data, ind, msg, logger)
    if data["msg_type"] == 2:
        data = read_clh_msg(data, ind, msg, logger)

    return data


def read_rcs_var(data, ind, msg, logger):
    """
    read the rcs value in a data msg
    """
    # get line a of the message containing RCS based on CL31 conf
    line_to_read = get_rcs_line_nb_in_msg(data["msg_type"])
    # size of the profile to read
    rcs_size = data["range"].size
    # extract line containing rcs
    try:
        rcs_line = msg[line_to_read]
    except IndexError:
        logger.error("Impossible to decode message. Profile is ignore")
        return data

    try:
        tmp = [
            rcs_line[s * RCS_BYTES_SIZE : s * RCS_BYTES_SIZE + RCS_BYTES_SIZE]  # NOQA
            for s in range(rcs_size)
        ]
        tmp = np.array([int(g, 16) if g != "" else np.nan for g in tmp])

    except ValueError:
        logger.error("Impossible to decode message. Profile is ignore")
        return data

    # Each sample is coded with a 20-bit HEX ASCII character set
    # msb nibble and bit first, 2's complement
    corr_2s_needed = tmp > 2**19
    if any(corr_2s_needed):
        tmp[corr_2s_needed] = -(2**20 - tmp[corr_2s_needed])

    data["rcs_0"][ind][:] = np.array(tmp, dtype=np.float32) * RCS_FACTOR

    return data


def read_vars(lines, data, conf, time_ind, f_name, logger):
    """
    read all available variables in one file
    """

    n_lines = len(lines)
    i_line = 0
    msg_n_lines = get_msg_nb_lines(data["msg_type"])

    # loop over the lines
    while i_line < n_lines:
        # reject header lines
        if lines[i_line] in FILE_HEADERS:
            i_line += 1
            continue

        # Try finding line with time stamp
        try:
            data["time"][time_ind] = dt.datetime.strptime(lines[i_line], FMT_DATE)
        except ValueError:
            i_line += 1
            continue

        logger.debug("timestamp: {:%Y%m%d %H:%M:%S}".format(data["time"][time_ind]))

        msg = lines[i_line : i_line + msg_n_lines]
        logger.debug("processing data message %d" % (time_ind + 1))

        # check if there is no change in message number
        cur_msg_type = get_msg_type(get_conf_msg(msg[1], logger), f_name, logger)
        if cur_msg_type != data["msg_type"]:
            i_line += 1
            time_ind += 1
            logger.error(
                "100 Incorrect Header Information in '{}'. Message type change in file".format(
                    f_name
                )
            )
            continue

        # read time only dependent variables
        logger.debug("reading time only dependent variables")
        data = read_time_dep_vars(data, time_ind, msg, data["msg_type"], logger)

        # read CBH
        logger.debug("reading cbh/clh")
        data = read_cbh_vars(data, time_ind, msg, logger)

        # read rcs
        logger.debug("reading rcs")
        data = read_rcs_var(data, time_ind, msg, logger)

        # check scale value if needed
        check_scale_value(data, conf, time_ind, f_name, logger)

        # Add number of line of a message to lines counter
        # i_line += msg_n_lines
        i_line += 1
        time_ind += 1

    return time_ind, data


def read_data(list_files, conf, logger):
    """
    Raw2L1 plugin to read data of the vaisala CL31
    """

    # checking conf parameters
    # -------------------------------------------------------------------------
    try:
        conf["check_scale"] = to_bool(conf["check_scale"])
    except (ValueError, KeyError):
        conf["check_scale"] = False

    try:
        conf["time_resol"] = int(conf["time_resolution"])
    except KeyError:
        logger.error("the time_resolution option in reader_conf is required")
        sys.exit(1)

    # encoding of file, if not defined use utf8
    if "file_encoding" not in conf:
        logger.info("No encoding defined for using %s", DEFAULT_ENCODING)
        conf["file_encoding"] = DEFAULT_ENCODING

    # analyse file to read to determine the size of the time variable
    # -------------------------------------------------------------------------
    data = {}
    data_dim = {}
    logger.info("analysing input files to get the configuration")
    data_dim["time"] = count_msg_to_read(list_files, conf, logger)

    # Get range and vertical resolution from first file
    logger.info("analyzing first file to determine acquisition configuration")
    data, data_dim = get_acq_conf(list_files[0], data, data_dim, conf, logger)

    logger.info("initialising data arrays")
    data = init_data(data, data_dim, conf, logger)

    # Reading all the data
    # -------------------------------------------------------------------------
    logger.info("reading files")
    time_ind = 0
    nb_files_read = 0
    for ifile in list_files:
        # try reading the file
        lines = get_file_lines(ifile, conf, logger)
        if lines is None:
            logger.warning(
                "102 No data found in the file '{}' trying next file".format(ifile)
            )
            continue

        nb_files_read += 1

        # reading data in the file
        time_ind, data = read_vars(lines, data, conf, time_ind, ifile, logger)

    # add start_time and time resolution variable
    # ------------------------------------------------------------------------
    data["time_resolution"] = conf["time_resol"]
    data["start_time"] = data["time"] - dt.timedelta(seconds=conf["time_resol"])

    # Final calculation on whole profiles
    # -------------------------------------------------------------------------
    # data["pr2"] = data["rcs_0"] * RCS_FACTOR * data["range"] ** 2

    # Summary of instrument message
    # ------------------------------------------------------------------------
    log_error_msg(data, logger)

    return data
