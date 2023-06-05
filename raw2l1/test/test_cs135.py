import os
import subprocess
import unittest

MAIN_DIR = os.path.dirname(os.path.dirname(__file__)) + os.sep
TEST_DIR = os.path.join(MAIN_DIR, "test")
CONF_DIR = os.path.join(TEST_DIR, "conf")
TEST_IN_DIR = os.path.join(TEST_DIR, "input")
TEST_OUT_DIR = os.path.join(TEST_DIR, "output")
PRGM = "raw2l1.py"


class TestCampbellScientificCS135(unittest.TestCase):
    """Test for CS135 data in campbell Scientific format"""

    IN_DIR = os.path.join(TEST_IN_DIR, "campbell_cs135")
    conf_file = os.path.join(CONF_DIR, "conf_campbell_cs135_eprofile.ini")

    def test_cs135_dummy_file(self):
        date = "20141030"
        test_ifile = os.path.join(self.IN_DIR, "cs135-20150213-message006.txt")
        test_ofile = os.path.join(TEST_OUT_DIR, "test_cs135_20150213_000000.nc")

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

        self.assertEqual(resp, 0, "CS135 ")


class TestCampbellScientificCS135ModeCL31(unittest.TestCase):
    """Test for CS135 data in vaisala format"""

    IN_DIR = os.path.join(TEST_IN_DIR, "campbell_cs135")
    conf_file = os.path.join(CONF_DIR, "conf_campbell_cs135-cl_eprofile.ini")

    def test_cs135_dummy_file(self):
        date = "20150703"
        test_ifile = os.path.join(self.IN_DIR, "15070300.DAT")
        test_ofile = os.path.join(TEST_OUT_DIR, "test_cs135_20150703_000000.nc")

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
                "error",
            ]
        )

        self.assertEqual(resp, 0, "CS135 ")


if __name__ == "__main__":
    unittest.main()
