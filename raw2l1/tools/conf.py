#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Compatibility with python 3
from __future__ import print_function, division, absolute_import
import ConfigParser
import logging

def add(conf, input_args, logger):
    """
    Allow to add parameters in conf section of conf object
    """

    # Warning: for configuration file, we do not use the filename but the filehandler
    #   to access filename use, conf_file.name
    for key, value in input_args.items():
        conf.set('conf', key, value)

    return conf

def init(input_args, logger):
    """
    Load and check the INI configuration file
    """

    conf = ConfigParser.RawConfigParser()
    conf.read(input_args['conf'].name)

    # TODO: Add a function to check available values once format is fixed

    # add user input arguments to conf object
    logger.debug("adding user entered options to configuration")
    conf = add(conf, input_args, logger)

    # if in debug mode log all configuration
    if logger.getEffectiveLevel() == logging.DEBUG:
        logger.debug("raw2l1 configuration")
        for section in conf.sections():
            for key, value in conf.items(section):
                logger.debug('['+section+'] ' + key + ' : ' + repr(value))
        logger.debug("end of configuration")

    return conf