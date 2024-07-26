import netCDF4 as nc
import numpy as np
import pytest

import raw2l1.reader.lufft_chm15k_nimbus as reader
from raw2l1.raw2l1 import raw2l1


def get_scaling(file):
    """Extract scaling factor from file."""
    nc_file = nc.Dataset(file)
    scaling = nc_file.variables["scaling"][:]
    nc_file.close()

    return scaling


@pytest.mark.parametrize(
    (
        "version",
        "expected_version",
    ),
    [
        (np.int16(235), 0.235),
        ("11.07.1 2.12 0.536", 0.536),
        ("12.12.1 2.13 0.747 0", 0.747),
    ],
)
def test_soft_version_parser(version, expected_version):
    version_value = reader.get_soft_version(version)

    assert version_value == expected_version


# test processing files
@pytest.mark.parametrize(
    (
        "date",
        "chm15k_conf_dir",
        "conf_file",
        "chm15k_input_dir",
        "input_file_chm15k",
        "chm15k_output_dir",
        "tmp_dir",
        "firmware",
    ),
    [
        (
            "20120306",
            "chm15k_conf_dir",
            "conf_lufft_chm15k_eprofile.ini",
            "chm15k_input_dir",
            "20120306_hohenpeissenberg_CHM060028_000.nc",
            "chm15k_output_dir",
            "tmp_dir",
            "v0.536",
        ),
        (
            "20130110",
            "chm15k_conf_dir",
            "conf_lufft_chm15k_eprofile.ini",
            "chm15k_input_dir",
            "20130110_hohenpeissenberg_CHM060028_000.nc",
            "chm15k_output_dir",
            "tmp_dir",
            "v0.536",
        ),
        (
            "20130718",
            "chm15k_conf_dir",
            "conf_lufft_chm15k_eprofile.ini",
            "chm15k_input_dir",
            "20130718_hohenpeissenberg_CHM060028_000.nc",
            "chm15k_output_dir",
            "tmp_dir",
            "v0.559",
        ),
        (
            "20131212",
            "chm15k_conf_dir",
            "conf_lufft_chm15k_eprofile.ini",
            "chm15k_input_dir",
            "20131212_hohenpeissenberg_CHM060028_000.nc",
            "chm15k_output_dir",
            "tmp_dir",
            "v0.719",
        ),
        (
            "20150427",
            "chm15k_conf_dir",
            "conf_lufft_chm15k_eprofile.ini",
            "chm15k_input_dir",
            "20150427_SIRTA_CHM150101_000.nc",
            "chm15k_output_dir",
            "tmp_dir",
            "v0.719",
        ),
        # problem with missing_values attr for some variables
        # It is type as str and create warnings
        (
            "20151001",
            "chm15k_conf_dir",
            "conf_lufft_chm15k_eprofile.ini",
            "chm15k_input_dir",
            "ceilometer-eprofile_20151001000023_03963_A201509300000_MaceHead_CHM15K.nc",
            "chm15k_output_dir",
            "tmp_dir",
            "v0.235",
        ),
        (
            "20160426",
            "chm15k_conf_dir",
            "conf_lufft_chm15k_eprofile.ini",
            "chm15k_input_dir",
            "ceilometer-eprofile_20160426110611_06348_A201604261055_CHM15k.nc",
            "chm15k_output_dir",
            "tmp_dir",
            "v0.738",
        ),
        (
            "20210609",
            "chm15k_conf_dir",
            "conf_lufft_chm15k_eprofile.ini",
            "chm15k_input_dir",
            "chm15k_beta-att.nc",
            "chm15k_output_dir",
            "tmp_dir",
            "v1.100",
        ),
    ],
    indirect=[
        "chm15k_conf_dir",
        "chm15k_input_dir",
        "chm15k_output_dir",
        "tmp_dir",
    ],  # variables in fixtures
)
def test_conversion(
    date,
    chm15k_conf_dir,
    conf_file,
    chm15k_input_dir,
    input_file_chm15k,
    chm15k_output_dir,
    tmp_dir,
    firmware,
):
    conf_file = open(chm15k_conf_dir / conf_file)  # noqa: SIM115 PTH123
    input_file = str(chm15k_input_dir / input_file_chm15k)
    output_file = str(chm15k_output_dir / input_file_chm15k)
    log_file = str(tmp_dir / "raw2l1.log")

    ret_code = raw2l1(
        date, conf_file, [input_file], output_file, verbose="debug", log_file=log_file
    )

    assert ret_code == 0, f"Conversion failed for file {input_file} {firmware}"


