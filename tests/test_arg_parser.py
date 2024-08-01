"""Tests input arguments parsing."""

import argparse
import datetime as dt
import io

import pytest

import raw2l1.tools.arg_parser as ag


def test_args_date_impossible():
    """Test ArgumentTypeError is raised for non-existing date."""
    with pytest.raises(argparse.ArgumentTypeError):
        ag.check_date_format("20150100")


def test_args_date_bad_format():
    """Test ArgumentTypeError is raised for unrecognized format."""
    with pytest.raises(argparse.ArgumentTypeError):
        ag.check_date_format("2015-01-01")


@pytest.mark.parametrize(
    ("date_str", "date_dt"), [("20150301", dt.datetime(2015, 3, 1))]
)
def test_args_date_parse(date_str, date_dt):
    """Test parsing of dates."""
    assert ag.check_date_format(date_str) == date_dt


def test_args_parsing(conf_dir, instr_dir_hatpro, output_dir):
    """Check full parsing of arguments."""
    args = [
        "20160101",
        str(conf_dir / "conf_dummy.ini"),
        str(instr_dir_hatpro / "hatpro_0a_z1Imwrad-TPB_v01_*.nc"),
        str(output_dir / "dummy.nc"),
        "-anc",
        str(instr_dir_hatpro / "hatpro_0a_z1Imwrad-TPB_v01_*.nc"),
    ]

    expected_args = {
        "date": dt.datetime(2016, 1, 1),
        "conf": (conf_dir / "conf_dummy.ini").open(),
        "input": [
            str(instr_dir_hatpro / "hatpro_0a_z1Imwrad-TPB_v01_20150901_000412_712.nc"),
            str(instr_dir_hatpro / "hatpro_0a_z1Imwrad-TPB_v01_20150901_120108_716.nc"),
            str(
                instr_dir_hatpro / "hatpro_0a_z1Imwrad-TPB_v01_20150930_000020_1436.nc"
            ),
        ],
        "output": str(output_dir / "dummy.nc"),
        "ancillary": [
            [
                str(
                    instr_dir_hatpro
                    / "hatpro_0a_z1Imwrad-TPB_v01_20150901_000412_712.nc"
                ),
                str(
                    instr_dir_hatpro
                    / "hatpro_0a_z1Imwrad-TPB_v01_20150901_120108_716.nc"
                ),
                str(
                    instr_dir_hatpro
                    / "hatpro_0a_z1Imwrad-TPB_v01_20150930_000020_1436.nc"
                ),
            ]
        ],
        "log_level": "info",
        "log": "logs/raw2l1.log",
        "verbose": "info",
        "input_min_size": 0,
        "input_check_time": False,
        "input_max_age": dt.timedelta(hours=2),
        "filter_day": False,
    }

    result_args = ag.get_input_args(args)

    for key, val in expected_args.items():
        # TODO: find a way to check io.TextIOWrapper open(conf_dir / "conf_dummy.ini")
        if isinstance(val, io.TextIOWrapper):
            continue

        assert val == result_args[key]
