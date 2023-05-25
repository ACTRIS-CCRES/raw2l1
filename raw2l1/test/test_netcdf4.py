import os
import subprocess
import unittest

MAIN_DIR = os.path.dirname(os.path.dirname(__file__)) + os.sep
TEST_DIR = os.path.join(MAIN_DIR, "test")
CONF_DIR = os.path.join(TEST_DIR, "conf")
TEST_IN_DIR = os.path.join(TEST_DIR, "input")
TEST_OUT_DIR = os.path.join(TEST_DIR, "output")
PRGM = "raw2l1.py"


class TestCampbellScientificCS135NetCDF4(unittest.TestCase):

    IN_DIR = os.path.join(TEST_IN_DIR, "campbell_cs135")
    conf_file = os.path.join(CONF_DIR, "conf_campbell_cs135_eprofile.ini")

    def test_cs135_dummy_file(self):

        date = "20141030"
        test_ifile = os.path.join(self.IN_DIR, "cs135-20150213-message006.txt")
        test_ofile = os.path.join(
            TEST_OUT_DIR,
            "conf_campbell_cs135-cl_eprofile.initest_cs135-nc4_20150213_000000.nc",
        )

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

        self.assertEqual(resp, 0, "CS135 netCDF4")
