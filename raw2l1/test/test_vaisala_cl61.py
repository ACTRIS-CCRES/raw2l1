"""Test for VAISALA CL61 ceilometer."""
import subprocess
from pathlib import Path

import pytest

MAIN_DIR = Path(__file__).resolve().parent.parent
TEST_DIR = MAIN_DIR / "test"
TEST_IN_DIR = TEST_DIR / "input" / "vaisala_cl61"
CONF_DIR = TEST_IN_DIR / "conf"
TEST_OUT_DIR = TEST_DIR / "output"
PRGM = MAIN_DIR / "raw2l1.py"


@pytest.mark.parametrize(
    "date, input_file, conf_file",
    [
        ("20210409", "cl61_20210409_090151.nc", "conf_vaisala_cl61_eprofile.ini"),
        ("20210409", "cl61_20211103*.nc", "conf_vaisala_cl61_eprofile.ini"),
        ("20220623", "cl61-v1.1_*.nc", "conf_vaisala_cl61_eprofile.ini"),
        ("20220623", "cl61-v1.1_*.nc", "conf_vaisala_cl61_eprofile_force-loc.ini"),
        ("20220912", "T3250605*.nc", "conf_vaisala_cl61_eprofile.ini"),
    ],
)
def test_vaisala_cl61(date, input_file, conf_file):
    """
    Test conversion of vaisala CL61 files.

    Parameters
    ----------
    date : str
        Date to process (format YYYYMMDD)
    input_file : str
        Input file name
    conf_file : str
        Configuration file name

    """
    in_file = TEST_IN_DIR / input_file
    out_file = TEST_OUT_DIR / input_file.replace("*", "")
    conf_file = CONF_DIR / conf_file

    resp = subprocess.check_call(
        [
            PRGM,
            date,
            conf_file,
            in_file,
            out_file,
            "-log_level",
            "debug",
            "-v",
            "debug",
        ]
    )

    assert resp == 0, "CL61 20210409 single file conversion failed"
