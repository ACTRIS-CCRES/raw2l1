import os
import subprocess
import unittest

MAIN_DIR = os.path.dirname(os.path.dirname(__file__))
CONF_DIR = os.path.join(MAIN_DIR, "conf")
TEST_DIR = os.path.join(MAIN_DIR, "test")
TEST_IN_DIR = os.path.join(TEST_DIR, "input")
TEST_OUT_DIR = os.path.join(TEST_DIR, "output")
PRGM = "raw2l1.py"


class TestVaisalaBugSIRTA(unittest.TestCase):

    IN_DIR = os.path.join(TEST_IN_DIR, "vaisala_cl31")
    conf_file = os.path.join(CONF_DIR, "conf_vaisala_cl31_eprofile.ini")

    def test_20150911(self):

        date = "20150911"
        test_ifile = os.path.join(self.IN_DIR, "cl31_0a_z1R5mF3s_v02_20150911_*.asc")
        test_ofile = os.path.join(TEST_OUT_DIR, "test_cl-sirta_20150911.nc")

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

        self.assertEqual(resp, 0, "CL SIRTA bug message type")

    def test_20150603(self):

        date = "20150603"
        test_ifile = os.path.join(self.IN_DIR, "cl31_0a_z1R5mF3s_v02_20150603_*.asc")
        test_ofile = os.path.join(TEST_OUT_DIR, "test_cl-sirta_20150521.nc")

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

        self.assertEqual(resp, 0, "CL SIRTA bug message type")

    def test_bad_alarm(self):

        date = "20200831"
        test_ifile = os.path.join(
            self.IN_DIR, "cl31_0a_z1R10mF30s_v01_20200831_000009_1440.asc"
        )
        test_ofile = os.path.join(TEST_OUT_DIR, "test_cl-sirta_20200831.nc")

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

        self.assertEqual(resp, 0, "CL SIRTA bug alarm msg")

    def test_corrupted_mf(self):

        date = "20200721"
        test_ifile = os.path.join(self.IN_DIR, "07157_A202007210103_CL31-Roissy.dat")
        test_ofile = os.path.join(TEST_OUT_DIR, "test_cl-sirta_20200721.nc")

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

        self.assertEqual(resp, 0, "CL SIRTA corrupted message")

    def test_error_bck_mf(self):

        date = "20200830"
        test_ifile = os.path.join(self.IN_DIR, "07157_A202008300054_CL31-Roissy.dat")
        test_ofile = os.path.join(TEST_OUT_DIR, "test_cl-roissy_20200830.nc")

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

        self.assertEqual(resp, 0, "CL roissy corrupted bck")


if __name__ == "__main__":
    unittest.main()