# test processing files
@pytest.mark.parametrize(
    (
        "date",
        "chm15k_conf_dir",
        "conf_file",
        "chm15k_input_dir",
        "input_file_chm15k",
        "overlap_file",
        "overlap_in_conf",
        "chm15k_output_dir",
        "output_file_chm15k",
        "tmp_dir",
        "expected_ret_code",
        "test_msg",
    ),
    [
        # overlap ile provided with `and` option
        (
            "20120306",
            "conf_dir",
            "conf_lufft_chm15k_eprofile.ini",
            "chm15k_input_dir",
            "20150427_SIRTA_CHM150101_000.nc",
            "TUB140013_20150211_4096.cfg",
            False,
            "chm15k_output_dir",
            "chm15k_ovl-as-arg.nc",
            "tmp_dir",
            0,
            "good overlap as argument",
        ),
        # overlap file defined in conf file
        (
            "20150427_SIRTA_CHM150101_000.nc",
            "chm15k_conf_dir",
            "conf_lufft_chm15k_eprofile.ini",
            "chm15k_input_dir",
            "20150427_SIRTA_CHM150101_000.nc",
            "",
            True,
            "chm15k_output_dir",
            "chm15k_ovl-in-conf.nc",
            "tmp_dir",
            0,
            "good overlap in conf",
        ),
    ],
    indirect=[
        "chm15k_conf_dir",
        "chm15k_input_dir",
        "chm15k_output_dir",
        "tmp_dir",
    ],  # variables in fixtures
)
def test_overlap(
    date,
    chm15k_conf_dir,
    conf_file,
    chm15k_input_dir,
    input_file_chm15k,
    overlap_file,
    overlap_in_conf,
    chm15k_output_dir,
    output_file_chm15k,
    tmp_dir,
    expected_ret_code,
    test_msg,
):
    conf_file = open(chm15k_conf_dir / conf_file)  # noqa: SIM115 PTH123
    input_file = str(chm15k_input_dir / input_file_chm15k)
    ovl_file = [[str(chm15k_input_dir / overlap_file)]]
    output_file = str(chm15k_output_dir / output_file_chm15k)
    log_file = str(tmp_dir / "raw2l1.log")

    raw2l1_args = [date, conf_file, [input_file], output_file]
    raw2l1_kwargs = {
        "verbose": "debug",
        "log_file": log_file,
    }
    if not overlap_in_conf:
        raw2l1_kwargs["ancillary"] = ovl_file

    ret_code = raw2l1(*raw2l1_args, **raw2l1_kwargs)

    assert ret_code == expected_ret_code, f"{test_msg} failed"


# class TestChm15kOverlap(unittest.TestCase):
#     IN_DIR = os.path.join(TEST_IN_DIR, "jenoptik_chm15k")
#     conf_file = os.path.join(CONF_DIR, "conf_lufft_chm15k_eprofile.ini")

#     def test_chm15k_overlap_good(self):
#         date = "20150427"
#         test_ifile = os.path.join(self.IN_DIR, "20150427_SIRTA_CHM150101_000.nc")
#         test_ovl_file = os.path.join(self.IN_DIR, "TUB140013_20150211_4096.cfg")
#         test_ofile = os.path.join(
#             TEST_OUT_DIR, "test_chm15k_20150427_sirta_good-ovl.nc"
#         )
#         test_cfile = os.path.join(CONF_DIR, "conf_lufft_chm15k_eprofile.ini")

#         resp = subprocess.check_call(
#             [
#                 MAIN_DIR + PRGM,
#                 date,
#                 test_cfile,
#                 test_ifile,
#                 test_ofile,
#                 "-anc",
#                 test_ovl_file,
#                 "-log_level",
#                 "debug",
#                 "-v",
#                 "debug",
#             ]
#         )

#         self.assertEqual(resp, 0, "reading overlap")

#     def test_chm15k_overlap_good_conf(self):
#         """
#         test that the reading of overlap TUB file defined in conf file goes well
#         """

