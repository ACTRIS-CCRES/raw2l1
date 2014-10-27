# -*- coding: utf8 -*-

from __future__ import print_function, absolute_import, division

import netCDF4 as nc
import numpy as np

# brand and model of the LIDAR
BRAND = 'jenoptik'
MODEL = 'CHM15K'


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


def read_data(list_files, logger):
    """
    Raw2L1 plugin to read raw data of Jenoptik CHM15K
    """

    logger.debug(
        'Start reading of data using reader for ' + BRAND + ' ' + MODEL
    )

    data = {}

    nb_files = 0
    nb_files_read = 0
    # Loop over the list of files
    for ifile in list_files:

        # Opening file
        try:
            raw_data = nc.Dataset(ifile, 'r')
        except:
            logger.error('unable to load ' + ifile + ' trying next one')
            pass

        nb_files += 1
        nb_files_read += 1
        logger.debug('reading %02d: ' % (nb_files) + ifile)

        # get Jenoptik software version to know the method to use
        # to calculate P
        soft_vers = get_soft_version(raw_data.software_version)
        logger.info("software version: %7.4f" % soft_vers)

        # read dimensions
        #---------------------------------------------------------------------
        logger.debug('reading time and convert it into datetime object')
        data['time'] = date_to_dt(
            raw_data.variables['time'][:], raw_data.variables['time'].units)
        logger.debug('reading range')
        data['range'] = raw_data.variables['range'][:]
        logger.debug('reading layer')
        data['layer'] = raw_data.variables['layer'][:]

        # read scalar
        #---------------------------------------------------------------------
        logger.debug('reading zenith')
        data['zenith'] = raw_data.variables['zenith'][:]
        logger.debug('reading wavelength')
        data['wavelength'] = raw_data.variables['wavelength'][:]
        logger.debug('reading range_gate as range_resol')
        data['range_resol'] = raw_data.variables['range_gate'][:]
        logger.debug('reading longitude')
        data['longitude'] = raw_data.variables['longitude'][:]
        logger.debug('reading latitude')
        data['latitude'] = raw_data.variables['latitude'][:]
        logger.debug('reading altitude')
        data['altitude'] = raw_data.variables['altitude'][:]
        logger.debug('reading cloud height offset (cho)')
        data['cho'] = raw_data.variables['cho'][:]
        logger.debug('reading azimuth')
        data['azimuth'] = raw_data.variables['azimuth'][:]

        # Time dependant variables
        #---------------------------------------------------------------------
        logger.debug('reading vertical optical range (vor)')
        data['vor'] = raw_data.variables['vor'][:]
        logger.debug('reading vertical optical range error (voe)')
        data['voe'] = raw_data.variables['voe'][:]
        logger.debug('reading total cloud cover (tcc)')
        data['tcc'] = raw_data.variables['tcc'][:]
        logger.debug('reading state_optics')
        data['state_optics'] = raw_data.variables['state_optics'][:]
        logger.debug('reading state_laser')
        data['state_laser'] = raw_data.variables['state_laser'][:]
        logger.debug('reading state_detector')
        data['state_detector'] = raw_data.variables['state_detector'][:]
        logger.debug('reading sky condition index (sci)')
        data['sci'] = raw_data.variables['sci'][:]
        logger.debug('reading quality score for aerosol lyer in PBL')
        data['pbs'] = raw_data.variables['pbs'][:]
        logger.debug('reading nn1')
        data['nn1'] = raw_data.variables['nn1'][:]
        logger.debug('reading nn2')
        data['nn2'] = raw_data.variables['nn1'][:]
        logger.debug('reading nn3')
        data['nn3'] = raw_data.variables['nn1'][:]
        logger.debug('reading maximum detection height (mxd)')
        data['mxd'] = raw_data.variables['mxd'][:]
        logger.debug('reading life_time')
        data['life_time'] = raw_data.variables['life_time'][:]
        logger.debug('reading 31 bit service code (error_ext)')
        data['error_ext'] = raw_data.variables['error_ext'][:]
        logger.debug('reading base cloud cover (bcc)')
        data['bcc'] = raw_data.variables['bcc'][:]

        # time dependant temperatures
        #---------------------------------------------------------------------
        logger.debug('reading temp_lom')
        data['temp_lom'] = get_temp(raw_data.variables['temp_lom'], logger)
        logger.debug('reading temp_int')
        data['temp_int'] = get_temp(raw_data.variables['temp_int'], logger)
        logger.debug('reading temp_ext')
        data['temp_ext'] = get_temp(raw_data.variables['temp_ext'], logger)
        logger.debug('reading temp_det')
        data['temp_det'] = get_temp(raw_data.variables['temp_det'], logger)

        # time, layer dependant variables
        #---------------------------------------------------------------------
        logger.debug('reading aerosol layer in pbl (pbl)')
        data['pbl'] = raw_data.variables['pbl'][:]
        logger.debug('reading cbh')
        data['cbh'] = raw_data.variables['cbh'][:, :]
        logger.debug('reading cloud depth (cdp)')
        data['cdp'] = raw_data.variables['cdp'][:]
        logger.debug('reading cloud depth variation (cde)')
        data['cde'] = raw_data.variables['cde'][:]
        logger.debug('reading cloud base height variation (cbe)')
        data['cde'] = raw_data.variables['cde'][:]

        # calculate Pr²
        #---------------------------------------------------------------------
        logger.debug('reading beta_raw')
        data['beta_raw'] = raw_data.variables['beta_raw'][:, :]
        logger.debug('reading stddev')
        data['stddev'] = raw_data.variables['stddev'][:]
        logger.debug('reading bckgrd_rcs_0 as base')
        data['bckgrd_rcs_0'] = raw_data.variables['base'][:]

        # Read variables depending on software version
        if soft_vers <= 0.559:
            logger.debug('reading laser_pulses as nn2')
            data['laser_pulses'] = raw_data.variables['nn2'][:]
        else:
            logger.debug('reading laser_pulses')
            data['laser_pulses'] = raw_data.variables['laser_pulses'][:]

        if soft_vers >= 0.7:
            logger.debug('reading scaling')
            data['scaling'] = raw_data.variables['scaling'][:]
            logger.debug('reading p_calc')
            data['p_calc'] = raw_data.variables['p_calc'][:]

        # Pr²
        logger.debug('calculing Pr² using:')
        if soft_vers < 0.7:
            logger.debug('P = (beta_raw*stddev+base)*laser_pulses')
            p = ((data['beta_raw'].T * data['stddev'] +
                  data['bckgrd_rcs_0'])
                 * data['laser_pulses']).T
        else:
            # find a way to pass the overlap
            logger.debug("P = (beta_raw/r2*ovl*p_calc*scaling+base)*laser_pulses*range_scale")
            p = ((
                (data['beta_raw'] / np.square(data['range'])).T
                * data['p_calc'] * data['scaling']
                + data['bckgrd_rcs_0'])
                * data['laser_pulses']).T

        data['rcs_0'] = p * np.square(data['range'])

        # Close NetCDF file
        #---------------------------------------------------------------------
        raw_data.close()

    if nb_files_read == 0:
        logger.critical('No file could be read')
        return None
    else:
        return data
