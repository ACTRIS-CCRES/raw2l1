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


class TestRunHatPro(unittest.TestCase):

    IN_DIR = TEST_IN_DIR + "rpg_hatpro" + os.sep

    def test_rpg_hatpro_bl_ta_toprof(self):

        date = "20150930"
        test_ifile = (
            self.IN_DIR + "hatpro_0a_z1Imwrad-CMP-TPC_v01_20160427_000057_479.nc"
        )
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
                "debug",
            ]
        )

        self.assertEqual(resp, 0)

    def test_rpg_hatpro_bl_ta_toprof_multi_files(self):

        date = "20150901"
        test_ifile = self.IN_DIR + "hatpro_0a_z1Imwrad-CMP-TPC_v01_20160427_*.nc"
        test_ofile = TEST_OUT_DIR + "sups_sir_mwrBL00_l2_ta_v01_20150901000412.nc"
        test_cfile = CONF_DIR + "conf_rpg_hatpro_bl00-l2-ta_toprof_netcdf4.ini"

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

    def test_rpg_hatpro_ta_toprof(self):

        date = "20150930"
        test_ifile = self.IN_DIR + "hatpro_0a_z1Imwrad-TPC_v01_20150930_000542_1433.nc"
        test_ofile = TEST_OUT_DIR + "sups_sir_mwr00_l2_ta_v01_20150930000542.nc"
        test_cfile = CONF_DIR + "conf_rpg_hatpro_l2-ta_toprof_netcdf4.ini"

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

    def test_rpg_hatpro_hua_toprof(self):

        date = "20150930"
        test_ifile = self.IN_DIR + "hatpro_0a_z1Imwrad-HPC_v01_20150930_000542_1433.nc"
        test_ofile = TEST_OUT_DIR + "sups_sir_mwr00_l2_hua_v01_20150930000542.nc"
        test_cfile = CONF_DIR + "conf_rpg_hatpro_l2-hua_toprof_netcdf4.ini"

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

    def test_rpg_hatpro_clwvi_toprof(self):

        date = "20150930"
        test_ifile = self.IN_DIR + "hatpro_0a_z1Imwrad-LWP_v01_20150930_000307_1436.nc"
        test_ofile = TEST_OUT_DIR + "sups_sir_mwr00_l2_clwvi_v01_20130901000307.nc"
        test_cfile = CONF_DIR + "conf_rpg_hatpro_l2-clwvi_toprof_netcdf4.ini"

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

    def test_rpg_hatpro_prw_toprof(self):

        date = "20150930"
        test_ifile = self.IN_DIR + "hatpro_0a_z1Imwrad-IWV_v01_20150930_000307_1436.nc"
        test_ofile = TEST_OUT_DIR + "sups_sir_mwr00_l2_prw_v01_20130930000307.nc"
        test_cfile = CONF_DIR + "conf_rpg_hatpro_l2-prw_toprof_netcdf4.ini"

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

    def test_rpg_hatpro_tb_toprof(self):

        date = "20150901"
        test_ifile = self.IN_DIR + "hatpro_0a_z1Imwrad-BRT_v01_20150901*.nc"
        test_afile = self.IN_DIR + "hatpro_0a_z1Imwrad-MET_v01_20150901_*.nc"
        test_ofile = TEST_OUT_DIR + "sups_sir_mwr00_l1_tb_v01_20150901000307.nc"
        test_cfile = CONF_DIR + "conf_rpg_hatpro_l1-tb_toprof_netcdf4.ini"

        resp = subprocess.check_call(
            [
                MAIN_DIR + PRGM,
                date,
                test_cfile,
                test_ifile,
                test_ofile,
                "-anc",
                test_afile,
                "-log_level",
                "debug",
                "-v",
                "debug",
            ]
        )

        self.assertEqual(resp, 0)

    def test_rpg_hatpro_tb_bl_toprof(self):

        date = "20150901"
        test_ifile = self.IN_DIR + "hatpro_0a_z1Imwrad-BLB_v01_20150901_*.nc"
        test_afile = self.IN_DIR + "hatpro_0a_z1Imwrad-MET_v01_20150901_*.nc"
        test_ofile = TEST_OUT_DIR + "sups_sir_mwrBL00_l1_tb_v01_20150901000307.nc"
        test_cfile = CONF_DIR + "conf_rpg_hatpro_bl00-l1-tb_toprof_netcdf4.ini"

        resp = subprocess.check_call(
            [
                MAIN_DIR + PRGM,
                date,
                test_cfile,
                test_ifile,
                test_ofile,
                "-anc",
                test_afile,
                "-log_level",
                "debug",
                "-v",
                "debug",
            ]
        )

        print(resp)
        self.assertEqual(resp, 0)


if __name__ == "__main__":
    unittest.main()
