#!/usr/bin/env python

import argparse
import datetime as dt
import os
import unittest

import raw2l1.tools.arg_parser as ag

MAIN_DIR = os.path.dirname(os.path.dirname(__file__)) + os.sep
TEST_DIR = os.path.join(MAIN_DIR, "tests")


class TestArgParserDate(unittest.TestCase):
    def test_date_error(self):
        self.assertRaises(argparse.ArgumentTypeError, ag.check_date_format, "20150100")

    def test_date_format(self):
        self.assertRaises(
            argparse.ArgumentTypeError, ag.check_date_format, "2015-01-01"
        )

    def test_date_20150301(self):
        self.assertEqual(ag.check_date_format("20150301"), dt.datetime(2015, 3, 1))


class TestArgParser(unittest.TestCase):
    def test_ancillary(self):
        conf_file = os.path.join(TEST_DIR, "conf", "conf_dummy.ini")
        in_pattern = os.path.join(
            TEST_DIR, "input", "rpg_hatpro", "hatpro_0a_z1Imwrad-TPB_v01_*.nc"
        )
        out_file = os.path.join(TEST_DIR, "output", "dummy.nc")

        argv = [
            "20160101",
            conf_file,
            in_pattern,
            out_file,
            "-anc",
            in_pattern,
        ]

        expected_inputs = [
            os.path.join(
                TEST_DIR,
                "input",
                "rpg_hatpro",
                "hatpro_0a_z1Imwrad-TPB_v01_20150901_000412_712.nc",
            ),
            os.path.join(
                TEST_DIR,
                "input",
                "rpg_hatpro",
                "hatpro_0a_z1Imwrad-TPB_v01_20150901_120108_716.nc",
            ),
            os.path.join(
                TEST_DIR,
                "input",
                "rpg_hatpro",
                "hatpro_0a_z1Imwrad-TPB_v01_20150930_000020_1436.nc",
            ),
        ]

        ref_inputs = {
            "date": dt.datetime(2016, 1, 1),
            "conf": open(conf_file),
            "input": expected_inputs,
            "output": os.path.abspath(out_file),
            "ancillary": [expected_inputs],
            "log_level": "info",
            "log": "logs/raw2l1.log",
            "verbose": "info",
            "input_min_size": 0,
            "input_check_time": False,
            "input_max_age": dt.timedelta(hours=2),
            "filter_day": False,
        }

        inputs = ag.get_input_args(argv)

        for key in list(inputs.keys()):
            if key != "conf":
                self.assertEqual(inputs[key], ref_inputs[key])

            # TODO : test conf element
            # conf is not tested because it is a file pointer.
            # don't know how to do it
            print((ref_inputs[key], inputs[key]))


if __name__ == "__main__":
    unittest.main()
