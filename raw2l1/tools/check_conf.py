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
            logger.critical(
                "%s option is missing in %s" % (opt, section))
            return False

    return True


def check_required_sections(conf, logger):
    """
    Check that section needed to configure raw2l1 are available
    """

    logger.debug("checking required configuration sections")
    for section in common.CONF_SECTIONS:
        if not conf.has_section(section):
            logger.critical("%s section is missing in configuration file")
            return False

    return True


def check_conf_options(conf, logger):
    """
    check that conf section has required options
    """

    section = 'conf'

    # check list of options
    logger.debug("checking [conf] section required options")
    if not check_list_options(conf, section, common.CONF_OPTIONS, logger):
        return False

    # check netcdf format
    option = 'netcdf_format'
    if conf.get(section, option) not in common.ALLOW_NETCDF_FMT:
        logger.critical("allow netCDF format ar : %s" % repr(common.ALLOW_NETCDF_FMT))
        return False

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
