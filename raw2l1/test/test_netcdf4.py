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


class TestCampbellScientificCS135NetCDF4(unittest.TestCase):

    IN_DIR = TEST_IN_DIR + "campbell_cs135" + os.sep
    conf_file = CONF_DIR + "conf_campbell_cs135_toprof_netcdf4.ini"

    def test_cs135_dummy_file(self):

        date = "20141030"
        test_ifile = self.IN_DIR + "cs135-20150213-message006.txt"
        test_ofile = TEST_OUT_DIR + "test_cs135-nc4_20150213_000000.nc"

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

        self.assertEqual(resp, 0, "CS135 netCDF4")


# class TestVaisalaCL31NetCDF4(unittest.TestCase):

#     IN_DIR = TEST_IN_DIR + 'vaisala_cl31' + os.sep
#     conf_file = CONF_DIR + 'conf_vaisala_cl31_toprof_netcdf4.ini'

#     def test_cl31_onehour_file(self):

#         date = '20141030'
#         test_ifile = (
#             self.IN_DIR + 'cl31_0a_z1R5mF3s_v01_20141030_*.asc'
#         )
#         test_ofile = TEST_OUT_DIR + 'test_cl31-nc4_20141030_000002.nc'

#         resp = subprocess.check_call([
#             MAIN_DIR + PRGM,
#             date,
#             self.conf_file,
#             test_ifile,
#             test_ofile,
#             '-log_level',
#             'debug'
#         ])

#         self.assertEqual(resp, 0, 'CL31 one hour file netCDF4')
