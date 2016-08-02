# -*- coding: utf8 -*-

from __future__ import print_function, absolute_import, division

import netCDF4 as nc
import numpy as np
import datetime as dt
import sys

# brand and model of the LIDAR
BRAND = 'jenoptik'
MODEL = 'CHM15K nimbus'

NN2_FACTOR = 3e-5
CONSTANT_P_CALC = 0.05

ERR_HEX_MSG = [
    {'hex': 0x00000001, 'level': 'ERROR', 'msg': 'Signal quality'},
    {'hex': 0x00000002, 'level': 'ERROR', 'msg': 'Signal recording'},
    {'hex': 0x00000004, 'level': 'ERROR', 'msg': 'Signal values null or void'},
    {'hex': 0x00000008, 'level': 'ERROR', 'msg': 'Signal recording error channel 2 (not used for Nimbus)'},
    {'hex': 0x00000010, 'level': 'ERROR', 'msg': 'Create new NetCDF file'},
    {'hex': 0x00000020, 'level': 'ERROR', 'msg': 'Write / add to NetCDF'},
    {'hex': 0x00000040, 'level': 'ERROR', 'msg': 'RS485 telegram can not be generated, transmitted'},
    {'hex': 0x00000080, 'level': 'ERROR', 'msg': 'Mount SD card faile (test: write to raw buffer)'},
    {'hex': 0x00000100, 'level': 'ERROR', 'msg': 'Detector high voltage control failed / cable defect or absent'},
    {'hex': 0x00000200, 'level': 'ERROR', 'msg': 'Inner housing temperature out of range'},
    {'hex': 0x00000400, 'level': 'ERROR', 'msg': 'Laser optical unit temperature error'},
    {'hex': 0x00000800, 'level': 'ERROR', 'msg': 'Laser trigger not detected'},
    {'hex': 0x00001000, 'level': 'WARNING', 'msg': 'Laser driver board temperature'},
    {'hex': 0x00002000, 'level': 'ERROR', 'msg': 'Laser interlock'},
    {'hex': 0x00004000, 'level': 'ERROR', 'msg': 'Laser head temperature'},
    {'hex': 0x00008000, 'level': 'WARNING', 'msg': 'Replace Laser - ageing'},
    {'hex': 0x00010000, 'level': 'WARNING', 'msg': 'Signal quality – low signal/ noise level'},
    {'hex': 0x00020000, 'level': 'WARNING', 'msg': 'Windows contaminated'},
    {'hex': 0x00040000, 'level': 'WARNING', 'msg': 'Signal processing'},
    {'hex': 0x00080000, 'level': 'STATUS', 'msg': 'not used'},
    {'hex': 0x00100000, 'level': 'WARNING', 'msg': 'File system, fsck repaired bad sectors'},
    {'hex': 0x00200000, 'level': 'WARNING', 'msg': 'RS485 baud rate/ transfer mode reset'},
    {'hex': 0x00400000, 'level': 'WARNING', 'msg': 'AFD'},
    {'hex': 0x00800000, 'level': 'WARNING', 'msg': 'configuration problem'},
    {'hex': 0x01000000, 'level': 'WARNING', 'msg': 'Laser optical unit temperature'},
    {'hex': 0x02000000, 'level': 'WARNING', 'msg': 'External temperature'},
    {'hex': 0x04000000, 'level': 'WARNING', 'msg': 'Detector temperature out of range'},
    {'hex': 0x08000000, 'level': 'WARNING', 'msg': 'General laser issue'},
    {'hex': 0x10000000, 'level': 'STATUS', 'msg': 'NOL > 3 and standard telegram selected'},
    {'hex': 0x20000000, 'level': 'STATUS', 'msg': 'Power save mode on'},
    {'hex': 0x40000000, 'level': 'STATUS', 'msg': 'Standby mode on'},
]


def get_error_index(err_msg, logger):
    """
    based on error error message read in file. return all indexes of related msg and level
    """

    err_ind = []
    err_int = err_msg
    for i, d in enumerate(ERR_HEX_MSG):
        if bool(err_int & d['hex']):
            err_ind.append(i)

    return err_ind


def store_error(data, err_msg, logger):
    """store errors msg and their count by type"""

    err_ind = get_error_index(err_msg, logger)

    for i in err_ind:

        if ERR_HEX_MSG[i]['msg'] in data['list_errors']:
            data['list_errors'][ERR_HEX_MSG[i]['msg']]['count'] += 1
        else:
            data['list_errors'][ERR_HEX_MSG[i]['msg']] = {}
            data['list_errors'][ERR_HEX_MSG[i]['msg']]['count'] = 1
            data['list_errors'][ERR_HEX_MSG[i]['msg']]['level'] = ERR_HEX_MSG[i]['level']

    return data


