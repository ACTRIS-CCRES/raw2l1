#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import subprocess
import os

MAIN_DIR = os.path.dirname(os.path.dirname(__file__)) + os.sep
CONF_DIR = os.path.join(MAIN_DIR, 'conf')
TEST_DIR = os.path.join(MAIN_DIR, 'test')
TEST_IN_DIR = os.path.join(TEST_DIR, 'input')
TEST_OUT_DIR = os.path.join(TEST_DIR, 'output')
PRGM = "raw2l1.py"


class TestChm15k(unittest.TestCase):

    IN_DIR = os.path.join(TEST_IN_DIR, 'jenoptik_chm15k')
    conf_file = os.path.join(CONF_DIR, 'conf_lufft_chm15k-nimbus_eprofile.ini')

    def test_chm15k_v0536(self):

        date = '20120306'
        test_ifile = os.path.join(self.IN_DIR, '20120306_hohenpeissenberg_CHM060028_000.nc')
        test_ofile = os.path.join(TEST_OUT_DIR, 'test_chm15k_v0536_20120306.nc')

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
        test_ifile = os.path.join(self.IN_DIR, '20130110_hohenpeissenberg_CHM060028_000.nc')
        test_ofile = os.path.join(TEST_OUT_DIR, 'test_chm15k_v0556_20130110.nc')

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
        test_ifile = os.path.join(self.IN_DIR, '20130718_hohenpeissenberg_CHM060028_000.nc')
        test_ofile = os.path.join(TEST_OUT_DIR, 'test_chm15k_v0559_20130718.nc')

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
        test_ifile = os.path.join(self.IN_DIR, '20131212_hohenpeissenberg_CHM060028_000.nc')
        test_ofile = os.path.join(TEST_OUT_DIR, 'test_chm15k_v0719_20131212.nc')

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
        test_ifile = os.path.join(self.IN_DIR, '20131212_hohenpeissenberg_CHM060028_000.nc')
        test_ofile = os.path.join(TEST_OUT_DIR, 'test_chm15k_20120327_probtime.nc')

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
        test_ifile = os.path.join(self.IN_DIR, '20150427_SIRTA_CHM150101_000.nc')
        test_ofile = os.path.join(TEST_OUT_DIR, 'test_chm15k_20150427_sirta.nc')
        test_cfile = os.path.join(CONF_DIR, 'conf_lufft_chm15k-nimbus_eprofile.ini')

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

    def test_chm15k_v0235(self):

        date = '20151001'
        test_ifile = os.path.join(self.IN_DIR,
                                  'ceilometer-eprofile_20151001000023_03963_A201509300000_MaceHead_CHM15K.nc')
        test_ofile = os.path.join(TEST_OUT_DIR, 'test_chm15k_v0235_20151001.nc')
        test_cfile = os.path.join(CONF_DIR, 'conf_lufft_chm15k-nimbus_eprofile.ini')

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

    def test_chm15k_v0738(self):

        date = '20160426'
        test_ifile = os.path.join(
            self.IN_DIR,
            'eprofile',
            'ceilometer-eprofile_20160426110611_06348_A201604261055_CHM15k.nc')
        test_ofile = os.path.join(
            TEST_OUT_DIR,
            'eprofile_20160426110611_06348_A201604261055_CHM15k.nc')
        test_cfile = os.path.join(
            CONF_DIR,
            'conf_lufft_chm15k-nimbus_eprofile.ini')

        resp = subprocess.call([
            MAIN_DIR + PRGM,
            date,
            test_cfile,
            test_ifile,
            test_ofile,
            '-log_level',
            'debug'
        ])

        self.assertEqual(resp, 0, 'Nimbus v0.738')


if __name__ == '__main__':
    unittest.main()
