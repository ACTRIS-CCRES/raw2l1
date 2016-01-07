#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import subprocess
import os

MAIN_DIR = os.path.dirname(os.path.dirname(__file__)) + os.sep
CONF_DIR = MAIN_DIR + 'conf' + os.sep
TEST_DIR = MAIN_DIR + 'test' + os.sep
TEST_IN_DIR = TEST_DIR + os.sep + 'input' + os.sep
TEST_OUT_DIR = TEST_DIR + os.sep + 'output' + os.sep
PRGM = "raw2l1.py"


class TestHatProL2BLAirTemp(unittest.TestCase):

    IN_DIR = TEST_IN_DIR + 'rpg_hatpro' + os.sep

    def test_chm15k_toprof(self):

        date = '20150427'
        test_ifile = self.IN_DIR + 'hatpro_0a_z1Imwrad-TPB_v01_20150930_000020_1436.nc'
        test_ofile = TEST_OUT_DIR + 'sups_sir_mwrBL00_l2_ta_v01_20150930000020.nc'
        test_cfile = CONF_DIR + 'conf_rpg_hatpro_bl00-l2-ta_toprof_netcdf4.ini'

        resp = subprocess.check_call([
            MAIN_DIR + PRGM,
            date,
            test_cfile,
            test_ifile,
            test_ofile,
            '-log_level',
            'debug'
        ])

        self.assertEqual(resp, 0)


class TestHatProL2AirTemp(unittest.TestCase):

    IN_DIR = TEST_IN_DIR + 'rpg_hatpro' + os.sep

    def test_chm15k_toprof(self):

        date = '20150427'
        test_ifile = self.IN_DIR + 'hatpro_0a_z1Imwrad-TPC_v01_20150930_000542_1433.nc'
        test_ofile = TEST_OUT_DIR + 'sups_sir_mwr00_l2_ta_v01_20150930000020.nc'
        test_cfile = CONF_DIR + 'conf_rpg_hatpro_l2-ta_toprof_netcdf4.ini'

        resp = subprocess.check_call([
            MAIN_DIR + PRGM,
            date,
            test_cfile,
            test_ifile,
            test_ofile,
            '-log_level',
            'debug'
        ])

        self.assertEqual(resp, 0)


if __name__ == '__main__':
    unittest.main()
