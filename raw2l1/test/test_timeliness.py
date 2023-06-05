#!/usr/bin/env python

import os
import subprocess
import unittest

MAIN_DIR = os.path.dirname(os.path.dirname(__file__)) + os.sep
TEST_DIR = os.path.join(MAIN_DIR, "test")
CONF_DIR = os.path.join(TEST_DIR, "conf")
TEST_IN_DIR = os.path.join(TEST_DIR, "input")
TEST_OUT_DIR = os.path.join(TEST_DIR, "output")
PRGM = "raw2l1.py"


class TestTimeliness(unittest.TestCase):
    IN_DIR = os.path.join(TEST_IN_DIR, "campbell_cs135")
    conf_file = os.path.join(CONF_DIR, "conf_campbell_cs135_eprofile.ini")

    def test_too_old_auto(self):
        date = "20141030"
        test_ifile = os.path.join(self.IN_DIR, "cs135-20150213-message006.txt")
        test_ofile = os.path.join(TEST_OUT_DIR, "test_cs135_20150213_000000.nc")

        resp = subprocess.call(
            [
                os.path.join(MAIN_DIR, PRGM),
                date,
                self.conf_file,
                test_ifile,
                test_ofile,
                "-log_level",
                "debug",
                "--check_timeliness",
            ]
        )

        self.assertEqual(resp, 1, "timeliness too old auto")

    def test_too_old_duration_set(self):
        date = "20141030"
        test_ifile = os.path.join(self.IN_DIR, "cs135-20150213-message006.txt")
        test_ofile = os.path.join(TEST_OUT_DIR, "test_cs135_20150213_000000.nc")

        resp = subprocess.call(
            [
                os.path.join(MAIN_DIR, PRGM),
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

        self.assertEqual(resp, 1, "timeliness too old duration set")


if __name__ == "__main__":
    unittest.main()
