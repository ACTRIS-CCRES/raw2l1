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
    '$string$': 'string',
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
            logger.warning("107 Unable to remove section "
                           "whilst creating netCDF file '{}'".format(conf.get('conf', 'output')) +
                           repr(elt) + ' ' + repr(err))
            continue

    return list_sec


def get_var_type(type_str, conf, logger):
    """
    Get numpy type based on type given conf file
    """

    try:
        val_type = KEYS_VALTYPE[type_str]
    except KeyError:
        msg = (
            "107 Type of data '" + type_str + "' unknown using default. "
            "Check your configuration file '{}'".format(conf.get('conf', 'conf')))
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
                mess = ("107 Error creating netCDF file '{}'".format(conf.get('conf', 'output')) +
                        "no key %s in data read. Global var %s will be ignore.")
                logger.error(mess % (reader_key, attr))
        elif attr == 'add_date':
            pass
        else:
            if attr == 'history':
                value = ('created the ' +
                         dt.datetime.today().strftime('%Y-%m-%d') +
                         ' ' + value)

            setattr(nc_id, attr, value)
            logger.debug("adding %s" % attr)

    # Add year, month day for STRAT compatibility
    add_date = False
    if conf.has_option('global', 'add_date'):
        add_date = conf.get_boolean('global', 'add_date')

    if add_date:
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
            logger.warning("107 Unable to process section"
                           " whilst creating netCDF file '{}'".format(conf.get('conf', 'output')) +
                           repr(err))
            continue

        if section not in common.CONF_SECTIONS and name == dim:

            logger.debug("dimension found: " + section)
            # get dimension of data:

            # case where dimensions have no values
            if conf.has_option(section, 'size'):
                dim_size = conf.get(section, 'size')
                nc_id.createDimension(dim,
                                      int(dim_size))

            elif KEY_READERDATA in conf.get(section, 'value'):
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
    val_type = get_var_type(conf.get('time', 'type'), conf, logger)

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
    data_type = get_var_type(conf.get(var_name, 'type'), conf, logger)

    logger.debug("adding data to " + var_name)
    logger.debug(str(data_type))
    logger.debug(conf.get('conf', 'netcdf_format'))
    if KEY_READERDATA in data_val:

        # prevent problem with netCDF3 and strings
        if (data_type == 'string' and
           conf.get('conf', 'netcdf_format') == 'NETCDF3_CLASSIC'):
            logger.error(
                "107 Error creating netCDF file '{}'".format(conf.get('conf', 'output')) +
                "Raw2l1 is not able to manage string " +
                "variables with netCDF3. " +
                "You should use NETCDF4 option"
            )
        else:
            try:
                data_key = get_data_key(data_val)
                nc_var[:] = data[data_key]
            except KeyError:
                msg = "107 Error creating netCDF file '{}'".format(format(conf.get('conf', 'output')))
                msg += " key %s does not exist in read data. Exiting program"
                logger.critical(msg % data_key)
                sys.exit(1)
    elif KEY_OVERLAP in data_val:
        over_fname = get_overlap_filename(data_val)
        try:
            nc_var[:] = read_overlap(over_fname, logger)
        except IOError, err:
            logger.error(
                "107 problem encountered while reading overlap file " +
                "'{}".format(over_fname)
            )
            logger.error(repr(err))
    else:
        try:
            data_val = convert_attribute(data_val, logger)
            if not isinstance(data_val, str):
                nc_var[:] = np.array(data_val, dtype=data_type)
        except ValueError, err:
            logger.error(
                "107 Error creating netCDF file '{}'".format(conf.get('conf', 'output')) +
                "impossible to convert value to " +
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

            # special case for missing value and _FillValue
            data_type = get_var_type(conf.get(section, 'type'), conf, logger)
            if option == "missing_value" or option == "_FillValue":
                try:
                    value = np.array(value, dtype=data_type)
                except ValueError:
                    mess = (
                        "107 Error creating netCDF file '%s'"
                        "impossible to convert missing_value %s. " +
                        "Using nan or -9 depending on type")
                    logger.error(mess % (conf.get('conf', 'output'), repr(value)))
                    if data_type == np.float32 or data_type == np.float64:
                        value = np.nan
                    else:
                        value = -9

            elif option == "flag_values" or option == 'flag_masks':
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

    # define variable in case user chose compression:
    if conf.get('conf', 'netcdf_format') == 'NETCDF4':

        comp = conf.get('conf', 'netcdf4_compression')
        comp_level = conf.getint('conf', 'netcdf4_compression_level')
    else:
        comp = False
        comp_level = 0

    # loop only over sections concerning the netCDf file
    for section in filter_conf_sections(conf, logger):

        var_name = section
        logger.debug("variable " + var_name)
        dim = conf.get(section, 'dim')
        logger.debug("dimension " + dim)

        # if variable has no type is it only a dimension
        # so we don't create the variable
        try:
            val_type = get_var_type(conf.get(section, 'type'), conf, logger)
            logger.debug("type " + repr(val_type))
        except ConfigParser.NoOptionError:
            continue

        # check if fill value is defined
        if conf.has_option(section, '_FillValue'):
            fill_value = conf.get(section, '_FillValue')
        else:
            fill_value = None

        # case of string variable:
        # we have to get the precise type of data from the read variable
        if (val_type == 'string' and
           conf.get('conf', 'netcdf_format') == 'NETCDF3_CLASSIC'):
            msg = "107 Error creation netCDF file '{}".format(conf.get('conf', 'output'))
            msg += " impossible to put string variable in netCDF3 files use netCDF4 format"
            logger.error(msg)
        elif val_type == 'string':
            if var_name not in data.keys():
                tmp_var_name = get_data_key(conf.get(var_name, 'value'))
            else:
                tmp_var_name = var_name

            try:
                val_type = data[tmp_var_name].dtype
            except:
                msg = "107 Error creating netCDF file '{}".format(format(conf.get('conf', 'output')))
                msg += " impossible to determine size of string for %s"
                logger.critical(msg % var_name)
                sys.exit(1)

        if dim == KEY_NODIM:
            nc_var = nc_id.createVariable(
                var_name,
                val_type,
                zlib=comp,
                complevel=comp_level,
                fill_value=fill_value
            )
        else:
            nc_var = nc_id.createVariable(
                var_name,
                val_type,
                dim_to_tuple(dim),
                zlib=comp,
                complevel=comp_level,
                fill_value=fill_value
            )

        # Add values to the variable
        if conf.has_option(var_name, 'value'):
            add_data_to_var(nc_var, var_name, conf, data, logger)
        else:
            msg = "107 Error creating netCDF file '{}'".format(conf.get('conf', 'output'))
            msg += " No value option found for {}".format(var_name)
            msg += " - your configuration file might contains errors"
            logger.error(msg)

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
        logger.critical("107 Error trying to create the netCDF file '{}".format(format(conf.get('conf', 'output'))))
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
