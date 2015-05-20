# -*- coding: utf-8 -*-

# Compatibility with python 3
from __future__ import print_function, division, absolute_import

import netCDF4 as nc
import sys
import datetime as dt
import numpy as np
import ConfigParser
from ast import literal_eval
from tools.read_overlap import read_overlap
from tools import common

KEY_READERDATA = '$reader_data$'
KEY_OVERLAP = '$overlap$'
KEY_NODIM = '$none$'
KEYS_VALTYPE = {
    '$short$': np.int16,
    '$integer$': np.int32,
    '$long$': np.int64,
    '$float$': np.float32,
    '$double$': np.float64,
    'default': np.float64,
}


def dim_to_tuple(dim):
    """
    convert a list of dimension into a tuple compatible with netCDF4 module
    syntax
    """

    list_dim = dim.replace(" ", "").split(',')

    return tuple(list_dim)


def get_n_dim(dim):
    """
    return the number of dimension of a variable
    """

    return len(dim.split(','))


def get_overlap_filename(option):
    """
    return the name of the overlap file to read based on the option value
    in the configuration file
    """

    return option.split(',')[1].strip(' ')


def get_data_key(option):
    """
    Extract key name of data dictionnary which value will be written in
    the netCDF variable
    """

    return option.split(',')[1].strip(' ')


def filter_conf_sections(conf, logger):
    """
    Remove unneeded sections of configuration file for the creation of
    the netCDF file and sections with special processing (time)
    """

    sections_to_rm = common.CONF_SECTIONS
    for sec in common.SPEC_SECTIONS:
        sections_to_rm.append(sec)

    list_sec = conf.sections()

    for elt in sections_to_rm:
        try:
            list_sec.remove(elt)
        except ValueError, err:
            logger.warning(repr(elt) + ' ' + repr(err))
            continue

    return list_sec


def get_var_type(type_str, logger):
    """
    Get numpy type based on type given conf file
    """

    try:
        val_type = KEYS_VALTYPE[type_str]
    except KeyError:
        msg = (
            "Type of data '" + type_str + "' unknown using default. " +
            "Check your configuration file")
        logger.error(msg)
        val_type = np.float64

    return val_type


def convert_attribute(value, logger):
    """
    Try to convert an attribute read in configuration into a python variable
    """

    try:
        value = literal_eval(value)
        msg = "converting attribute to %s"
        logger.debug(msg % type(value))
    except (ValueError, SyntaxError):
        pass

    return value


def create_netcdf_global(conf, nc_id, data, logger):
    """
    Create the global attribute of the netCDF file
    """

    for attr, value in conf.items('global'):
        if KEY_READERDATA in value:
            reader_key = get_data_key(value)
            try:
                setattr(nc_id, attr, data[reader_key])
                logger.debug("adding %s" % attr)
            except KeyError:
                mess = "no key %s in data read. Global var %s will be ignore."
                logger.error(mess % (reader_key, attr))
        else:
            if attr == 'history':
                value = ('created the ' +
                         dt.datetime.today().strftime('%Y-%m-%d') +
                         ' ' + value)

            setattr(nc_id, attr, value)
            logger.debug("adding %s" % attr)

    # Add year, month day for STRAT compatibility
    dt_date = conf.get('conf', 'date')
    setattr(nc_id, 'year', int(dt_date.strftime('%Y')))
    setattr(nc_id, 'month', int(dt_date.strftime('%m')))
    setattr(nc_id, 'day', int(dt_date.strftime('%d')))

    return None


def create_netcdf_time_dim(nc_id, logger):
    """
    Special function to create time dimension as its dimension is unlimited
    """

    logger.debug("dimension found: time")
    nc_id.createDimension('time', None)

    return None


def create_netcdf_dim(conf, data, nc_id, logger):
    """
    Create the dimensions of the netCDF file
    """

    # loop only over section concerning the netCDf file
    for section in filter_conf_sections(conf, logger):

        # process only section concerning the output file
        try:
            dim = conf.get(section, 'dim')
            name = section
        except ConfigParser.NoSectionError, err:
            logger.warning(repr(err))
            continue

        if section not in common.CONF_SECTIONS and name == dim:

            logger.debug("dimension found: " + section)
            # get dimension of data:

            if KEY_READERDATA in conf.get(section, 'value'):
                try:
                    nc_id.createDimension(dim,
                                          data[dim].size)
                except:
                    val_key = get_data_key(conf.get(section, 'value'))
                    nc_id.createDimension(dim,
                                          data[val_key].size)
            else:
                nc_id.createDimension(dim, 1)

    return None


