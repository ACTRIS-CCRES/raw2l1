#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import subprocess
import os

MAIN_DIR = os.path.dirname(os.path.dirname(__file__)) + os.sep
CONF_DIR = os.path.join(MAIN_DIR, 'conf')
TEST_DIR = os.path.join(MAIN_DIR, 'test')
TEST_IN_DIR = os.path.join(TEST_DIR, 'input')
TEST_OUT_DIR = os.path.join(TEST_DIR, 'output')
PRGM = "raw2l1.py"


class TestRunWLS70(unittest.TestCase):
    """test full run for leosphere WLS70 depending on input file version"""

    IN_DIR = os.path.join(TEST_IN_DIR, 'leosphere_wls')

    def test_leosphere_wls70_102(self):
        """test file version V1.0.2"""

        date = '20150930'
        test_ifile = os.path.join(
            self.IN_DIR,
            'Wls70-10-v1.0.2')
        test_ofile = os.path.join(
            TEST_OUT_DIR,
            'Wls70-10-v1.0.2.nc')
        test_cfile = os.path.join(
            CONF_DIR,
            'conf_leosphere_wls70.ini')

        resp = subprocess.call([
            os.path.join(MAIN_DIR, PRGM),
            date,
            test_cfile,
            test_ifile,
            test_ofile,
            '-v',
            'debug'
        ])

        self.assertEqual(resp, 0)

    def test_leosphere_wls70_114(self):
        """test file version V1.1.4"""

        date = '20150704'
        test_ifile = os.path.join(
            self.IN_DIR,
            'Wls70-10-v1.1.4')
        test_ofile = os.path.join(
            TEST_OUT_DIR,
            'Wls70-10-v1.1.4.nc')
        test_cfile = os.path.join(
            CONF_DIR,
            'conf_leosphere_wls70.ini')

        resp = subprocess.call([
            os.path.join(MAIN_DIR, PRGM),
            date,
            test_cfile,
            test_ifile,
            test_ofile,
            '-v',
            'debug'
        ])

        self.assertEqual(resp, 0)

    def test_leosphere_wls70_115rc1(self):
        """test file version V1.0.2"""

        date = '20150908'
        test_ifile = os.path.join(
            self.IN_DIR,
            'Wls70-10-v1.1.5-rc1')
        test_ofile = os.path.join(
            TEST_OUT_DIR,
            'Wls70-10-v1.1.5-rc1.nc')
        test_cfile = os.path.join(
            CONF_DIR,
            'conf_leosphere_wls70.ini')

        resp = subprocess.call([
            os.path.join(MAIN_DIR, PRGM),
            date,
            test_cfile,
            test_ifile,
            test_ofile,
            '-v',
            'debug'
        ])

        self.assertEqual(resp, 0)
