#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import subprocess
import os

MAIN_DIR = os.path.dirname(os.path.dirname(__file__)) + os.sep
CONF_DIR = MAIN_DIR + "conf" + os.sep
TEST_DIR = MAIN_DIR + "test" + os.sep
TEST_IN_DIR = TEST_DIR + os.sep + "input" + os.sep
TEST_OUT_DIR = TEST_DIR + os.sep + "output" + os.sep
PRGM = "raw2l1.py"


class TestChm15kToprof(unittest.TestCase):

    IN_DIR = TEST_IN_DIR + "jenoptik_chm15k" + os.sep
    conf_file = CONF_DIR + "conf_lufft_chm15k-nimbus_toprof.ini"

    def test_chm15k_toprof(self):

        date = "20150427"
        test_ifile = self.IN_DIR + "20150427_SIRTA_CHM150101_000.nc"
        test_ofile = TEST_OUT_DIR + "test_chm15k_20150427_sirta_toprof.nc"
        test_cfile = CONF_DIR + "conf_lufft_chm15k-nimbus_toprof.ini"

        resp = subprocess.check_call(
            [
                MAIN_DIR + PRGM,
                date,
                test_cfile,
                test_ifile,
                test_ofile,
                "-log_level",
                "debug",
            ]
        )

        self.assertEqual(resp, 0)


class TestVaisalaCL31Toprof(unittest.TestCase):

    IN_DIR = TEST_IN_DIR + "vaisala_cl31" + os.sep
    conf_file = CONF_DIR + "conf_vaisala_cl31_toprof.ini"

    def test_cl31_onehour_file(self):

        date = "20141030"
        test_ifile = self.IN_DIR + "cl31_0a_z1R5mF3s_v01_20141030_*.asc"
        test_ofile = TEST_OUT_DIR + "test_cl31_20141030_toprof.nc"

        resp = subprocess.check_call(
            [
                MAIN_DIR + PRGM,
                date,
                self.conf_file,
                test_ifile,
                test_ofile,
                "-log_level",
                "debug",
            ]
        )

        self.assertEqual(resp, 0, "CL31 one hour file")


class TestVaisalaCL51Toprof(unittest.TestCase):

    IN_DIR = TEST_IN_DIR + "vaisala_cl51" + os.sep
    conf_file = CONF_DIR + "conf_vaisala_cl51_toprof.ini"

    def test_cl51_oneday_file(self):

        date = "20140901"
        test_ifile = self.IN_DIR + "h4090100.dat"
        test_ofile = TEST_OUT_DIR + "test_cl51_20140901_toprof.nc"

        resp = subprocess.check_call(
            [
                MAIN_DIR + PRGM,
                date,
                self.conf_file,
                test_ifile,
                test_ofile,
                "-log_level",
                "debug",
            ]
        )

        self.assertEqual(resp, 0, "CL51 one hour file")


if __name__ == "__main__":
    unittest.main()
