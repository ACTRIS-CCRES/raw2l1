# Compatibility with python 3


import numpy as np

OVER_DTYPE = [("range", "f4"), ("overlap", "f4")]
COMMENTS = "#"
FILLING = np.nan


def read_overlap(fname, logger):
    """
    function to read overlap function contains in a file with two columns:
    """

    logger.debug("reading overlap file: " + fname)
    try:
        data = np.genfromtxt(
            fname, dtype=OVER_DTYPE, comments=COMMENTS, filling_values=FILLING
        )

    except OSError as err:
        logger.errot("107 Error Reading overlap file : " + fname)
        logger.error(err)
        data = None

    return data["overlap"]
