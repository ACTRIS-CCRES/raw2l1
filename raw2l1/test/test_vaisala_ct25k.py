"""Test for VAISALA CT25k ceilometer."""

import subprocess
from pathlib import Path

import pytest

MAIN_DIR = Path(__file__).resolve().parent.parent
TEST_DIR = MAIN_DIR / "test"
TEST_IN_DIR = TEST_DIR / "input" / "vaisala_ct25k"
CONF_DIR = TEST_IN_DIR / "conf"
TEST_OUT_DIR = TEST_DIR / "output"
PRGM = MAIN_DIR / "raw2l1.py"


@pytest.mark.parametrize(
    "date, input_file, conf_file, msg",
    [
        (
            "20220101",
            "vaisala_ct25k_01.DAT",
            "conf_vaisala_ct25k.ini",
            "vaisala CT25k 1 file",
        ),
        (
            "20220101",
            "vaisala_ct25k_*.DAT",
            "conf_vaisala_ct25k.ini",
            "vaisala CT25k 2 files",
        ),
    ],
)
def test_vaisala_cl61(date, input_file, conf_file, msg):
    """
    Test conversion of vaisala CT25k files.

    Parameters
    ----------
    date : str
        Date to process (format YYYYMMDD).
    input_file : str
        Input file name.
    conf_file : str
        Configuration file name.
    msg : str
        Message to display if test fails.

    """
    in_file = TEST_IN_DIR / input_file
    out_file = TEST_OUT_DIR / input_file.replace("*", "").replace(".DAT", ".nc")
    conf_file = CONF_DIR / conf_file

    resp = subprocess.check_call(
        [PRGM, date, conf_file, in_file, out_file, "-log_level", "debug", "-v", "debug"]
    )

    assert resp == 0, f"failed: vaisala CT25k {date}:  {msg}"
