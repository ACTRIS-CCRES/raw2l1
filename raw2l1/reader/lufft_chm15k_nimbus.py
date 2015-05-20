# -*- coding: utf8 -*-

from __future__ import print_function, absolute_import, division

import netCDF4 as nc
import numpy as np
import datetime as dt
import sys

# brand and model of the LIDAR
BRAND = 'jenoptik'
MODEL = 'CHM15K nimbus'


def get_soft_version(str_version):
    """
    function to get the number of acquisition software version as a float
    """

    version_nb = str_version.split(' ')[-1]

    return float(version_nb)


def date_to_dt(date_num, date_units):
    """
    convert date np.array from datenum to datetime.datetime
    """

    return nc.num2date(date_num,
                       units=date_units,
                       calendar='standard')


def get_vars_dim(list_files, logger):
    """
    analyse the files to be read to determine the size of the final
    time dimension
    """

    data_dim = {}
    data_dim['time'] = 0
    data_dim['range'] = 0
    data_dim['layer'] = 0

    # loop over list of files
    f_count = 0
    for ifile in list_files:
        try:
            nc_id = nc.Dataset(ifile, 'r')
            f_count += 1
        except:
            logger.error("error trying to open " + ifile)
            continue

        if f_count == 1:
            data_dim['range'] = len(nc_id.variables['range'][:])
            data_dim['layer'] = len(nc_id.variables['layer'][:])

        data_dim['time'] += len(nc_id.variables['time'][:])

        nc_id.close()

    logger.debug("size of dimensions")
    for key in data_dim.keys():
        logger.debug("%r : %d" % (key, data_dim[key]))

    return data_dim


def get_temp(nc_obj, logger):
    """
    convert temperature to Kelvin taking into account errors in files with
    version lower than 0.7

    2 problems with temperature variables for software version < 0.7:
    - the scale factor instead of being a float is a unicode string
    (doing a ncdump -h on the file shows it, scale_factor is between
    double quote) which prevents netCDF4 module to do automatically
    the calculation. It has to be deactivate using
    set_auto_maskandscale(false)
    - the scale factor is wrong. It has a value of 10 and should be 0.1
    """

    try:
        tmp = nc_obj[:]
    except:
        logger.debug('Correcting temperature scale problem')
        nc_obj.set_auto_maskandscale(False)
        tmp = nc_obj[:] / np.float(nc_obj.scale_factor)

    return tmp


