#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import subprocess
import os

MAIN_DIR = os.path.dirname(os.path.dirname(__file__)) + os.sep
CONF_DIR = MAIN_DIR + 'conf' + os.sep
TEST_DIR = MAIN_DIR + 'test' + os.sep
TEST_IN_DIR = TEST_DIR + os.sep + 'input' + os.sep
TEST_OUT_DIR = TEST_DIR + os.sep + 'output' + os.sep
PRGM = "raw2l1.py"


class TestVaisalaCL31(unittest.TestCase):

    IN_DIR = TEST_IN_DIR + 'vaisala_cl31' + os.sep
    conf_file = CONF_DIR + 'conf_vaisala_cl31.ini'

    def test_cl31_onehour_file(self):

        date = '20141030'
        test_ifile = (
            self.IN_DIR + 'cl31_0a_z1R5mF3s_v01_20141030_000002_61.asc'
        )
        test_ofile = TEST_OUT_DIR + 'test_cl31_20141030_000002.nc'

        resp = subprocess.check_call([
            MAIN_DIR + PRGM,
            date,
            self.conf_file,
            test_ifile,
            test_ofile,
            '-log_level',
            'debug'
        ])

        self.assertEqual(resp, 0, 'CL31 one hour file')


class TestVaisalaCL51(unittest.TestCase):

    IN_DIR = TEST_IN_DIR + 'vaisala_cl51' + os.sep
    conf_file = CONF_DIR + 'conf_vaisala_cl51.ini'

    def test_cl51_oneday_file(self):

        date = '20140901'
        test_ifile = (
            self.IN_DIR + 'h4090100.dat'
        )
        test_ofile = TEST_OUT_DIR + 'test_cl51_20140901.nc'

        resp = subprocess.check_call([
            MAIN_DIR + PRGM,
            date,
            self.conf_file,
            test_ifile,
            test_ofile,
            '-log_level',
            'debug'
        ])

        self.assertEqual(resp, 0, 'CL51 one hour file')

if __name__ == '__main__':
    unittest.main()
