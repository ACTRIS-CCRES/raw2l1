import os
import subprocess
import unittest

MAIN_DIR = os.path.dirname(os.path.dirname(__file__))
TEST_DIR = os.path.join(MAIN_DIR, "test")
CONF_DIR = os.path.join(TEST_DIR, "conf")
TEST_IN_DIR = os.path.join(TEST_DIR, "input")
TEST_OUT_DIR = os.path.join(TEST_DIR, "output")
PRGM = "raw2l1.py"


class TestVaisalaCL31MissingCBE(unittest.TestCase):
    IN_DIR = os.path.join(TEST_IN_DIR, "vaisala_cl", "eprofile")
    conf_file = os.path.join(CONF_DIR, "conf_vaisala_cl31_eprofile.ini")

    def test_20160523005942_c6052300(self):
        date = "20160523"
        test_ifile = os.path.join(self.IN_DIR, "ceilometer_20160523005942_c6052300.DAT")
        test_ofile = os.path.join(TEST_OUT_DIR, "ceilometer_20160523005942_c6052300.nc")

        resp = subprocess.check_call(
            [
                os.path.join(MAIN_DIR, PRGM),
                date,
                self.conf_file,
                test_ifile,
                test_ofile,
                "-log_level",
                "debug",
            ]
        )

        self.assertEqual(resp, 0, "CL31 missing CBE c6052300")

    def test_20160523010011_P6052300(self):
        date = "20160523"
        test_ifile = os.path.join(self.IN_DIR, "ceilometer_20160523010011_P6052300.DAT")
        test_ofile = os.path.join(TEST_OUT_DIR, "ceilometer_20160523010011_P6052300.nc")

        resp = subprocess.check_call(
            [
                os.path.join(MAIN_DIR, PRGM),
                date,
                self.conf_file,
                test_ifile,
                test_ofile,
                "-log_level",
                "debug",
            ]
        )

        self.assertEqual(resp, 0, "CL31 missing CBE ceilometer P6052300")

    def test_20160523010012_Q6052300(self):
        date = "20160523"
        test_ifile = os.path.join(self.IN_DIR, "ceilometer_20160523010012_Q6052300.DAT")
        test_ofile = os.path.join(TEST_OUT_DIR, "ceilometer_20160523010012_Q6052300.nc")

        resp = subprocess.check_call(
            [
                os.path.join(MAIN_DIR, PRGM),
                date,
                self.conf_file,
                test_ifile,
                test_ofile,
                "-log_level",
                "debug",
            ]
        )

        self.assertEqual(resp, 0, "CL31 missing CBE ceilometer Q6052300")

    def test_20160523010012_T6052300(self):
        date = "20160523"
        test_ifile = os.path.join(self.IN_DIR, "ceilometer_20160523010012_T6052300.DAT")
        test_ofile = os.path.join(TEST_OUT_DIR, "ceilometer_20160523010012_T6052300.nc")

        resp = subprocess.check_call(
            [
                os.path.join(MAIN_DIR, PRGM),
                date,
                self.conf_file,
                test_ifile,
                test_ofile,
                "-log_level",
                "debug",
            ]
        )

        self.assertEqual(resp, 0, "CL31 missing CBE ceilometer T6052300")

    def test_20160523100012_P6052309(self):
        date = "20160523"
        test_ifile = os.path.join(self.IN_DIR, "ceilometer_20160523100012_P6052309.DAT")
        test_ofile = os.path.join(TEST_OUT_DIR, "ceilometer_20160523100012_P6052309.nc")

        resp = subprocess.check_call(
            [
                os.path.join(MAIN_DIR, PRGM),
                date,
                self.conf_file,
                test_ifile,
                test_ofile,
                "-log_level",
                "debug",
            ]
        )

        self.assertEqual(resp, 0, "CL31 missing CBE ceilometer P6052309")


class TestVaisalaCL51MissingCBE(unittest.TestCase):
    IN_DIR = os.path.join(TEST_IN_DIR, "vaisala_cl", "eprofile")
    conf_file = os.path.join(CONF_DIR, "conf_vaisala_cl51_eprofile.ini")

    def test_20160523160107_06472_A201605231500(self):
        date = "20160523"
        test_ifile = os.path.join(
            self.IN_DIR,
            "ceilometer-eprofile_20160523160107_06472_A201605231500_cl51.dat",
        )
        test_ofile = os.path.join(
            TEST_OUT_DIR,
            "ceilometer-eprofile_20160523160107_06472_A201605231500_cl51.nc",
        )

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

        self.assertEqual(resp, 0, "CL51 missing CBE ceilometer ")