def init_data(vars_dim, logger):
    """
    based on the analysing of the file to read initialize the np.array of
    the output data dictionnary
    """

    data = {}

    # instrument characteristics
    # -------------------------------------------------------------------------
    data['firmware_version'] = ""
    data['instrument_id'] = ""
    data['scaling'] = np.nan

    # dimensions of the output netCDf file
    # -------------------------------------------------------------------------
    data['time'] = np.empty((vars_dim['time'],), dtype=np.dtype(dt.datetime))
    data['range'] = np.empty((vars_dim['range'],), dtype=np.float32)
    data['layer'] = np.empty((vars_dim['layer'],), dtype=np.int16)

    # Time dependent variables
    # -------------------------------------------------------------------------
    data['vor'] = np.empty((vars_dim['time'],), dtype=np.int16)
    data['voe'] = np.empty((vars_dim['time'],), dtype=np.int16)
    data['tcc'] = np.empty((vars_dim['time'],), dtype=np.int8)
    data['stddev'] = np.empty((vars_dim['time'],), dtype=np.float32)
    data['state_optics'] = np.empty((vars_dim['time'],), dtype=np.int8)
    data['state_laser'] = np.empty((vars_dim['time'],), dtype=np.int8)
    data['state_detector'] = np.empty((vars_dim['time'],), dtype=np.int8)
    data['sci'] = np.empty((vars_dim['time'],), dtype=np.int8)
    data['nn1'] = np.empty((vars_dim['time'],), dtype=np.int16)
    data['nn2'] = np.empty((vars_dim['time'],), dtype=np.int16)
    data['nn3'] = np.empty((vars_dim['time'],), dtype=np.int16)
    data['mxd'] = np.empty((vars_dim['time'],), dtype=np.int16)
    data['life_time'] = np.empty((vars_dim['time'],), dtype=np.int32)
    data['error_ext'] = np.empty((vars_dim['time'],), dtype=np.int32)
    data['temp_lom'] = np.empty((vars_dim['time'],), dtype=np.int16)
    data['temp_int'] = np.empty((vars_dim['time'],), dtype=np.int16)
    data['temp_ext'] = np.empty((vars_dim['time'],), dtype=np.int16)
    data['temp_det'] = np.empty((vars_dim['time'],), dtype=np.int16)
    data['laser_pulses'] = np.empty((vars_dim['time'],), dtype=np.int32)
    data['error_ext'] = np.empty((vars_dim['time'],), dtype=np.int32)
    data['bcc'] = np.empty((vars_dim['time'],), dtype=np.int8)
    data['bckgrd_rcs_0'] = np.empty((vars_dim['time'],), dtype=np.float32)
    data['average_time'] = np.empty((vars_dim['time'],), dtype=np.int32)
    data['p_calc'] = np.empty((vars_dim['time'],), dtype=np.int16)

    # Time, layer dependent variables
    # -------------------------------------------------------------------------
    data['pbs'] = np.empty((vars_dim['time'], vars_dim['layer']),
                           dtype=np.int8)
    data['pbl'] = np.empty((vars_dim['time'], vars_dim['layer']),
                           dtype=np.int16)
    data['cdp'] = np.empty((vars_dim['time'], vars_dim['layer']),
                           dtype=np.int16)
    data['cde'] = np.empty((vars_dim['time'], vars_dim['layer']),
                           dtype=np.int16)
    data['cbh'] = np.empty((vars_dim['time'], vars_dim['layer']),
                           dtype=np.int16)
    data['cbe'] = np.empty((vars_dim['time'], vars_dim['layer']),
                           dtype=np.int16)

    # Time, range dependent variables
    # -------------------------------------------------------------------------
    data['beta_raw'] = np.empty((vars_dim['time'], vars_dim['range']),
                                dtype=np.float32)
    data['rcs_0'] = np.empty((vars_dim['time'], vars_dim['range']),
                             dtype=np.float32)

    return data


def read_time_var(data, nc_id, time_ind, logger):
    """
    Add data to the time variable dimension
    """

    logger.debug('convert time variable into datetime object')
    tmp = nc_id.variables['time'][:]
    time_size = len(tmp)

    ind_b = time_ind
    ind_e = time_ind + len(tmp)

    data['time'][ind_b:ind_e] = date_to_dt(tmp,
                                           nc_id.variables['time'].units)

    return time_size, data


def read_dim_vars(data, nc_id, logger):
    """
    read dimension variables of the netCDf file
    """

    # get time variable size
    tmp = nc_id.variables['time'][:]
    time_size = len(tmp)

    logger.debug('reading time variable')
    # first reading of time variable
    time_size, data = read_time_var(data, nc_id, 0, logger)

    logger.debug('reading range')
    data['range'] = nc_id.variables['range'][:]
    logger.debug('reading layer')
    data['layer'] = nc_id.variables['layer'][:]

    return time_size, data


def read_scalar_vars(data, nc_id, soft_vers, logger):
    """
    read scalar variables of the netCDF file
    """

    logger.debug('reading zenith')
    data['zenith'] = nc_id.variables['zenith'][:]
    logger.debug('reading wavelength as l0_wavelength')
    data['l0_wavelength'] = nc_id.variables['wavelength'][:]
    logger.debug('reading range_gate as range_resol')
    data['range_resol'] = nc_id.variables['range_gate'][:]
    logger.debug('reading longitude')
    data['longitude'] = nc_id.variables['longitude'][:]
    logger.debug('reading latitude')
    data['latitude'] = nc_id.variables['latitude'][:]
    logger.debug('reading altitude')
    data['altitude'] = nc_id.variables['altitude'][:]
    logger.debug('reading cloud height offset (cho)')
    data['cho'] = nc_id.variables['cho'][:]
    logger.debug('reading azimuth')
    data['azimuth'] = nc_id.variables['azimuth'][:]
    if soft_vers >= 0.7:
        logger.debug('reading scaling')
        data['scaling'] = nc_id.variables['scaling'][:]

    return data


