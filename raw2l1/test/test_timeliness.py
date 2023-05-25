#!/usr/bin/env python

import os
import subprocess
import unittest

from nose.tools import raises

MAIN_DIR = os.path.dirname(os.path.dirname(__file__)) + os.sep
CONF_DIR = MAIN_DIR + "conf" + os.sep
TEST_DIR = MAIN_DIR + "test" + os.sep
TEST_IN_DIR = TEST_DIR + os.sep + "input" + os.sep
TEST_OUT_DIR = TEST_DIR + os.sep + "output" + os.sep
PRGM = "raw2l1.py"


class TestTimeliness(unittest.TestCase):

    IN_DIR = TEST_IN_DIR + "campbell_cs135" + os.sep
    conf_file = CONF_DIR + "conf_campbell_cs135_toprof.ini"

    @raises(subprocess.CalledProcessError)
    def test_too_old_auto(self):

        date = "20141030"
        test_ifile = self.IN_DIR + "cs135-20150213-message006.txt"
        test_ofile = TEST_OUT_DIR + "test_cs135_20150213_000000.nc"

        subprocess.check_call(
            [
                MAIN_DIR + PRGM,
                date,
                self.conf_file,
                test_ifile,
                test_ofile,
                "-log_level",
                "debug",
                "--check_timeliness",
            ]
        )

    @raises(subprocess.CalledProcessError)
    def test_too_old_duration_set(self):

        date = "20141030"
        test_ifile = self.IN_DIR + "cs135-20150213-message006.txt"
        test_ofile = TEST_OUT_DIR + "test_cs135_20150213_000000.nc"

        subprocess.check_call(
            [
                MAIN_DIR + PRGM,
                date,
                self.conf_file,
                test_ifile,
                test_ofile,
                "-log_level",
                "debug",
                "--check_timeliness",
                "-file_max_age",
                "24",
            ]
        )


if __name__ == "__main__":
    unittest.main()
