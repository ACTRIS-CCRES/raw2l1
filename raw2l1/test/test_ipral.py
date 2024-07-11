#!/usr/bin/env python

import os
import subprocess
import unittest

MAIN_DIR = os.path.dirname(os.path.dirname(__file__)) + os.sep
CONF_DIR = os.path.join(MAIN_DIR, "conf")
TEST_DIR = os.path.join(MAIN_DIR, "test")
TEST_IN_DIR = os.path.join(TEST_DIR, "input", "sirta_ipral")
TEST_OUT_DIR = os.path.join(TEST_DIR, "output")
PRGM = "raw2l1.py"


class TestRunIpral(unittest.TestCase):
    """test run of SIRTA IPRAL reader"""

    IN_DIR = os.path.join(TEST_IN_DIR, "data")
    conf_file = os.path.join(TEST_IN_DIR, "conf", "conf_ipral_test_00.ini")

    def test_run_ipral_one_file(self):
        """test ipral reader with one file"""

        date = "20170621"
        test_ifile = os.path.join(self.IN_DIR, "RM1762107.030037")
        test_ofile = os.path.join(TEST_OUT_DIR, "test_ipral_one_file.nc")

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

        self.assertEqual(resp, 0, "run IPRAL one file")

    def test_run_ipral_several_files(self):
        """test ipral reader with several files"""

        date = "20170621"
        test_ifile = os.path.join(self.IN_DIR, "RM17621*")
        test_ofile = os.path.join(TEST_OUT_DIR, "test_ipral_several_files.nc")

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
                "info",
            ]
        )

        self.assertEqual(resp, 0, "run IPRAL several files")


if __name__ == "__main__":
    unittest.main()