def read_timedep_vars(data, nc_id, soft_vers, time_ind, time_size, logger):
    """
    read time depedant variables in the netCDf files
    """

    ind_b = time_ind
    ind_e = time_ind + time_size

    # time dependent variables
    # ---------------------------------------------------------------------
    logger.debug('reading vertical optical range (vor)')
    data['vor'][ind_b:ind_e] = nc_id.variables['vor'][:]
    logger.debug('reading vertical optical range error (voe)')
    data['voe'][ind_b:ind_e] = nc_id.variables['voe'][:]
    logger.debug('reading total cloud cover (tcc)')
    data['tcc'][ind_b:ind_e] = nc_id.variables['tcc'][:]
    logger.debug('reading state_optics')
    data['state_optics'][ind_b:ind_e] = nc_id.variables['state_optics'][:]
    logger.debug('reading state_laser')
    data['state_laser'][ind_b:ind_e] = nc_id.variables['state_laser'][:]
    logger.debug('reading state_detector')
    data['state_detector'][ind_b:ind_e] = nc_id.variables['state_detector'][:]
    logger.debug('reading sky condition index (sci)')
    data['sci'][ind_b:ind_e] = nc_id.variables['sci'][:]
    logger.debug('reading nn1')
    data['nn1'][ind_b:ind_e] = nc_id.variables['nn1'][:]
    logger.debug('reading nn2')
    data['nn2'][ind_b:ind_e] = nc_id.variables['nn1'][:]
    logger.debug('reading nn3')
    data['nn3'][ind_b:ind_e] = nc_id.variables['nn1'][:]
    logger.debug('reading maximum detection height (mxd)')
    data['mxd'][ind_b:ind_e] = nc_id.variables['mxd'][:]
    logger.debug('reading life_time')
    data['life_time'][ind_b:ind_e] = nc_id.variables['life_time'][:]
    logger.debug('reading 31 bit service code (error_ext)')
    data['error_ext'][ind_b:ind_e] = nc_id.variables['error_ext'][:]
    logger.debug('reading base cloud cover (bcc)')
    data['bcc'][ind_b:ind_e] = nc_id.variables['bcc'][:]
    logger.debug('reading bckgrd_rcs_0 as base')
    data['bckgrd_rcs_0'][ind_b:ind_e] = nc_id.variables['base'][:]
    logger.debug('reading stddev')
    data['stddev'][ind_b:ind_e] = nc_id.variables['stddev'][:]

    # time dependant temperatures
    logger.debug('reading temp_lom')
    data['temp_lom'][ind_b:ind_e] = get_temp(nc_id.variables['temp_lom'],
                                             logger)
    logger.debug('reading temp_int')
    data['temp_int'][ind_b:ind_e] = get_temp(nc_id.variables['temp_int'],
                                             logger)
    logger.debug('reading temp_ext')
    data['temp_ext'][ind_b:ind_e] = get_temp(nc_id.variables['temp_ext'],
                                             logger)
    logger.debug('reading temp_det')
    data['temp_det'][ind_b:ind_e] = get_temp(nc_id.variables['temp_det'],
                                             logger)

    # 2d time dependent variables
    # ---------------------------------------------------------------------
    logger.debug('reading quality score for aerosol layer in PBL')
    data['pbs'][ind_b:ind_e, :] = nc_id.variables['pbs'][:]
    logger.debug('reading aerosol layer in pbl (pbl)')
    data['pbl'][ind_b:ind_e, :] = nc_id.variables['pbl'][:]
    logger.debug('reading cbh')
    data['cbh'][ind_b:ind_e, :] = nc_id.variables['cbh'][:, :]
    logger.debug('reading cloud depth (cdp)')
    data['cdp'][ind_b:ind_e, :] = nc_id.variables['cdp'][:]
    logger.debug('reading cloud depth variation (cde)')
    data['cbe'][ind_b:ind_e, :] = nc_id.variables['cbe'][:]
    logger.debug('reading cloud base height variation (cbe)')
    data['cde'][ind_b:ind_e, :] = nc_id.variables['cde'][:]
    logger.debug('reading beta_raw')
    data['beta_raw'][ind_b:ind_e, :] = nc_id.variables['beta_raw'][:]

    # Read variables depending on software version
    if soft_vers <= 0.559:
        logger.debug('reading laser_pulses as nn2')
        data['laser_pulses'][ind_b:ind_e] = nc_id.variables['nn2'][:]
    else:
        logger.debug('reading laser_pulses')
        data['laser_pulses'][ind_b:ind_e] = nc_id.variables['laser_pulses'][:]

    if soft_vers >= 0.7:
        logger.debug('reading p_calc')
        data['p_calc'][ind_b:ind_e] = nc_id.variables['p_calc'][:]

    return data


