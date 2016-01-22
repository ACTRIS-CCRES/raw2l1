# -*- coding: utf8 -*-

from __future__ import print_function, division, absolute_import

import numpy as np
import datetime as dt
import netCDF4 as nc

from .libhatpro import correct_time_units

# brand and model of the LIDAR
BRAND = 'RPG'
MODEL = 'HATPRO boundary layer temperature'

TIME_DIM = 'time'
TIME_VAR = 'time'


FLT_MISSING_VALUE = -999.
INT_MISSING_VALUE = -9


def get_data_size(list_files, logger):
    """based on all files to read determine the size of the data"""

    dim = {}
    dim['time'] = 0
    for i, f in enumerate(list_files):

        nc_id = nc.Dataset(f, 'r')

        dim['time'] += len(nc_id.dimensions[TIME_DIM])

        nc_id.close()

    logger.debug('time size = {}'.format(dim['time']))

    return dim


def init_data(vars_dim, logger):
    """initialize data dictionary"""

    data = {}

    data['time'] = np.empty((vars_dim['time'],), dtype=np.dtype(dt.datetime))
    data['time_bnds'] = np.empty((vars_dim['time'], 2),
                                 dtype=np.dtype(dt.datetime))
    data['azi'] = np.ones((vars_dim['time'],),
                          dtype=np.float32) * FLT_MISSING_VALUE
    data['ele'] = np.ones((vars_dim['time'],),
                          dtype=np.float32) * FLT_MISSING_VALUE
    data['prw'] = np.ones((vars_dim['time'],),
                          dtype=np.float32) * FLT_MISSING_VALUE
    data['prw_offset'] = np.ones((vars_dim['time'],),
                                 dtype=np.float32) * FLT_MISSING_VALUE
    data['prw_off_zenith'] = np.ones((vars_dim['time'],),
                                     dtype=np.float32) * FLT_MISSING_VALUE
    data['prw_err'] = np.ones((vars_dim['n_ret'],),
                              dtype=np.float32) * FLT_MISSING_VALUE

    data['flag'] = np.zeros((vars_dim['time'],), dtype=np.int16)
    data['rain_flag'] = np.zeros((vars_dim['time'],), dtype=np.int16)

    return data


def read_time(nc_id, logger):
    """read time variable"""

    time = nc_id.variables[TIME_VAR][:]
    units = correct_time_units(nc_id.variables[TIME_VAR].units)

    time = nc.num2date(time, units=units)

    return len(time), time


def read_data(list_files, conf, logger):
    """raw2l1 plugin to read raw data of RPG hatpro
    bloundary layer temperature"""

    logger.debug(
        'start reading data using reader for ' + BRAND + ' ' + MODEL)

    # get variables size
    vars_dim = get_data_size(list_files, logger)
    vars_dim['n_ret'] = int(conf['n_ret'])

    # Initialize data
    data = init_data(vars_dim, logger)

    # read data
    time_ind = 0
    for i, f in enumerate(list_files):

        nc_id = nc.Dataset(f, 'r')

        time_size, time = read_time(nc_id, logger)

        # determining index of data
        ind_s = time_ind
        ind_e = time_ind + time_size

        data['time'][ind_s:ind_e] = time
        data['ele'][ind_s:ind_e] = nc_id.variables['elevation_angle'][:]
        data['azi'][ind_s:ind_e] = nc_id.variables['azimuth_angle'][:]
        data['prw'][ind_s:ind_e] = nc_id.variables['IWV_data'][:]
        data['rain_flag'][ind_s:ind_e] = nc_id.variables['rain_flag'][:]

        nc_id.close()

        time_ind += time_size

    # produce time_bounds variable
    time_units = conf['time_units']
    integ_time = conf['integration_time']
    data['time_bnds'][:, 0] = nc.date2num(data['time'], units=time_units)
    tmp = data['time'] + dt.timedelta(seconds=float(integ_time))
    data['time_bnds'][:, 1] = nc.date2num(tmp, units=time_units)

    # quality flags
    rain_filter = data['rain_flag'] == 1
    data['flag'][rain_filter] = 8

    return data
