#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, division, absolute_import

import os
import sys
from importlib import import_module


class RawDataReader:
    def __init__(self, conf, logger):
        self.conf = conf
        self.logger = logger
        self.data_reader = conf.get
        self.reader_mod = self.__load_reader__()
        self.data = {}

    def __load_reader__(self):

        reader_dir = self.conf.get('conf', 'reader_dir')
        reader_name = self.conf.get('conf', 'reader')

        self.logger.info("loading lidar data reader module: " + reader_name)
        try:
            reader_mod = import_module(
                reader_dir + "." + self.conf.get('conf', 'reader'))
        except Exception, err:
            self.logger.critical("unable to load lidar data reader")
            self.logger.critical(err)
            self.logger.critical("quitting raw2l1")
            sys.exit(1)

        self.logger.info("loading " + reader_name + " : success")

        self.logger.info("loading read_data function from " + reader_name)
        try:
            reader_fcn = getattr(reader_mod, 'read_data')
        except Exception, err:
            self.logger.critical("unable find read_data function")
            self.logger.critical(err)
            self.logger.critical("quitting raw2l1")
            sys.exit(1)
        self.logger.info("loading read_data function : success")

        return reader_fcn

    def read_data(self):

        self.data = self.reader_mod(
            [self.conf.get('conf', 'input')], self.logger)
