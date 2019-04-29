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


class TestCampbellScientificCS135(unittest.TestCase):
    """Test for CS135 data in campbell Scientific format"""

    IN_DIR = TEST_IN_DIR + "campbell_cs135" + os.sep
    conf_file = CONF_DIR + "conf_campbell_cs135_toprof.ini"

    def test_cs135_dummy_file(self):

        date = "20141030"
        test_ifile = self.IN_DIR + "cs135-20150213-message006.txt"
        test_ofile = TEST_OUT_DIR + "test_cs135_20150213_000000.nc"

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

        self.assertEqual(resp, 0, "CS135 ")


class TestCampbellScientificCS135ModeCL31(unittest.TestCase):
    """Test for CS135 data in vaisala format"""

    IN_DIR = TEST_IN_DIR + "campbell_cs135" + os.sep
    conf_file = IN_DIR + "conf_cs135-cl31_toprof.ini"

    def test_cs135_dummy_file(self):

        date = "20150703"
        test_ifile = self.IN_DIR + "15070300.DAT"
        test_ofile = TEST_OUT_DIR + "test_cs135_20150703_000000.nc"

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
                "error",
            ]
        )

        self.assertEqual(resp, 0, "CS135 ")


# class TestCampbellScientificCS135RealFile(unittest.TestCase):
#     """Test with ceilinex file. file remove by mistake"""

#     IN_DIR = TEST_IN_DIR + 'campbell_cs135' + os.sep
#     conf_file = IN_DIR + 'conf_campbell_cs135_toprof_netcdf4.ini'

#     def test_cs135_dummy_file(self):

#         date = '20150903'
#         test_ifile = (
#             self.IN_DIR + 'CS2_20150903.bin'
#         )
#         test_ofile = TEST_OUT_DIR + 'test_cs135_20150903_000000.nc'

#         resp = subprocess.check_call([
#             MAIN_DIR + PRGM,
#             date,
#             self.conf_file,
#             test_ifile,
#             test_ofile,
#             '-log_level',
#             'debug'
#         ])

#         self.assertEqual(resp, 0, 'CS135 ')

if __name__ == "__main__":
    unittest.main()
