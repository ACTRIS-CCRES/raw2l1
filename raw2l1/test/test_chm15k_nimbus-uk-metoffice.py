#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import subprocess
import os

MAIN_DIR = os.path.dirname(os.path.dirname(__file__)) + os.sep
CONF_DIR = os.path.join(MAIN_DIR, "conf")
TEST_DIR = os.path.join(MAIN_DIR, "test")
TEST_IN_DIR = os.path.join(TEST_DIR, "input")
TEST_OUT_DIR = os.path.join(TEST_DIR, "output")
PRGM = "raw2l1.py"


class TestChm15kMetOffice(unittest.TestCase):

    IN_DIR = os.path.join(TEST_IN_DIR, "jenoptik_chm15k")
    conf_file = os.path.join(
        CONF_DIR, "conf_lufft_chm15k-nimbus-uk-metoffice_eprofile.ini"
    )

    def test_20160514(self):

        date = "20160514"
        test_ifile = os.path.join(
            self.IN_DIR,
            "metoffice-jenoptick-chm15k-nimbus-ceilometer_aldergrove_201605140000.nc",
        )
        test_ofile = os.path.join(TEST_OUT_DIR, "test_chm15k_metoffice.nc")
        test_cfile = os.path.join(
            CONF_DIR, "conf_lufft_chm15k-nimbus-uk-metoffice_eprofile.ini"
        )

        resp = subprocess.call(
            [
                MAIN_DIR + PRGM,
                date,
                test_cfile,
                test_ifile,
                test_ofile,
                "-log_level",
                "debug",
                "-v",
                "debug",
            ]
        )

        self.assertEqual(resp, 0, "Nimbus metoffice 20160514")


if __name__ == "__main__":
    unittest.main()
