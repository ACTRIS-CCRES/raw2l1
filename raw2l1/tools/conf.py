#!/usr/bin/env python

# Compatibility with python 3

import configparser
import logging


def add(conf, input_args, version, logger):
    """
    Allow to add parameters in conf section of conf object
    """

    # Warning: for configuration file, we do not use the filename but the
    # filehandler
    #   to access filename use, conf_file.name
    for key, value in list(input_args.items()):
        conf.set("conf", key, value)

    # add version in conf
    conf.set("conf", "version", version)

    return conf


def init(input_args, version, logger):
    """
    Load and check the INI configuration file
    """

    conf = configparser.RawConfigParser()
    conf.optionxform = str
    conf.read(input_args["conf"].name)

    # TODO: Add a function to check available values once format is fixed

    # add user input arguments to conf object
    logger.debug("adding user entered options to configuration")
    conf = add(conf, input_args, version, logger)

    # if in debug mode log all configuration
    if logger.getEffectiveLevel() == logging.DEBUG:
        logger.debug("raw2l1 configuration")
        for section in conf.sections():
            for key, value in conf.items(section):
                logger.debug("[" + section + "] " + key + " : " + repr(value))
        logger.debug("end of configuration")

    return conf
