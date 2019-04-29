#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import subprocess
import os

import numpy as np
import netCDF4 as nc

import reader.lufft_chm15k_nimbus as reader


MAIN_DIR = os.path.dirname(os.path.dirname(__file__)) + os.sep
CONF_DIR = os.path.join(MAIN_DIR, "conf")
TEST_DIR = os.path.join(MAIN_DIR, "test")
TEST_IN_DIR = os.path.join(TEST_DIR, "input")
TEST_OUT_DIR = os.path.join(TEST_DIR, "output")
PRGM = "raw2l1.py"


class TestSoftVersionParsing(unittest.TestCase):
    """check that the parsing of software version is working"""

    def test_version_old_format(self):
        """old format of sofware version"""

        version = np.int16(235)
        version_value = reader.get_soft_version(version)

        self.assertEqual(version_value, 0.235, "old format of sofware version)")

    def test_version_lower_0747(self):
        """software version before 0.747"""

        version = "11.07.1 2.12 0.536"
        version_value = reader.get_soft_version(version)

        self.assertEqual(version_value, 0.536, "version lower than 0.747")

    def test_version_greater_0747(self):
        """software version greater or equal than 0.747"""

        version = "12.12.1 2.13 0.747 0"
        version_value = reader.get_soft_version(version)

        self.assertEqual(version_value, 0.747, "version greater equal than 0.747")