def log_error_msg(data, logger):

    msg_format = '{} : {:d} message(s)'

    if len(data['list_errors']) > 0:
        logger.info('summary of instruments messages')

    for msg in data['list_errors']:

        if data['list_errors'][msg]['level'] == 'STATUS':
            logger.info(msg_format.format(msg, data['list_errors'][msg]['count']))
        elif data['list_errors'][msg]['level'] == 'WARNING':
            logger.warning(msg_format.format(msg, data['list_errors'][msg]['count']))
        elif data['list_errors'][msg]['level'] == 'ALARM':
            logger.error(msg_format.format(msg, data['list_errors'][msg]['count']))


def get_soft_version(str_version):
    """
    function to get the number of acquisition software version as a float
    """

    if type(str_version) == np.int16:
        version_nb = float(str_version) / 1000.
    else:
        version_nb = float(str_version.split(' ')[-1])

    return version_nb


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
            logger.error("109 error trying to open '{}'".format(ifile))
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
    except TypeError:
        logger.debug('Correcting temperature scale problem')
        nc_obj.set_auto_maskandscale(False)
        tmp = nc_obj[:] / np.float(nc_obj.scale_factor)

    return tmp


def init_data(vars_dim, conf, logger):
    """
    based on the analysing of the file to read initialize the np.array of
    the output data dictionnary
    """

    missing_int = conf['missing_int']
    missing_float = conf['missing_float']

    data = {}

    # meta informations
    data['meta'] = {}
    data['meta']['is_metoffice'] = False
    data['meta']['is_nn2'] = False
    data['meta']['is_p_calc'] = False

    # instrument characteristics
    # -------------------------------------------------------------------------
    data['firmware_version'] = ""
    data['instrument_id'] = ""
    data['scaling'] = np.nan

    # dimensions of the output netCDf file
    # -------------------------------------------------------------------------
    data['time'] = np.empty((vars_dim['time'],), dtype=np.dtype(dt.datetime))
    data['range'] = np.ones((vars_dim['range'],),
                            dtype=np.float32) * missing_float
    data['layer'] = np.ones((vars_dim['layer'],),
                            dtype=np.int16) * missing_int

    # scalar variables
    # -------------------------------------------------------------------------
    data['cho'] = np.nan

    # Time dependent variables
    # -------------------------------------------------------------------------
    data['vor'] = np.ones((vars_dim['time'],),
                          dtype=np.int16) * missing_int
    data['voe'] = np.ones((vars_dim['time'],),
                          dtype=np.int16) * missing_int
    data['tcc'] = np.ones((vars_dim['time'],),
                          dtype=np.int8) * missing_int
    data['stddev'] = np.ones((vars_dim['time'],),
                             dtype=np.float32) * missing_float
    data['state_optics'] = np.ones((vars_dim['time'],),
                                   dtype=np.int8) * missing_int
    data['state_laser'] = np.ones((vars_dim['time'],),
                                  dtype=np.int8) * missing_int
    data['state_detector'] = np.ones((vars_dim['time'],),
                                     dtype=np.int8) * missing_int
    data['sci'] = np.ones((vars_dim['time'],),
                          dtype=np.int8) * missing_int
    data['nn1'] = np.ones((vars_dim['time'],),
                          dtype=np.int16) * missing_int
    data['nn2'] = np.ones((vars_dim['time'],),
                          dtype=np.int16) * missing_int
    data['nn3'] = np.ones((vars_dim['time'],),
                          dtype=np.int16) * missing_int
    data['mxd'] = np.ones((vars_dim['time'],),
                          dtype=np.int16) * missing_int
    data['life_time'] = np.ones((vars_dim['time'],),
                                dtype=np.int32) * missing_int
    data['error_ext'] = np.ones((vars_dim['time'],),
                                dtype=np.int32) * missing_int
    data['temp_lom'] = np.ones((vars_dim['time'],),
                               dtype=np.int16) * missing_int
    data['temp_int'] = np.ones((vars_dim['time'],),
                               dtype=np.int16) * missing_int
    data['temp_ext'] = np.ones((vars_dim['time'],),
                               dtype=np.int16) * missing_int
    data['temp_det'] = np.ones((vars_dim['time'],),
                               dtype=np.int16) * missing_int
    data['laser_pulses'] = np.ones((vars_dim['time'],),
                                   dtype=np.int32) * missing_int
    data['error_ext'] = np.ones((vars_dim['time'],),
                                dtype=np.int32) * missing_int
    data['bcc'] = np.ones((vars_dim['time'],),
                          dtype=np.int8) * missing_int
    data['bckgrd_rcs_0'] = np.ones((vars_dim['time'],),
                                   dtype=np.float32) * missing_float
    data['average_time'] = np.ones((vars_dim['time'],),
                                   dtype=np.int32) * missing_int
    data['p_calc'] = np.ones((vars_dim['time'],),
                             dtype=np.float32) * missing_int

    # Time, layer dependent variables
    # -------------------------------------------------------------------------
    data['pbs'] = np.ones((vars_dim['time'], vars_dim['layer']),
                          dtype=np.int8) * missing_int
    data['pbl'] = np.ones((vars_dim['time'], vars_dim['layer']),
                          dtype=np.int16) * missing_int
    data['cdp'] = np.ones((vars_dim['time'], vars_dim['layer']),
                          dtype=np.int16) * missing_int
    data['cde'] = np.ones((vars_dim['time'], vars_dim['layer']),
                          dtype=np.int16) * missing_int
    data['cbh'] = np.ones((vars_dim['time'], vars_dim['layer']),
                          dtype=np.int16) * missing_int
    data['cbe'] = np.ones((vars_dim['time'], vars_dim['layer']),
                          dtype=np.int16) * missing_int

    data['list_errors'] = {}

    # Time, range dependent variables
    # -------------------------------------------------------------------------

    # for MetOffice data
    data['beta'] = np.ones((vars_dim['time'], vars_dim['range']),
                           dtype=np.float32) * missing_float
    data['beta_raw'] = np.ones((vars_dim['time'], vars_dim['range']),
                               dtype=np.float32) * missing_float
    data['rcs_0'] = np.ones((vars_dim['time'], vars_dim['range']),
                            dtype=np.float32) * missing_float

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
    logger.debug('reading azimuth')
    data['azimuth'] = nc_id.variables['azimuth'][:]
    if soft_vers > 0.235:
        logger.debug('reading cloud height offset (cho)')
        data['cho'] = nc_id.variables['cho'][:]
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
    try:
        data['nn2'][ind_b:ind_e] = nc_id.variables['nn2'][:]
        data['meta']['is_nn2'] = True
    except KeyError:
        logger.warning("nn2 variable not available")

    logger.debug('reading nn3')
    try:
        data['nn3'][ind_b:ind_e] = nc_id.variables['nn3'][:]
    except KeyError:
        logger.warning("nn3 variable not available")

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
    try:
        data['temp_lom'][ind_b:ind_e] = get_temp(nc_id.variables['temp_lom'],
                                                 logger)
    except KeyError:
        logger.warning('temp_lom variable is not available')
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
    # case of MetOffice
    try:
        data['beta'][ind_b:ind_e, :] = nc_id.variables['beta'][:]
        data['is_metoffice'] = True
        logger.debug('reading beta (MetOffice data)')
    except KeyError:
        pass

    # Read variables depending on software version
    if 0.235 < soft_vers <= 0.559:
        logger.debug('reading laser_pulses as nn2')
        data['laser_pulses'][ind_b:ind_e] = nc_id.variables['nn2'][:]
    elif soft_vers > 0.559:
        logger.debug('reading laser_pulses')
        data['laser_pulses'][ind_b:ind_e] = nc_id.variables['laser_pulses'][:]

    logger.debug('reading p_calc')
    try:
        data['p_calc'][ind_b:ind_e] = nc_id.variables['p_calc'][:]
        data['meta']['is_p_calc'] = True
    except KeyError:
        logger.debug('p_calc variable not available')

    return data


