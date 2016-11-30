# -*- coding: utf8 -*-

from __future__ import print_function, absolute_import, division

import datetime as dt

# IPRAL configuration
# ----------------------------------------------------------------------------

# brand and model of the LIDAR
BRAND = 'Gordien Stratos/Raymetrics/SIRTA'
MODEL = 'IPRAL'

# channels : each channel is define by 4 parameters :
# - wavelength
# - polarisation ('o', 's', 'p')
# - telescope 1 -> far field, 2 -> near field
# - analog (BT) ou photcounting (BC)
CHANNELS = [
    (1064, 'o', 1, 'BT'),  # 00
    (607, 'o', 1, 'BC'),   # 01
    (355, 'p', 1, 'BT'),   # 02
    (355, 'p', 1, 'BC'),   # 03
    (355, 's', 1, 'BT'),   # 04
    (355, 's', 1, 'BC'),   # 05
    (387, 'o', 1, 'BT'),   # 06
    (387, 'o', 1, 'BC'),   # 07
    (408, 'o', 1, 'BT'),   # 08
    (408, 'o', 1, 'BC'),   # 09
    (532, 'o', 1, 'BT'),   # 10
    (532, 'o', 1, 'BC'),   # 11
    (355, 'o', 2, 'BT'),   # 12
    (355, 'o', 2, 'BC'),   # 13
    (387, 'o', 2, 'BT'),   # 14
    (387, 'o', 2, 'BC'),   # 15
    (532, 'o', 2, 'BT'),   # 16
    (532, 'o', 2, 'BC'),   # 17
]

POLARIZATION = {'o': 'none', 's': 'perpendicular', 'p': 'parallel'}

# dates format
DATE_FMT = '%md/%m/%Y %H:%M:%S'

FILENAME_LENGTH = 13
LINE_2_N_FIELDS = 12

# error messages
# ----------------------------------------------------------------------------
ERR_MSG = {
    0: ("ERROR: filename has not the right number of characters ({}). "
        "Should be {}. File {} will be ignore."),
    1: ("ERROR: month in hexadecimal format '{}' could not be converted "
        "into int. "),
    2: "ERROR: impossible to convert to date filename '{}'",
    3: "ERROR: line 2 has {} fields. It sould be {}. {} will be skipped",
    4: "imossible to convert {} into datetime object",
}


def filename_to_date(s, logger):
    """get the date of the file based on the filename"""

    # check filename
    if len(s) != FILENAME_LENGTH:
        logger.error(ERR_MSG[0].format(len(s), FILENAME_LENGTH, s))
        return None

    year = s[2:2]
    # month coded in 1 character in hex format
    try:
        month = str('%02d'.format(int(s[4:1], 16)))
    except ValueError:
        logger.error(ERR_MSG[1].format(s[4:1]))
        return None
    day = int(s[5:2])
    hour = int(s[7:2])
    minute = int(s[10:2])
    second = int(s[12:1] + '0')

    date_str = year + month + day + ' ' + hour + minute + second

    try:
        date = dt.datetime.strptime(date_str, 'y%m%d %H%M%S')
    except ValueError:
        logger.error(ERR_MSG[2].format(s))

    return date


def get_date_dt(date, hour, logger):
    """convert string date into datetime object"""

    date_str = date + ' ' + hour
    try:
        date_dt = dt.datetime.strptime(date_str, DATE_FMT)
    except ValueError:
        logger.warning(ERR_MSG[4].format(date_str))
        return None

    return date_dt


def read_line_2(line, filename, logger):
    """
    read line 2 and return interesting values
    SIRTA    05/11/2015 08:10:00 05/11/2015 08:10:36 0156 0038.0 0002.0 -90.0 0.0 15.0 1013.0
    """

    fields = line.split()
    if len(fields) != LINE_2_N_FIELDS:
        logger.error(ERR_MSG[3].format(len(fields), LINE_2_N_FIELDS, filename))
        return None

    data = {}
    data['date_start'] = get_date_dt(fields[1], fields[2])
    if data['date_start'] is None:
        return None

    data['date_end'] = get_date_dt(fields[1], fields[2])

    return data


def read_data(list_files, conf, logger):
    """
    Raw2L1 plugin to read raw data of Jenoptik CHM15K
    """

    logger.info(
        'Start reading of data using reader for ' + BRAND + ' ' + MODEL
    )

    data = {}

    return data
