# -*- coding: utf8 -*-



CONF_MSG_REGEX = r'CL.\d{5}'
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

# constant
RCS_BYTES_SIZE = 5
RCS_FACTOR = 1e-8
DEG_TO_K = 273.15
CBH_ALT_FACTOR = 10.
SUM_BCKSCATTER_FACTOR = 1.E-4

