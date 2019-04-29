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


class TestSigmaSpaceMiniMPL(unittest.TestCase):

    IN_DIR = TEST_IN_DIR + "sigmaspace_minimpl" + os.sep
    conf_file = CONF_DIR + "conf_sigmaspace_minimpl_eprofile.ini"

    def test_5min_file(self):

        date = "20160601"
        test_ifile = self.IN_DIR + "MPL_5030_201606010000.nc"
        test_ofile = TEST_OUT_DIR + "test_minimpl_20160601_5min.nc"

        resp = subprocess.check_call(
            [
                MAIN_DIR + PRGM,
                date,
                self.conf_file,
                test_ifile,
                test_ofile,
                "-log_level",
                "debug",
                "-v",
                "debug",
            ]
        )

        self.assertEqual(resp, 0, "miniMPL one file")

    def test_1h_file(self):

        date = "20160601"
        test_ifile = self.IN_DIR + "MPL_5030_20160601*.nc"
        test_ofile = TEST_OUT_DIR + "test_minimpl_20160601_1h.nc"

        resp = subprocess.check_call(
            [
                MAIN_DIR + PRGM,
                date,
                self.conf_file,
                test_ifile,
                test_ofile,
                "-log_level",
                "debug",
                "-v",
                "debug",
            ]
        )

        self.assertEqual(resp, 0, "miniMPL 1h")


if __name__ == "__main__":
    unittest.main()
