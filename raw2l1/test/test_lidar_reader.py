#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import ConfigParser
import datetime as dt
import logging

import numpy as np

import tools.lidar_reader as lr


def add_arg_options(conf):
    """ add arguments needed to check loading of configuration file"""

    conf.set('conf', 'date', dt.datetime(2016, 6, 10))
    conf.set('conf', 'ancillary', [])

    return conf


class TestLidarReader(unittest.TestCase):

    def test_no_missing_conf(self):

        logger = logging.getLogger('dummy')

        conf = ConfigParser.RawConfigParser()
        conf.optionxform = str
        conf.read('test/conf/readerconf_no_missing.ini')
        conf = add_arg_options(conf)

        reader = lr.RawDataReader(conf, logger)

        self.assertEquals(
            (reader.reader_conf['missing_float'], reader.reader_conf['missing_int']),
            (np.float(-999.), np.int(-9)))

    def test_no_missing_int_conf(self):

        logger = logging.getLogger('dummy')

        conf = ConfigParser.RawConfigParser()
        conf.optionxform = str
        conf.read('test/conf/readerconf_no_missing_int.ini')
        conf = add_arg_options(conf)

        reader = lr.RawDataReader(conf, logger)

        self.assertEquals(
            (reader.reader_conf['missing_float'], reader.reader_conf['missing_int']),
            (np.float(-1337), np.int(-9)))

    def test_no_missing_float_conf(self):

        logger = logging.getLogger('dummy')

        conf = ConfigParser.RawConfigParser()
        conf.optionxform = str
        conf.read('test/conf/readerconf_no_missing_float.ini')
        conf = add_arg_options(conf)

        reader = lr.RawDataReader(conf, logger)

        self.assertEquals(
            (reader.reader_conf['missing_float'], reader.reader_conf['missing_int']),
            (np.float(-999), np.int(-1337)))

    def test_no_missing_nan_float_conf(self):

        logger = logging.getLogger('dummy')

        conf = ConfigParser.RawConfigParser()
        conf.optionxform = str
        conf.read('test/conf/readerconf_missing_float_nan.ini')
        conf = add_arg_options(conf)

        reader = lr.RawDataReader(conf, logger)

        self.assertTrue(np.isnan(reader.reader_conf['missing_float']))


if __name__ == '__main__':
    unittest.main()
