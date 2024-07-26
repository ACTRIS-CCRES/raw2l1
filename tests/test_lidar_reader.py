import configparser
import datetime as dt
import logging
import unittest

import numpy as np

import raw2l1.tools.lidar_reader as lr


def add_arg_options(conf):
    """Add arguments needed to check loading of configuration file"""
    conf.set("conf", "date", dt.datetime(2016, 6, 10))
    conf.set("conf", "ancillary", [])

    return conf


class TestLidarReader(unittest.TestCase):
    def test_no_missing_conf(self):
        logger = logging.getLogger("dummy")

        conf = configparser.RawConfigParser()
        conf.optionxform = str
        conf.read("test/conf/readerconf_no_missing.ini")
        conf = add_arg_options(conf)

        reader = lr.RawDataReader(conf, logger)

        self.assertEqual(
            (reader.reader_conf["missing_float"], reader.reader_conf["missing_int"]),
            (-999.0, -9),
        )

    def test_no_missing_int_conf(self):
        logger = logging.getLogger("dummy")

        conf = configparser.RawConfigParser()
        conf.optionxform = str
        conf.read("test/conf/readerconf_no_missing_int.ini")
        conf = add_arg_options(conf)

        reader = lr.RawDataReader(conf, logger)

        self.assertEqual(
            (reader.reader_conf["missing_float"], reader.reader_conf["missing_int"]),
            (float(-1337), -9),
        )

    def test_no_missing_float_conf(self):
        logger = logging.getLogger("dummy")

        conf = configparser.RawConfigParser()
        conf.optionxform = str
        conf.read("test/conf/readerconf_no_missing_float.ini")
        conf = add_arg_options(conf)

        reader = lr.RawDataReader(conf, logger)

        self.assertEqual(
            (reader.reader_conf["missing_float"], reader.reader_conf["missing_int"]),
            (float(-999), -1337),
        )

    def test_no_missing_nan_float_conf(self):
        logger = logging.getLogger("dummy")

        conf = configparser.RawConfigParser()
        conf.optionxform = str
        conf.read("test/conf/readerconf_missing_float_nan.ini")
        conf = add_arg_options(conf)

        reader = lr.RawDataReader(conf, logger)

        self.assertTrue(np.isnan(reader.reader_conf["missing_float"]))


if __name__ == "__main__":
    unittest.main()