def create_netcdf_time_var(conf, data, nc_id, logger):
    """
    Special fonction to create the time variable
    """

    units = conf.get('time', 'units')
    calendar = conf.get('time', 'calendar')
    val_type = get_var_type(conf.get('time', 'type'), logger)

    nc_var = nc_id.createVariable('time', val_type, ('time',))

    logger.debug("converting time to CF compliant format")
    nc_var[:] = nc.date2num(data['time'], units=units, calendar=calendar)

    logger.debug("adding attributes to time variable")
    add_attr_to_var(nc_var, conf, 'time', logger)

    return None


def add_data_to_var(nc_var, var_name, conf, data, logger):
    """
    add the values to a variables
    """

    data_val = conf.get(var_name, 'value')
    data_type = get_var_type(conf.get(var_name, 'type'), logger)

    logger.debug("adding data to " + var_name)
    if KEY_READERDATA in data_val:
        try:
            data_key = get_data_key(data_val)
            nc_var[:] = data[data_key]
        except KeyError:
            mess = "key %s does not exist in read data. Exiting program"
            logger.critical(mess % data_key)
            sys.exit(1)
    elif KEY_OVERLAP in data_val:
        over_fname = get_overlap_filename(data_val)
        try:
            nc_var[:] = read_overlap(over_fname, logger)
        except IOError, err:
            logger.error("problem encountered while reading overlap file")
            logger.error(repr(err))
    else:
        try:
            nc_var[:] = np.array(data_val, dtype=data_type)
        except ValueError, err:
            logger.error("impossible to convert value to " +
                         repr(data_type) + "for variable " + var_name)
            logger.error(repr(err))

    return None


def add_attr_to_var(nc_var, conf, section, logger):
    """
    add attribute to the variable of the netCDF file
    """

    logger.debug("adding attributes to %s variable" % section)
    for option, value in conf.items(section):
        if option not in common.RESERV_ATTR:

            # special case for missing value
            data_type = get_var_type(conf.get(section, 'type'), logger)
            if option == "missing_value":
                try:
                    value = np.array(value, dtype=data_type)
                except ValueError:
                    mess = ("impossible to convert missing_value %s. " +
                            "Using nan or -9 depending on type")
                    logger.error(mess % repr(value))
                    if data_type == np.float32 or data_type == np.float64:
                        value = np.nan
                    else:
                        value = -9

            elif option == "flag_values":
                value = convert_attribute(value, logger)
                if not isinstance(value, str):
                    value = np.array(value, dtype=data_type)

            # attributes we don't know if they are string
            if option not in common.STRING_ATTR:
                value = convert_attribute(value, logger)

            logger.debug("adding %s attribute %s" % (option, repr(value)))
            setattr(nc_var, option, value)

    return None


def create_netcdf_variables(conf, data, nc_id, logger):
    """
    create netCDF variable and add attributes found in
    the configuration file
    """

    # loop only over sections concerning the netCDf file
    for section in filter_conf_sections(conf, logger):

        var_name = section
        logger.debug("variable " + var_name)
        dim = conf.get(section, 'dim')
        logger.debug("dimension " + dim)
        val_type = get_var_type(conf.get(section, 'type'), logger)
        logger.debug("type " + repr(val_type))

        if dim == KEY_NODIM:
            nc_var = nc_id.createVariable(var_name, val_type)
        else:
            nc_var = nc_id.createVariable(var_name, val_type,
                                          dim_to_tuple(dim))

        # Add values to the variable
        if conf.has_option(var_name, 'value'):
            add_data_to_var(nc_var, var_name, conf, data, logger)
        else:
            logger.error("No value option found for " + var_name)
            logger.error("your configuration file might contains errors")

        # add attributes to the variable
        add_attr_to_var(nc_var, conf, section, logger)

    return None


def create_netcdf(conf, data, logger):
    """
    Create and write in the netCDf file
    """

    status = 0

    # open netCDF file
    # -------------------------------------------------------------------------
    logger.info("create netCDF file " + conf.get('conf', 'output'))
    try:
        nc_id = nc.Dataset(conf.get('conf', 'output'),
                           'w',
                           format=conf.get('conf', 'netcdf_format'))
    except IOError, err:
        logger.critical("error trying to create the netCDF file")
        logger.critical(err)
        logger.critical("quitting raw2l1")
        sys.exit(1)

    # write global attributes in netCDF file
    # -------------------------------------------------------------------------
    logger.info("adding global attributes")
    create_netcdf_global(conf, nc_id, data, logger)

    # write dimension of the netCDF file
    # -------------------------------------------------------------------------
    logger.info("creating dimensions")
    create_netcdf_time_dim(nc_id, logger)
    create_netcdf_dim(conf, data, nc_id, logger)

    # write variables in netCDf file
    # -------------------------------------------------------------------------
    logger.info("creating variables")
    logger.debug("creating time variable")
    create_netcdf_time_var(conf, data, nc_id, logger)
    create_netcdf_variables(conf, data, nc_id, logger)

    nc_id.close()

    return status