class TestChm15k(unittest.TestCase):

    IN_DIR = os.path.join(TEST_IN_DIR, "jenoptik_chm15k")
    conf_file = os.path.join(CONF_DIR, "conf_lufft_chm15k-nimbus_eprofile.ini")

    def test_chm15k_v0536(self):

        date = "20120306"
        test_ifile = os.path.join(
            self.IN_DIR, "20120306_hohenpeissenberg_CHM060028_000.nc"
        )
        test_ofile = os.path.join(TEST_OUT_DIR, "test_chm15k_v0536_20120306.nc")

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

        self.assertEqual(resp, 0, "CHM15K v0.536")

    def test_chm15k_v0556(self):

        date = "20130110"
        test_ifile = os.path.join(
            self.IN_DIR, "20130110_hohenpeissenberg_CHM060028_000.nc"
        )
        test_ofile = os.path.join(TEST_OUT_DIR, "test_chm15k_v0556_20130110.nc")

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

        self.assertEqual(resp, 0, "CHM15K v0.556")

    def test_chm15k_v0559(self):

        date = "20130718"
        test_ifile = os.path.join(
            self.IN_DIR, "20130718_hohenpeissenberg_CHM060028_000.nc"
        )
        test_ofile = os.path.join(TEST_OUT_DIR, "test_chm15k_v0559_20130718.nc")

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

        self.assertEqual(resp, 0)

    def test_chm15k_v0719(self):

        date = "20131212"
        test_ifile = os.path.join(
            self.IN_DIR, "20131212_hohenpeissenberg_CHM060028_000.nc"
        )
        test_ofile = os.path.join(TEST_OUT_DIR, "test_chm15k_v0719_20131212.nc")

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

        self.assertEqual(resp, 0, "test version v0.719")

    def test_chm15k_prob_time(self):

        date = "20120327"
        test_ifile = os.path.join(
            self.IN_DIR, "20131212_hohenpeissenberg_CHM060028_000.nc"
        )
        test_ofile = os.path.join(TEST_OUT_DIR, "test_chm15k_20120327_probtime.nc")

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

        self.assertEqual(resp, 0)

    def test_chm15k_sirta(self):

        date = "20150427"
        test_ifile = os.path.join(self.IN_DIR, "20150427_SIRTA_CHM150101_000.nc")
        test_ofile = os.path.join(TEST_OUT_DIR, "test_chm15k_20150427_sirta.nc")
        test_cfile = os.path.join(CONF_DIR, "conf_lufft_chm15k-nimbus_eprofile.ini")

        resp = subprocess.check_call(
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

        self.assertEqual(resp, 0)

    def test_chm15k_v0235(self):

        date = "20151001"
        test_ifile = os.path.join(
            self.IN_DIR,
            "ceilometer-eprofile_20151001000023_03963_A201509300000_MaceHead_CHM15K.nc",
        )
        test_ofile = os.path.join(TEST_OUT_DIR, "test_chm15k_v0235_20151001.nc")
        test_cfile = os.path.join(CONF_DIR, "conf_lufft_chm15k-nimbus_eprofile.ini")

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

    def test_chm15k_v0738(self):

        date = "20160426"
        test_ifile = os.path.join(
            self.IN_DIR,
            "ceilometer-eprofile_20160426110611_06348_A201604261055_CHM15k.nc",
        )
        test_ofile = os.path.join(
            TEST_OUT_DIR, "eprofile_20160426110611_06348_A201604261055_CHM15k.nc"
        )
        test_cfile = os.path.join(CONF_DIR, "conf_lufft_chm15k-nimbus_eprofile.ini")

        resp = subprocess.call(
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

        self.assertEqual(resp, 0, "Nimbus v0.738")


class TestChm15kOverlap(unittest.TestCase):

    IN_DIR = os.path.join(TEST_IN_DIR, "jenoptik_chm15k")
    conf_file = os.path.join(CONF_DIR, "conf_lufft_chm15k-nimbus_eprofile.ini")

    def test_chm15k_overlap_good(self):

        date = "20150427"
        test_ifile = os.path.join(self.IN_DIR, "20150427_SIRTA_CHM150101_000.nc")
        test_ovl_file = os.path.join(self.IN_DIR, "TUB140013_20150211_4096.cfg")
        test_ofile = os.path.join(
            TEST_OUT_DIR, "test_chm15k_20150427_sirta_good-ovl.nc"
        )
        test_cfile = os.path.join(CONF_DIR, "conf_lufft_chm15k-nimbus_eprofile.ini")

        resp = subprocess.check_call(
            [
                MAIN_DIR + PRGM,
                date,
                test_cfile,
                test_ifile,
                test_ofile,
                "-anc",
                test_ovl_file,
                "-log_level",
                "debug",
                "-v",
                "debug",
            ]
        )

        self.assertEqual(resp, 0, "reading overlap")

    def test_chm15k_overlap_good_conf(self):
        """
        test that the reading of overlap TUB file defined in conf file goes well
        """

        date = "20150427"
        test_ifile = os.path.join(self.IN_DIR, "20150427_SIRTA_CHM150101_000.nc")
        test_ofile = os.path.join(
            TEST_OUT_DIR, "test_chm15k_20150427_sirta_good-ovl-conf-file.nc"
        )
        test_cfile = os.path.join(self.IN_DIR, "conf_lufft_chm15k-nimbus_eprofile.ini")

        resp = subprocess.check_call(
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

        self.assertEqual(resp, 0, "reading overlap define conf file")

    def test_chm15k_overlap_bad(self):

        date = "20150427"
        test_ifile = os.path.join(self.IN_DIR, "20150427_SIRTA_CHM150101_000.nc")
        test_ovl_file = os.path.join(self.IN_DIR, "jenoptik_chm15k_overlap.txt")
        test_ofile = os.path.join(TEST_OUT_DIR, "test_chm15k_20150427_sirta_bad-ovl.nc")
        test_cfile = os.path.join(CONF_DIR, "conf_lufft_chm15k-nimbus_eprofile.ini")

        resp = subprocess.check_call(
            [
                MAIN_DIR + PRGM,
                date,
                test_cfile,
                test_ifile,
                test_ofile,
                "-anc",
                test_ovl_file,
                "-log_level",
                "debug",
                "-v",
                "debug",
            ]
        )

        self.assertEqual(resp, 0, "bad overlap file but readable")

    def test_chm15k_overlap_empty(self):

        date = "20150427"
        test_ifile = os.path.join(self.IN_DIR, "20150427_SIRTA_CHM150101_000.nc")
        test_ovl_file = os.path.join(self.IN_DIR, "empty_overlap.txt")
        test_ofile = os.path.join(
            TEST_OUT_DIR, "test_chm15k_20150427_sirta_empty-ovl.nc"
        )
        test_cfile = os.path.join(CONF_DIR, "conf_lufft_chm15k-nimbus_eprofile.ini")

        resp = subprocess.check_call(
            [
                MAIN_DIR + PRGM,
                date,
                test_cfile,
                test_ifile,
                test_ofile,
                "-anc",
                test_ovl_file,
                "-log_level",
                "debug",
                "-v",
                "debug",
            ]
        )

        self.assertEqual(resp, 0, "bad overlap file but readable")

    def test_cho_substraction(self):
        """test that the cho value is substracted from cbh"""

        missing_cbh_prod = -9
        missing_cbh_orig = -1

        date = "20161113"
        test_ifile = os.path.join(
            self.IN_DIR,
            "ceilometer-eprofile_20161113193414_06610_A201611131920_CHM15k.nc",
        )
        test_ofile = os.path.join(TEST_OUT_DIR, "validation_cho.nc")
        test_cfile = os.path.join(CONF_DIR, "conf_lufft_chm15k-nimbus_eprofile.ini")

        # create file using raw2l1
        subprocess.check_call(
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

        # read cbh from created file
        nc_prod = nc.Dataset(test_ofile)
        cbh_prod = nc_prod.variables["cloud_base_height"][:]
        cbh_prod = np.ma.filled(cbh_prod)
        cbh_prod = cbh_prod.astype(int)
        nc_prod.close()

        # read cbh from original file
        nc_orig = nc.Dataset(test_ifile)
        cbh_orig = nc_orig.variables["cbh"][:]
        cho_orig = nc_orig.variables["cho"][:]
        cbh_orig[cbh_orig != missing_cbh_orig] = (
            cbh_orig[cbh_orig != missing_cbh_orig] - cho_orig
        )
        cbh_orig[cbh_orig == missing_cbh_orig] = missing_cbh_prod

        self.assertEqual(cbh_orig.tolist(), cbh_prod.tolist(), "")


if __name__ == "__main__":
    unittest.main()
