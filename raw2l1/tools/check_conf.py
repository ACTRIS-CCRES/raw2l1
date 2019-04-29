#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from tools import common


def check_list_options(conf, section, list_opts, logger):
    """
    check that one section has all required options
    """

    for opt in list_opts:
        if not conf.has_option(section, opt):
            logger.critical("107 %s option is missing in %s" % (opt, section))
            return False

    return True


def check_required_sections(conf, logger):
    """
    Check that section needed to configure raw2l1 are available
    """

    logger.debug("checking required configuration sections")
    for section in common.CONF_SECTIONS:
        if not conf.has_section(section):
            logger.critical("107 %s section is missing in configuration file")
            return False

    return True


def check_nc4_compression_option(conf, section, logger):
    """
    check options and values for netCDF4 compression
    """

    # get name of the config file in case of error/warning
    conf_file = conf.get("conf", "conf")

    # check if compression option is present
    opt = "netcdf4_compression"
    if not conf.has_option("conf", opt):
        conf.set(section, opt, "false")

    # check compression value
    val = conf.get(section, opt)
    if val not in common.ALLOW_NC4_COMP:

        msg = "107 Error Reading config file '" + conf_file + "'"
        msg += (
            " authorized values for %s option in %s section is %s. Option set to false"
        )
        logger.error(msg % (opt, section, repr(common.ALLOW_NC4_COMP)))
        conf.set(opt, section, "false")

    # check if compression level is present
    opt = "netcdf4_compression_level"
    err_msg = "107 Error Reading config file '%s'authorized value for %s option in %s section are %s. Option set to 4"
    if not conf.has_option(section, opt):
        conf.set(section, opt, "4")

    # check compression level value
    try:
        val = conf.getint(section, opt)
    except ValueError:
        logger.error(
            err_msg % (conf_file, opt, section, repr(common.ALLOW_NC4_COMP_LEVEL))
        )

    if val not in common.ALLOW_NC4_COMP_LEVEL:
        logger.error(
            err_msg % (conf_file, opt, section, repr(common.ALLOW_NC4_COMP_LEVEL))
        )


def check_conf_options(conf, logger):
    """
    check that conf section has required options
    """

    section = "conf"

    # check list of options
    logger.debug("checking [conf] section required options")
    if not check_list_options(conf, section, common.CONF_OPTIONS, logger):
        return False

    # check netcdf format
    option = "netcdf_format"
    if conf.get(section, option) not in common.ALLOW_NC_FMT:
        logger.critical("107 allow netCDF format are : %s" % repr(common.ALLOW_NC_FMT))
        return False

    # if format is NETCDF4 check compression option
    if conf.get(section, "netcdf_format") == "NETCDF4":
        check_nc4_compression_option(conf, section, logger)

    return True


def check_conf(conf, logger):
    """
    Check the data entered in the configuration file
    """

    # require sections of the configuration file
    if not check_required_sections(conf, logger):
        sys.exit(3)

    # check conf section of the configuration file
    if not check_conf_options(conf, logger):
        sys.exit(3)

    return conf
