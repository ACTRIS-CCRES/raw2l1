#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import subprocess
import os

MAIN_DIR = os.path.dirname(os.path.dirname(__file__)) + os.sep
TEST_DIR = os.path.join(MAIN_DIR, 'test')
TEST_IN_DIR = os.path.join(TEST_DIR, 'input', 'leosphere_wls')
CONF_DIR = os.path.join(TEST_IN_DIR, 'conf')
TEST_OUT_DIR = os.path.join(TEST_DIR, 'output')
PRGM = "raw2l1.py"


class TestRunWLS7(unittest.TestCase):
    """test full run for leosphere WLS70 depending on input file version"""

    IN_DIR = os.path.join(TEST_IN_DIR, 'wls7_10min')

    def test_leosphere_wls7_102(self):
        """test file version V1.0.2"""

        date = '20110103'
        test_ifile = os.path.join(
            self.IN_DIR,
            'wls7v2-v1.0.2-wlscerea_0a_windLz1M10mn-LR_v01_20110103_142000_590.txt')
        test_ofile = os.path.join(
            TEST_OUT_DIR,
            'Wls70-10-v1.0.2.nc')
        test_cfile = os.path.join(
            CONF_DIR,
            'conf_leosphere_wls7_10min.ini')

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

    def test_leosphere_wls7_1022(self):
        """test file version V1.0.2.2"""

        date = '20110901'
        test_ifile = os.path.join(
            self.IN_DIR,
            'wls7v2-v1.0.2.2-wlscerea_0a_windLz1M10mn-LR_v01_20110110_162000_470.txt')
        test_ofile = os.path.join(
            TEST_OUT_DIR,
            'Wls70-10-v1.1.4.nc')
        test_cfile = os.path.join(
            CONF_DIR,
            'conf_leosphere_wls7_10min.ini')

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

    def test_leosphere_wls7_1024(self):
        """test file version V1.0.2.4"""

        date = '20120101'
        test_ifile = os.path.join(
            self.IN_DIR,
            'wls7v2-v1.0.2.4-wlscerea_0a_windLz1M10mn-LR_v01_20110929_144000_570.txt')
        test_ofile = os.path.join(
            TEST_OUT_DIR,
            'Wls7-111-v1.0.2.4.nc')
        test_cfile = os.path.join(
            CONF_DIR,
            'conf_leosphere_wls7_10min.ini')

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

    def test_leosphere_wls7_1112(self):
        """test file version V1.1.12"""

        date = '20150119'
        test_ifile = os.path.join(
            self.IN_DIR,
            'wls7v2-v1.1.12-wlscerea_0a_windLz1M10mn-LR_v01_20150119_154000_510.txt')
        test_ofile = os.path.join(
            TEST_OUT_DIR,
            'Wls7-111-v1.1.12.nc')
        test_cfile = os.path.join(
            CONF_DIR,
            'conf_leosphere_wls7_10min.ini')

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

    def test_leosphere_wls7_1113(self):
        """test file version V1.1.13"""

        date = '20150701'
        test_ifile = os.path.join(
            self.IN_DIR,
            'wls7v2-v1.1.13-wlscerea_0a_windLz1M10mn-LR_v01_20150602_130000_670.txt')
        test_ofile = os.path.join(
            TEST_OUT_DIR,
            'Wls7-111-v1.1.13.nc')
        test_cfile = os.path.join(
            CONF_DIR,
            'conf_leosphere_wls7_10min.ini')

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

    def test_leosphere_wls7_1113a(self):
        """test file version V1.1.13a"""

        date = '20120704'
        test_ifile = os.path.join(
            self.IN_DIR,
            'wls7v2-v1.1.3a-wlscerea_0a_windLz1M10mn-LR_v01_20120726_001000_1440.txt')
        test_ofile = os.path.join(
            TEST_OUT_DIR,
            'Wls7-111-v1.1.3.a.nc')
        test_cfile = os.path.join(
            CONF_DIR,
            'conf_leosphere_wls7_10min.ini')

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

    def test_leosphere_wls7_1115(self):
        """test file version V1.1.15"""

        date = '20160913'
        test_ifile = os.path.join(
            self.IN_DIR,
            'wls7v2-v1.1.15-wlscerea_0a_windLz1M10mn-LR_v01_20160719_090000_910.txt')
        test_ofile = os.path.join(
            TEST_OUT_DIR,
            'Wls7-111-v1.1.15.nc')
        test_cfile = os.path.join(
            CONF_DIR,
            'conf_leosphere_wls7_10min.ini')

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

    def test_leosphere_wls7_1116(self):
        """test file version V1.1.16"""

        date = '20130426'
        test_ifile = os.path.join(
            self.IN_DIR,
            'wls7v2-v1.1.6-wlscerea_0a_windLz1M10mn-LR_v01_20130426_001000_1440.txt')
        test_ofile = os.path.join(
            TEST_OUT_DIR,
            'Wls7-111-v1.1.6.nc')
        test_cfile = os.path.join(
            CONF_DIR,
            'conf_leosphere_wls7_10min.ini')

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

    def test_leosphere_wls7_1119(self):
        """test file version V1.1.19"""

        date = '20140605'
        test_ifile = os.path.join(
            self.IN_DIR,
            'wls7v2-v1.1.9-wlscerea_0a_windLz1M10mn-LR_v01_20140603_001000_1440.txt')
        test_ofile = os.path.join(
            TEST_OUT_DIR,
            'Wls7-111-v1.1.9.nc')
        test_cfile = os.path.join(
            CONF_DIR,
            'conf_leosphere_wls7_10min.ini')

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

    # def test_leosphere_wls7_2158(self):Timestamp (end of interval)
    #     """test file version V2.1.58"""

    #     date = '20100113'
    #     test_ifile = os.path.join(
    #         self.IN_DIR,
    #         'Wls7-57-v2.1.58')
    #     test_ofile = os.path.join(
    #         TEST_OUT_DIR,
    #         'Wls7-57-v2.1.58.nc')
    #     test_cfile = os.path.join(
    #         CONF_DIR,
    #         'conf_leosphere_wls7.ini')

    #     resp = subprocess.call([
    #         os.path.join(MAIN_DIR, PRGM),
    #         date,
    #         test_cfile,
    #         test_ifile,
    #         test_ofile,
    #         '-v',
    #         'debug'
    #     ])

    #     self.assertEqual(resp, 0)
