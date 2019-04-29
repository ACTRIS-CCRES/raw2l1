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


class TestLogs(unittest.TestCase):

    IN_DIR = TEST_IN_DIR + "rpg_hatpro" + os.sep

    def test_log_cinfo_finfo(self):

        date = "20150930"
        test_ifile = self.IN_DIR + "hatpro_0a_z1Imwrad-TPB_v01_20150930_000020_1436.nc"
        test_ofile = TEST_OUT_DIR + "sups_sir_mwrBL00_l2_ta_v01_201509300000020.nc"
        test_cfile = CONF_DIR + "conf_rpg_hatpro_bl00-l2-ta_toprof_netcdf4.ini"

        resp = subprocess.check_call(
            [
                MAIN_DIR + PRGM,
                date,
                test_cfile,
                test_ifile,
                test_ofile,
                "-log_level",
                "warning",
                "-v",
                "info",
            ]
        )

        self.assertEqual(resp, 0)
