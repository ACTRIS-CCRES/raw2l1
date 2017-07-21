#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
reader for raw data from SIRTA IPRAL LIDAR
the file format is based on LICEL file format
"""

from __future__ import print_function, absolute_import, division

import sys
import ast
import datetime as dt
from collections import OrderedDict

import numpy as np
import netCDF4 as nc


# brand and model of the LIDAR
BRAND = 'Gordien Stratos'
MODEL = 'IPRAL'

DATETIME_FMT = '{} {}'
DATE_FMT = '%d/%m/%Y %H:%M:%S'
TIME_FMT = '%H:%M:%S'

N_HEADER_LINE = 3

MISSING_FLOAT = np.nan
MISSING_INT = -9


def date_to_dt(date_num, date_units):
    """convert date np.array from datenum to datetime.datetime"""

    return nc.num2date(date_num,
                       units=date_units,
                       calendar='standard')

def get_data_size(list_files, logger):
    """determine size of data to read"""

    # create dimensions dict
    data_dim = {}
    data_dim['time'] = 0
    data_dim['range'] = 0
    data_dim['n_chan'] = 0
    data_dim['nv'] = 2 # size for time bounds

    # loop over list of files
    for i_file, file_ in enumerate(list_files):

        try:
            f_id = open(file_, 'rb')
        except IOError:
            logger.error("error trying to open %s", file_)
            continue

        # line 1 : name of file, we don't need it
        f_id.readline()

        # line 2 : date and time, we need it
        line = f_id.readline()
        elts = line.split()
        datetime_str = DATETIME_FMT.format(elts[1], elts[2])

        # try to parse date to check file is valid
        try:
            timestamp = dt.datetime.strptime(datetime_str, DATE_FMT)
        except ValueError:
            logger.error("wrong time format in " + file_)
            continue

        data_dim['time'] += 1

        # line 3 : number of channels, we need it
        line = f_id.readline()
        elts = line.split()

        # read or check number of channels in file
        if i_file == 0:
            data_dim['n_chan'] = int(elts[4])
            logger.info('number of channels : %d', data_dim['n_chan'])
        else:
            tmp = int(elts[4])
            if tmp != data_dim['n_chan']:
                logger.critical('number of channels was %d in previous file and is now %d in %s',
                                data_dim['n_chan'], tmp, file_)
                sys.exit(1)

        logger.info('data contains %d channels', data_dim['n_chan'])

        # line 4 : get range from first channel description
        line = f_id.readline()
        elts = line.split()

        if i_file == 0:
            data_dim['range'] = int(elts[3])
            logger.info('size of range : %d', data_dim['range'])
        else:
            tmp = int(elts[3])
            if tmp != data_dim['range']:
                logger.critical('size of range was %d in previous file and is now %d in %s',
                                data_dim['range'], tmp, file_)
                sys.exit(1)

        f_id.close()

    # log dimensions
    logger.debug('dim time     : %d', data_dim['time'])
    logger.debug('dim range    : %d', data_dim['range'])
    logger.debug('dim channels : %d', data_dim['n_chan'])
    logger.debug('dim nv       : %d', data_dim['nv'])

    return data_dim


def init_data(data_dim, logger):
    """initialize dict containing ndarrays based on data dimension"""

    data = {}

    # dimensions
    data['time'] = np.empty((data_dim['time'],), dtype=np.dtype(dt.datetime))
    data['time_bounds'] = np.empty((data_dim['time'], data_dim['nv']), dtype=np.dtype(dt.datetime))
    data['range'] = np.empty((data_dim['range'],), dtype=np.float32)

    # scalar values
    data['type1_shots'] = MISSING_FLOAT
    data['frequency'] = MISSING_FLOAT
    data['type2_shots'] = MISSING_FLOAT
    data['time_resol'] = MISSING_FLOAT
    data['zenith'] = MISSING_FLOAT
    data['range_resol'] = MISSING_FLOAT
    data['longitude'] = MISSING_FLOAT
    data['latitude'] = MISSING_FLOAT
    data['altitude'] = MISSING_FLOAT

    # n_chan dependant
    for i_chan in xrange(data_dim['n_chan']):

        # data['rcs_nan%02d' % i_chan] = np.ones((data_dim['time'], data_dim['range']),
        #                                        dtype=np.float32) * MISSING_FLOAT
        data['rcs_%02d' % i_chan] = np.ones((data_dim['time'], data_dim['range']),
                                            dtype=np.float32) * MISSING_FLOAT
        data['wavelength_%02d' % i_chan] = np.ones((data_dim['time'], data_dim['range']),
                                                   dtype=np.float32) * MISSING_FLOAT
        data['voltage_%02d' % i_chan] = MISSING_INT
        data['range_length_%02d' % i_chan] = MISSING_INT
        data['bin_shift_%02d' % i_chan] = MISSING_INT
        data['ADCbits_%02d' % i_chan] = MISSING_INT
        data['n_shots_%02d' % i_chan] = MISSING_INT
        data['detection_mode_%02d' % i_chan] = np.empty(1, dtype=np.str)
        data['max_detection_range_%02d' % i_chan] = MISSING_INT
        data['discriminator_level_%02d' % i_chan] = MISSING_INT

    return data


def read_header(file_id, data, data_dim, index, logger, date_only=False):
    """Extract data from file ASCII header"""

    # first line: filename (we don't need it)
    # ------------------------------------------------------------------------
    file_id.readline()

    # second line : datetime, localization and meteo
    # ------------------------------------------------------------------------
    logger.debug('reading header second line')
    line = file_id.readline()
    elts = line.split()

    logger.debug('reading dates')
    datetime_start = DATETIME_FMT.format(elts[1], elts[2])
    datetime_end = DATETIME_FMT.format(elts[3], elts[4])

    data['time'][index] = dt.datetime.strptime(datetime_start, DATE_FMT)
    logger.debug('datetime: %s', data['time'][index])
    data['time_bounds'][index, 0] = data['time'][index]
    data['time_bounds'][index, 1] = dt.datetime.strptime(datetime_end, DATE_FMT)

    if date_only:
        logger.debug('reading only date')
        return data

    data['time_resol'] = (data['time_bounds'][index, 1] - data['time_bounds'][index, 0]).total_seconds()
    data['altitude'] = np.float(elts[5])
    data['latitude'] = np.float(elts[6])
    data['longitude'] = float(elts[7])
    data['zenith'] = float(elts[8])

    # third line: nothing interesting to read ??
    # ------------------------------------------------------------------------
    line = file_id.readline()
    elts = line.split()
    data["type1_shots"] = np.float(elts[0])
    data['frequency'] = np.float(elts[1])
    data["type2_shots"] = np.float(elts[2])

    # channels description
    # ------------------------------------------------------------------------
    wavelengths = []
    range_resol = []
    for i_chan in xrange(data_dim['n_chan']):

        var_name = 'rcs_{:02d}'.format(i_chan)

        line = file_id.readline()
        elts = line.split()

        data['laser_{:02d}'.format(i_chan)] = int(elts[1])
        data['telescope_{:02d}'.format(i_chan)] = int(elts[2])
        data['voltage_{:02d}'.format(i_chan)] = int(elts[5])
        range_resol.append(float(elts[6]))
        data['range_length_{:02d}'.format(i_chan)] = float(elts[6])
        wavelengths.append(int(elts[7].split('.')[0]))
        data['polarization_{:02d}'.format(i_chan)] = str(elts[7][6])
        data['bin_shift_{:02d}'.format(i_chan)] = float(elts[10])
        data['ADCbits_{:02d}'.format(i_chan)] = int(elts[12])
        data['n_shots_{:02d}'.format(i_chan)] = int(elts[13])

        tmp = elts[15][0:2]
        if tmp == 'BT':
            data['detection_mode_{:02d}'.format(i_chan)] = 'analog'
            data['max_detection_range_{:02d}'.format(i_chan)] = float(elts[14]) * 1000.
            data['discriminator_level_{:02d}'.format(i_chan)] = MISSING_FLOAT
        elif tmp == 'BC':
            data['detection_mode_{:02d}'.format(i_chan)] = 'photocounting'
            data['discriminator_level_{:02d}'.format(i_chan)] = float(elts[14])
            data['max_detection_range_{:02d}'.format(i_chan)] = MISSING_FLOAT

    # remove duplicate wavelength and link each to a channel
    sort_wavelengths = set(wavelengths)
    for i_wv, wavelength in enumerate(sort_wavelengths):
        data['wavelength_l{:02d}'.format(i_wv)] = wavelength

    for i_chan in xrange(data_dim['n_chan']):
        for i_wv, wavelength in enumerate(sort_wavelengths):
            if wavelengths[i_chan] == wavelength:
                data['wavelength_{:02d}'.format(i_chan)] = i_wv
                continue

    # check all range_resol is the same
    sort_range_resol = set(range_resol)
    if len(sort_range_resol) == 1:
        data['range_resol'] = list(sort_range_resol)[0]
        logger.debug('range_resol: %s', data['range_resol'])
    else:
        logger.critical("all channel don't have the same resolution : %s", sort_range_resol )

    return data


def read_profiles(file_id, data, data_dim, index, logger):
    """read profile for each channel"""

    # skip header and channels descriptions
    for i in range(N_HEADER_LINE + data_dim['n_chan']):
        line = file_id.readline()

    for i_chan in xrange(data_dim['n_chan']):

        tmp_data = np.fromfile(file_id, dtype='i4', count=data_dim['range'])

        shots = data['n_shots_{:02d}'.format(i_chan)]

        if data['detection_mode_{:02d}'.format(i_chan)] == 'analog':
            max_range = data['max_detection_range_{:02d}'.format(i_chan)]
            adc = data['ADCbits_{:02d}'.format(i_chan)]
            data['rcs_{:02d}'.format(i_chan)][index, :] = tmp_data / shots * max_range / (2**adc - 1)
            data['units_{:02d}'.format(i_chan)] = 'mV'
        else :
            range_length = data['range_length_{:02d}'.format(i_chan)]
            # It coincides with the ASCII converted by the Advanced Licel.exe by it has no sense.
            # See Licel programming manual.pdf. Bins-per-microseconds number from technical specifications 20 bins/microsec.
            data['rcs_{:02d}'.format(i_chan)][index,:] = tmp_data / shots * 20. * (7.5 / range_length)
            data['units_{:02d}'.format(i_chan)] = 'MHz'

        # jump over space between profiles
        dummy = file_id.seek(file_id.tell()+2)

    return data


def read_data(list_files, conf, logger):
    """Raw2L1 plugin to read raw data of SIRTA IPRAL LIDAR"""

    logger.info('Start reading of data using reader for %s %s', BRAND, MODEL)

    # determine size of data to read
    # ------------------------------------------------------------------------
    logger.info("determining size of var to read")
    data_dim = get_data_size(list_files, logger)

    # initialize data array
    logger.info("initializing data output array")
    data = init_data(data_dim, logger)


    for ind, file_ in enumerate(list_files):

        try:
            f_id = open(file_, 'rb')
        except IOError:
            logger.error("error trying to open " + file_)
            continue

        # read header
        # --------------------------------------------------------------------
        if ind != 0:
            date_only = True
        else:
            date_only = False

        data = read_header(f_id, data, data_dim, ind, logger, date_only=date_only)

        # read data
        # --------------------------------------------------------------------
        logger.info('read data')

        # go back to start of file
        f_id.seek(0)

        # read profiles
        data = read_profiles(f_id, data, data_dim, ind, logger)

        # end of reading
        # --------------------------------------------------------------------
        f_id.close()


    # final calculations
    # --------------------------------------------------------------------

    # determine range
    data['range'] = np.arange(1, data_dim['range'] + 1) * data['range_resol']
    print(data['range'])

    # add necessary dimension
    data['nv'] = data_dim['nv']

    # PR2
    for i_chan in xrange(data_dim['n_chan']):
        square = np.square(data['range'])
        data['rcs_{:02d}'.format(i_chan)] = data['rcs_{:02d}'.format(i_chan)] * square

    return data
