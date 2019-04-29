#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import subprocess
import os

MAIN_DIR = os.path.dirname(os.path.dirname(__file__)) + os.sep
TEST_DIR = os.path.join(MAIN_DIR, "test")
TEST_IN_DIR = os.path.join(TEST_DIR, "input", "leosphere_wls")
CONF_DIR = os.path.join(TEST_IN_DIR, "conf")
TEST_OUT_DIR = os.path.join(TEST_DIR, "output")
PRGM = "raw2l1.py"


class TestRunWLS70T10Min(unittest.TestCase):
    """test full run for leosphere WLS70 depending on input file version"""

    IN_DIR = os.path.join(TEST_IN_DIR, "wls70_10min")

    def test_leosphere_wls70_102(self):
        """test file version V1.0.2"""

        date = "20150930"
        test_ifile = os.path.join(
            self.IN_DIR,
            "wls70-v1.0.2_wlscerea_0a_windLz1M10mn-HR_v01_20150618_001002_550.txt",
        )
        test_ofile = os.path.join(TEST_OUT_DIR, "Wls70-10-v1.0.2.nc")
        test_cfile = os.path.join(CONF_DIR, "conf_leosphere_wls70_10min.ini")

        resp = subprocess.call(
            [
                os.path.join(MAIN_DIR, PRGM),
                date,
                test_cfile,
                test_ifile,
                test_ofile,
                "-v",
                "debug",
            ]
        )

        self.assertEqual(resp, 0)

    def test_leosphere_wls70_114(self):
        """test file version V1.1.4"""

        date = "20150704"
        test_ifile = os.path.join(
            self.IN_DIR,
            "wls70-v1.1.4_wlscerea_0a_windLz1M10mn-HR_v01_20150703_121000_720.txt",
        )
        test_ofile = os.path.join(TEST_OUT_DIR, "Wls70-10-v1.1.4.nc")
        test_cfile = os.path.join(CONF_DIR, "conf_leosphere_wls70_10min.ini")

        resp = subprocess.call(
            [
                os.path.join(MAIN_DIR, PRGM),
                date,
                test_cfile,
                test_ifile,
                test_ofile,
                "-v",
                "debug",
            ]
        )

        self.assertEqual(resp, 0)

    def test_leosphere_wls70_115rc1(self):
        """test file version V1.0.2"""

        date = "20150908"
        test_ifile = os.path.join(
            self.IN_DIR,
            "wls70-v1.1.5-rc-wlscerea_0a_windLz1M10mn-HR_v01_20150909_001000_720.txt",
        )
        test_ofile = os.path.join(TEST_OUT_DIR, "Wls70-10-v1.1.5-rc1.nc")
        test_cfile = os.path.join(CONF_DIR, "conf_leosphere_wls70_10min.ini")

        resp = subprocess.call(
            [
                os.path.join(MAIN_DIR, PRGM),
                date,
                test_cfile,
                test_ifile,
                test_ofile,
                "-v",
                "debug",
            ]
        )

        self.assertEqual(resp, 0)


class TestRunWLS70T10S(unittest.TestCase):
    """test full run for leosphere WLS70 10s depending on input file version"""

    IN_DIR = os.path.join(TEST_IN_DIR, "wls70_10s")

    def test_leosphere_wls70_102(self):
        """test file version V1.0.2"""

        date = "20150930"
        test_ifile = os.path.join(
            self.IN_DIR,
            "wls70-v1.0.2_wlscerea_0a_windLz1R10s-HR_v01_20150618_000009_554.rtd",
        )
        test_ofile = os.path.join(TEST_OUT_DIR, "Wls70-10s-v1.0.2.nc")
        test_cfile = os.path.join(CONF_DIR, "conf_leosphere_wls70_10s.ini")

        resp = subprocess.call(
            [
                os.path.join(MAIN_DIR, PRGM),
                date,
                test_cfile,
                test_ifile,
                test_ofile,
                "-v",
                "debug",
            ]
        )

        self.assertEqual(resp, 0)

    def test_leosphere_wls70_114(self):
        """test file version V1.1.4"""

        date = "20150704"
        test_ifile = os.path.join(
            self.IN_DIR,
            "wls70-v1.1.4_wlscerea_0a_windLz1R10s-HR_v01_20150703_110643_54.rtd",
        )
        test_ofile = os.path.join(TEST_OUT_DIR, "Wls70-10s-v1.1.4.nc")
        test_cfile = os.path.join(CONF_DIR, "conf_leosphere_wls70_10s.ini")

        resp = subprocess.call(
            [
                os.path.join(MAIN_DIR, PRGM),
                date,
                test_cfile,
                test_ifile,
                test_ofile,
                "-v",
                "debug",
            ]
        )

        self.assertEqual(resp, 0)

    def test_leosphere_wls70_115rc1(self):
        """test file version V1.1.5rc"""

        date = "20150908"
        test_ifile = os.path.join(
            self.IN_DIR,
            "wls70-v1.1.5-rc_wlscerea_0a_windLz1R10s-HR_v01_20150909_120001_721.rtd",
        )
        test_ofile = os.path.join(TEST_OUT_DIR, "Wls70-10s-v1.1.5-rc1.nc")
        test_cfile = os.path.join(CONF_DIR, "conf_leosphere_wls70_10s.ini")

        resp = subprocess.call(
            [
                os.path.join(MAIN_DIR, PRGM),
                date,
                test_cfile,
                test_ifile,
                test_ofile,
                "-v",
                "debug",
            ]
        )

        self.assertEqual(resp, 0)