class TestVaisalaCL31EmptyFile(unittest.TestCase):
    IN_DIR = os.path.join(TEST_IN_DIR, "vaisala_cl", "eprofile")
    conf_file = os.path.join(CONF_DIR, "conf_vaisala_cl31_eprofile.ini")

    def test_20160427230032_h6042722(self):
        date = "20160427"
        test_ifile = os.path.join(self.IN_DIR, "ceilometer_20160427230032_h6042722.DAT")
        test_ofile = os.path.join(TEST_OUT_DIR, "ceilometer_20160427230032_h6042722.nc")

        resp = subprocess.call(
            [
                os.path.join(MAIN_DIR, PRGM),
                date,
                self.conf_file,
                test_ifile,
                test_ofile,
                "-log_level",
                "debug",
            ]
        )

        self.assertEqual(resp, 1, "CL31 empty log file h6042722")

    def test_20160428200020_h6042819(self):
        date = "20160428"
        test_ifile = os.path.join(self.IN_DIR, "ceilometer_20160428200020_h6042819.DAT")
        test_ofile = os.path.join(TEST_OUT_DIR, "ceilometer_20160428200020_h6042819.nc")

        resp = subprocess.call(
            [
                os.path.join(MAIN_DIR, PRGM),
                date,
                self.conf_file,
                test_ifile,
                test_ofile,
                "-log_level",
                "debug",
            ]
        )

        self.assertEqual(resp, 1, "CL31 empty log file h6042819")


class TestVaisalaCL51EmptyFile(unittest.TestCase):
    IN_DIR = os.path.join(TEST_IN_DIR, "vaisala_cl", "eprofile")
    conf_file = os.path.join(CONF_DIR, "conf_vaisala_cl51_eprofile.ini")

    def test_20160517070311_06447_A201605170600(self):
        date = "20160517"
        test_ifile = os.path.join(
            self.IN_DIR,
            "ceilometer-eprofile_20160517070311_06447_A201605170600_cl51.dat",
        )
        test_ofile = os.path.join(
            TEST_OUT_DIR,
            "ceilometer-eprofile_20160517070311_06447_A201605170600_cl51.nc",
        )

        resp = subprocess.call(
            [
                os.path.join(MAIN_DIR, PRGM),
                date,
                self.conf_file,
                test_ifile,
                test_ofile,
                "-log_level",
                "debug",
            ]
        )

        self.assertEqual(resp, 1, "CL51 empty log file")


class TestVaisalaCL51IncompleteFile(unittest.TestCase):
    IN_DIR = os.path.join(TEST_IN_DIR, "vaisala_cl", "eprofile")
    conf_file = os.path.join(CONF_DIR, "conf_vaisala_cl51_eprofile.ini")

    def test_20160517120306_06447_A201605171100(self):
        date = "20160517"
        test_ifile = os.path.join(
            self.IN_DIR,
            "ceilometer-eprofile_20160517120306_06447_A201605171100_cl51.dat",
        )
        test_ofile = os.path.join(
            TEST_OUT_DIR,
            "ceilometer-eprofile_20160517120306_06447_A201605171100_cl51.nc",
        )

        resp = subprocess.call(
            [
                os.path.join(MAIN_DIR, PRGM),
                date,
                self.conf_file,
                test_ifile,
                test_ofile,
                "-log_level",
                "debug",
            ]
        )

        self.assertEqual(
            resp, 0, "CL51 empty log file 20160517120306_06447_A201605171100"
        )

    def test_20160426210111_06418_A201604262000(self):
        date = "20160426"
        test_ifile = os.path.join(
            self.IN_DIR,
            "ceilometer-eprofile_20160426210111_06418_A201604262000_cl51.dat",
        )
        test_ofile = os.path.join(
            TEST_OUT_DIR,
            "ceilometer-eprofile_20160426210111_06418_A201604262000_cl51.nc",
        )

        resp = subprocess.call(
            [
                os.path.join(MAIN_DIR, PRGM),
                date,
                self.conf_file,
                test_ifile,
                test_ofile,
                "-log_level",
                "debug",
            ]
        )

        self.assertEqual(
            resp, 0, "CL51 empty log file 20160426210111_06418_A201604262000"
        )
