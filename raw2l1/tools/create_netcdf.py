# -*- coding: utf-8 -*-

# Compatibility with python 3
from __future__ import print_function, division, absolute_import

import netCDF4 as nc
import sys
import numpy as np
import ConfigParser
from tools.read_overlap import read_overlap
from tools import common


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


def get_var_type(type_str):
    """
    Get numpy type based on type given conf file
    """

    val_type = {}
    val_type['integer'] = np.int32
    val_type['long'] = np.int64
    val_type['float'] = np.float32
    val_type['double'] = np.float64

    return val_type[type_str]


def create_netcdf_global(conf, nc_id, logger):
    """
    Create the global attribute of the netCDF file
    """

    for attr, value in conf.items('global'):
        logger.debug("adding " + attr)
        setattr(nc_id, attr, value)

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

            if 'data' in conf.get(section, 'value'):
                nc_id.createDimension(dim,
                                      data[dim].size)
            else:
                nc_id.createDimension(dim, 1)

    return None


def create_netcdf_time_var(conf, data, nc_id, logger):
    """
    Special fonction to create the time variable
    """

    units = conf.get('time', 'units')
    calendar = conf.get('time', 'calendar')
    val_type = get_var_type(conf.get('time', 'type'))

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
    data_type = get_var_type(conf.get(var_name, 'type'))

    logger.debug("adding data to " + var_name)
    if 'data' in data_val:
        nc_var[:] = data[get_data_key(data_val)]
    elif 'overlap' in data_val:
        over_fname = get_overlap_filename(data_val)
        try:
            nc_var[:] = read_overlap(over_fname, logger)
        except IOError, err:
            logger.error("problem encountered while reading overlap file")
            logger.error(repr(err))
    else:
        try:
            nc_var[:] = np.array(data_val, dtype=data_type)
        except IOError, err:
            logger.error("impossible to convert value to " +
                         repr(data_type) + "for variable " + var_name)
            logger.error(repr(err))

    return None


def add_attr_to_var(nc_var, conf, section, logger):
    """
    add attribute to the variable of the netCDF file
    """

    logger.debug("adding attributes to " + section + "variable")
    for option, value in conf.items(section):
        if option not in common.RESERV_ATTR:
            logger.debug("adding " + option + " attribute")
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
        dim = conf.get(section, 'dim')
        val_type = get_var_type(conf.get(section, 'type'))

        if dim == 'none':
            nc_var = nc_id.createVariable(var_name, val_type)
        else:
            nc_var = nc_id.createVariable(var_name, val_type,
                                          dim_to_tuple(dim))

        # Add values to the variable
        if conf.has_option(var_name, 'value'):
            add_data_to_var(nc_var, var_name, conf, data, logger)
        else:
            logger.error("No value option found for " + var_name)
            logger.error("your configuration file might contains erros")

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
    create_netcdf_global(conf, nc_id, logger)

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
