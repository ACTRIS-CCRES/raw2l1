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


class TestChm15k(unittest.TestCase):

    IN_DIR = TEST_IN_DIR + 'jenoptik_chm15k' + os.sep
    conf_file = CONF_DIR + 'conf_jenoptik_chm15k.ini'

    def test_chm15k_v0536(self):

        date = '20120306'
        test_ifile = self.IN_DIR + '20120306_hohenpeissenberg_CHM060028_000.nc'
        test_ofile = TEST_OUT_DIR + 'test_chm15k_20120306.nc'

        resp = subprocess.check_call([
            MAIN_DIR + PRGM,
            date,
            self.conf_file,
            test_ifile,
            test_ofile,
            '-log_level',
            'debug'
        ])

        self.assertEqual(resp, 0, 'CHM15K v0.536')

    def test_chm15k_v0556(self):

        date = '20130110'
        test_ifile = self.IN_DIR + '20130110_hohenpeissenberg_CHM060028_000.nc'
        test_ofile = TEST_OUT_DIR + 'test_chm15k_20130110.nc'

        resp = subprocess.check_call([
            MAIN_DIR + PRGM,
            date,
            self.conf_file,
            test_ifile,
            test_ofile,
            '-log_level',
            'debug'
        ])

        self.assertEqual(resp, 0, 'CHM15K v0.556')

    def test_chm15k_v0559(self):

        date = '20130718'
        test_ifile = self.IN_DIR + '20130718_hohenpeissenberg_CHM060028_000.nc'
        test_ofile = TEST_OUT_DIR + 'test_chm15k_20130718.nc'

        resp = subprocess.check_call([
            MAIN_DIR + PRGM,
            date,
            self.conf_file,
            test_ifile,
            test_ofile,
            '-log_level',
            'debug'
        ])

        self.assertEqual(resp, 0)

    def test_chm15k_v0719(self):

        date = '20131212'
        test_ifile = self.IN_DIR + '20131212_hohenpeissenberg_CHM060028_000.nc'
        test_ofile = TEST_OUT_DIR + 'test_chm15k_20131212.nc'

        resp = subprocess.check_call([
            MAIN_DIR + PRGM,
            date,
            self.conf_file,
            test_ifile,
            test_ofile,
            '-log_level',
            'debug'
        ])

        self.assertEqual(resp, 0, 'test version v0.719')

    def test_chm15k_prob_time(self):

        date = '20120327'
        test_ifile = self.IN_DIR + '20131212_hohenpeissenberg_CHM060028_000.nc'
        test_ofile = TEST_OUT_DIR + 'test_chm15k_20120327_probtime.nc'

        resp = subprocess.check_call([
            MAIN_DIR + PRGM,
            date,
            self.conf_file,
            test_ifile,
            test_ofile,
            '-log_level',
            'debug'
        ])

        self.assertEqual(resp, 0)

    def test_chm15k_sirta(self):

        date = '20150427'
        test_ifile = self.IN_DIR + '20150427_SIRTA_CHM150101_000.nc'
        test_ofile = TEST_OUT_DIR + 'test_chm15k_20150427_sirta.nc'
        test_cfile = CONF_DIR + 'conf_lufft_chm15k-nimbus_toprof.ini'

        resp = subprocess.check_call([
            MAIN_DIR + PRGM,
            date,
            test_cfile,
            test_ifile,
            test_ofile,
            '-log_level',
            'debug',
            '-v',
            'debug'
        ])

        self.assertEqual(resp, 0)

    def test_chm15k_error_msg(self):

        date = '20151001'
        test_ifile = self.IN_DIR + 'ceilometer-eprofile_20151001000023_03963_A201509300000_MaceHead_CHM15K.nc'
        test_ofile = TEST_OUT_DIR + 'test_chm15k_20151001_error_msg.nc'
        test_cfile = CONF_DIR + 'conf_lufft_chm15k-nimbus_toprof.ini'

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