def calc_pr2(data, soft_vers, logger):
    """
    Do the calculation of the Pr² according to the sofware version of the LIDAR
    """

    # Pr²
    logger.debug('calculing Pr2 using:')
    if soft_vers < 0.7:

        # check if it is a MetOffice
        if data['meta']['is_metoffice']:
            logger.debug('using beta to get rcs_0 (MetOffice)')
            data['rcs_0'] = data['beta']
        else:

            # if p_calc not available
            if not data['meta']['is_p_calc']:

                if data['meta']['is_nn2']:
                    data['p_calc'] = data['nn2'] * NN2_FACTOR
                else:
                    # if no nn2 : assume it is constant
                    data['p_calc'] = CONSTANT_P_CALC

        logger.debug('P = (beta_raw*stddev)*p_calc')
        print('0 value P_CALC :', np.any(data['p_calc'] == 0))
        data['rcs_0'] = (
            (data['beta_raw'].T * data['stddev'] + data['bckgrd_rcs_0']) /
            data['p_calc']).T * np.square(data['range'])
    else:
        # find a way to pass the overlap
        logger.debug("P = (beta_raw/r2*ovl*p_calc*scaling+base)" +
                     "*laser_pulses*range_scale")
        # Warning: For this type of file we do not correct the overlap function
        # as it is not available in the netCDf file
        data['rcs_0'] = data['beta_raw']

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
    data = init_data(vars_dim, conf, logger)

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
            logger.error('109 unable to load ' + ifile + ' trying next one')

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

    # calculate Pr2
    # ---------------------------------------------------------------------
    logger.info("calculating Pr2")
    data = calc_pr2(data, soft_vers, logger)

    # print messages status read in the file for each time step
    for err_msg in data['error_ext'][:]:
        data = store_error(data, err_msg, logger)
    log_error_msg(data, logger)

    if nb_files_read == 0:
        for f in list_files:
            logger.critical("109 Tried to read '{}'. No file could be read".format(f))
        sys.exit(1)
    else:
        return data
