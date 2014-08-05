#!/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
import sys

OVER_DTYPE = [
        ('range', 'f4'),
        ('overlap', 'f4')
    ]
COMMENTS = '#'
FILLING  = -999.

def read_overlap(fname):
    """
    function to read overlap function contains in a file with two columns:
    """

    try:
        data = np.genfromtxt(fname,
                        dtype = OVER_DTYPE,
                        comments = COMMENTS,
                        filling_values = FILLING,
                )
    except IOError:
        print 'error encounter while reading file containing overlap function'
        sys.exit(1)

    return data
