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


class TestVaisalaBugSIRTA(unittest.TestCase):

    IN_DIR = TEST_IN_DIR + "vaisala_cl31" + os.sep
    conf_file = CONF_DIR + "conf_vaisala_cl31_toprof_netcdf4.ini"

    # def test_20150911(self):

    #     date = '20150911'
    #     test_ifile = (
    #         self.IN_DIR + 'cl31_0a_z1R5mF3s_v02_20150911_*.asc'
    #     )
    #     test_ofile = TEST_OUT_DIR + 'test_cl-sirta_20150911.nc'

    #     resp = subprocess.check_call([
    #         MAIN_DIR + PRGM,
    #         date,
    #         self.conf_file,
    #         test_ifile,
    #         test_ofile,
    #         '-log_level',
    #         'debug',
    #         '-v',
    #         'debug'
    #     ])

    #     self.assertEqual(resp, 0, 'CL SIRTA bug message type')

    def test_20150603(self):

        date = "20150603"
        test_ifile = self.IN_DIR + "cl31_0a_z1R5mF3s_v02_20150603_*.asc"
        test_ofile = TEST_OUT_DIR + "test_cl-sirta_20150521.nc"

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

        self.assertEqual(resp, 0, "CL SIRTA bug message type")


if __name__ == "__main__":
    unittest.main()
