# -*- coding: utf8 -*-

# Compatibility with python 3
from __future__ import print_function, division, absolute_import

import numpy as np

OVER_DTYPE = [('range', 'f4'), ('overlap', 'f4')]
COMMENTS = '#'
FILLING = np.nan


def read_overlap(fname, logger):
    """
    function to read overlap function contains in a file with two columns:
    """

    logger.debug("reading overlap file: " + fname)
    try:
        data = np.genfromtxt(fname,
                             dtype=OVER_DTYPE,
                             comments=COMMENTS,
                             filling_values=FILLING,)

    except IOError, err:
        logger.error(err)
        data = None

    return data['overlap']