def calc_pr2(data, soft_vers, logger):
    """
    Do the calculation of the Pr² according to the sofware version of the LIDAR
    """

    # Pr²
    logger.debug('calculing Pr² using:')
    if soft_vers < 0.7:
        logger.debug('P = (beta_raw*stddev+base)*laser_pulses')
        p_raw = (
            (data['beta_raw'].T * data['stddev'] + data['bckgrd_rcs_0']) *
            data['laser_pulses'])
    else:
        # find a way to pass the overlap
        logger.debug("P = (beta_raw/r2*ovl*p_calc*scaling+base)" +
                     "*laser_pulses*range_scale")
        # Warning: For this type of file we do not correct the overlap function
        # as it is not available in the netCDf file
        p_raw = ((
            np.transpose(data['beta_raw'] / np.square(data['range']))
            * data['p_calc'] * data['scaling']
            + data['bckgrd_rcs_0']) * data['laser_pulses'])

    data['rcs_0'] = p_raw.T * np.square(data['range'])

    return data


def read_data(list_files, conf, logger):
    """
    Raw2L1 plugin to read raw data of Jenoptik CHM15K
    """

    logger.debug(
        'Start reading of data using reader for ' + BRAND + ' ' + MODEL
    )

    # analyse the files to read to get the complete size of data
    logger.info("determining size of var to read")
    vars_dim = get_vars_dim(list_files, logger)
    for dim, size in vars_dim.items():
        logger.debug(dim + ': ' + str(size))
    logger.info("initializing data output array")
    data = init_data(vars_dim, logger)

    nb_files = 0
    nb_files_read = 0
    time_ind = 0
    # Loop over the list of files
    for ifile in list_files:

        # Opening file
        try:
            raw_data = nc.Dataset(ifile, 'r')
            nb_files_read += 1
        except:
            logger.error('unable to load ' + ifile + ' trying next one')

        nb_files += 1
        logger.debug('reading %02d: ' % (nb_files) + ifile)

        # Data which only need to be read in one file
        if nb_files_read == 1:
            # get Jenoptik software version to know the method to use
            # to calculate P
            soft_vers = get_soft_version(raw_data.software_version)
            data['firmware_version'] = soft_vers
            data['instrument_id'] = raw_data.serlom
            logger.info("software version: %7.4f" % soft_vers)

            # read dimensions
            # -----------------------------------------------------------------
            logger.info("reading dimension variables")
            time_size, data = read_dim_vars(data, raw_data, logger)

            # read scalar
            # -----------------------------------------------------------------
            logger.info("reading scalar variables")
            data = read_scalar_vars(data, raw_data, soft_vers, logger)

        # Time dependant variables
        # ---------------------------------------------------------------------
        logger.info("reading time dependant variables for file %02d" %
                    nb_files_read)
        if nb_files_read > 1:
            time_size, data = read_time_var(data, raw_data, time_ind, logger)
        data = read_timedep_vars(data, raw_data, soft_vers, time_ind,
                                 time_size, logger)

        time_ind += time_size

        # Close NetCDF file
        # ---------------------------------------------------------------------
        raw_data.close()

    logger.info("reading of files: done")

    # calculate Pr²
    # ---------------------------------------------------------------------
    logger.info("calculating Pr²")
    data = calc_pr2(data, soft_vers, logger)

    if nb_files_read == 0:
        logger.critical('No file could be read')
        sys.exit(1)
    else:
        return data