#         date = "20150427"
#         test_ifile = os.path.join(self.IN_DIR, "20150427_SIRTA_CHM150101_000.nc")
#         test_ofile = os.path.join(
#             TEST_OUT_DIR, "test_chm15k_20150427_sirta_good-ovl-conf-file.nc"
#         )
#         test_cfile = os.path.join(CONF_DIR, "conf_lufft_chm15k_eprofile.ini")

#         resp = subprocess.check_call(
#             [
#                 MAIN_DIR + PRGM,
#                 date,
#                 test_cfile,
#                 test_ifile,
#                 test_ofile,
#                 "-log_level",
#                 "debug",
#                 "-v",
#                 "debug",
#             ]
#         )

#         self.assertEqual(resp, 0, "reading overlap define conf file")

#     def test_chm15k_overlap_bad(self):
#         date = "20150427"
#         test_ifile = os.path.join(self.IN_DIR, "20150427_SIRTA_CHM150101_000.nc")
#         test_ovl_file = os.path.join(self.IN_DIR, "jenoptik_chm15k_overlap.txt")
#         test_ofile = os.path.join(TEST_OUT_DIR, "test_chm15k_20150427_sirta_bad-ovl.nc")
#         test_cfile = os.path.join(CONF_DIR, "conf_lufft_chm15k_eprofile.ini")

#         resp = subprocess.check_call(
#             [
#                 MAIN_DIR + PRGM,
#                 date,
#                 test_cfile,
#                 test_ifile,
#                 test_ofile,
#                 "-anc",
#                 test_ovl_file,
#                 "-log_level",
#                 "debug",
#                 "-v",
#                 "debug",
#             ]
#         )

#         self.assertEqual(resp, 0, "bad overlap file but readable")

#     def test_chm15k_overlap_empty(self):
#         date = "20150427"
#         test_ifile = os.path.join(self.IN_DIR, "20150427_SIRTA_CHM150101_000.nc")
#         test_ovl_file = os.path.join(self.IN_DIR, "empty_overlap.txt")
#         test_ofile = os.path.join(
#             TEST_OUT_DIR, "test_chm15k_20150427_sirta_empty-ovl.nc"
#         )
#         test_cfile = os.path.join(CONF_DIR, "conf_lufft_chm15k_eprofile.ini")

#         resp = subprocess.check_call(
#             [
#                 MAIN_DIR + PRGM,
#                 date,
#                 test_cfile,
#                 test_ifile,
#                 test_ofile,
#                 "-anc",
#                 test_ovl_file,
#                 "-log_level",
#                 "debug",
#                 "-v",
#                 "debug",
#             ]
#         )

#         self.assertEqual(resp, 0, "bad overlap file but readable")

#     def test_cho_substraction(self):
#         """test that the cho value is substracted from cbh"""

#         missing_cbh_prod = -9
#         missing_cbh_orig = -1

#         date = "20161113"
#         test_ifile = os.path.join(
#             self.IN_DIR,
#             "ceilometer-eprofile_20161113193414_06610_A201611131920_CHM15k.nc",
#         )
#         test_ofile = os.path.join(TEST_OUT_DIR, "validation_cho.nc")
#         test_cfile = os.path.join(CONF_DIR, "conf_lufft_chm15k_eprofile.ini")

#         # create file using raw2l1
#         subprocess.check_call(
#             [
#                 MAIN_DIR + PRGM,
#                 date,
#                 test_cfile,
#                 test_ifile,
#                 test_ofile,
#                 "-log_level",
#                 "debug",
#                 "-v",
#                 "debug",
#             ]
#         )

#         # read cbh from created file
#         nc_prod = nc.Dataset(test_ofile)
#         cbh_prod = nc_prod.variables["cloud_base_height"][:]
#         cbh_prod = np.ma.filled(cbh_prod)
#         cbh_prod = cbh_prod.astype(int)
#         nc_prod.close()

#         # read cbh from original file
#         nc_orig = nc.Dataset(test_ifile)
#         cbh_orig = nc_orig.variables["cbh"][:]
#         cho_orig = nc_orig.variables["cho"][:]
#         cbh_orig[cbh_orig != missing_cbh_orig] = (
#             cbh_orig[cbh_orig != missing_cbh_orig] - cho_orig
#         )
#         cbh_orig[cbh_orig == missing_cbh_orig] = missing_cbh_prod

#         self.assertEqual(cbh_orig.tolist(), cbh_prod.tolist(), "")


# if __name__ == "__main__":
#     unittest.main()
