import unittest
import subprocess
import os

MAIN_DIR = os.path.dirname(os.path.dirname(__file__))
TEST_DIR = os.path.join(MAIN_DIR, "test")
CONF_DIR = os.path.join(TEST_DIR, "conf")
TEST_IN_DIR = os.path.join(TEST_DIR, "input")
TEST_OUT_DIR = os.path.join(TEST_DIR, "output")
PRGM = "raw2l1.py"


class TestSigmaSpaceMiniMPL(unittest.TestCase):

    IN_DIR = os.path.join(TEST_IN_DIR, "sigmaspace_minimpl")
    conf_file = os.path.join(CONF_DIR, "conf_sigmaspace_minimpl_eprofile.ini")

    def test_5min_file(self):

        date = "20160601"
        test_ifile = os.path.join(self.IN_DIR, "MPL_5030_201606010000.nc")
        test_ofile = os.path.join(TEST_OUT_DIR, "test_minimpl_20160601_5min.nc")

        resp = subprocess.check_call(
            [
                os.path.join(MAIN_DIR, PRGM),
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

        self.assertEqual(resp, 0, "miniMPL one file")

    def test_1h_file(self):

        date = "20160601"
        test_ifile = os.path.join(self.IN_DIR, "MPL_5030_20160601*.nc")
        test_ofile = os.path.join(TEST_OUT_DIR, "test_minimpl_20160601_1h.nc")

        resp = subprocess.check_call(
            [
                os.path.join(MAIN_DIR, PRGM),
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

        self.assertEqual(resp, 0, "miniMPL 1h")


if __name__ == "__main__":
    unittest.main()
