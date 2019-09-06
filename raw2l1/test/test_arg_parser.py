#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

import os
import argparse
import datetime as dt

import tools.arg_parser as ag


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

        argv = [
            "20160101",
            "test/conf/conf_dummy.ini",
            "test/input/rpg_hatpro/hatpro_0a_z1Imwrad-TPB_v01_*.nc",
            "test/output/dummy.nc",
            "-anc",
            "test/input/rpg_hatpro/hatpro_0a_z1Imwrad-TPB_v01_*.nc",
        ]

        ref_inputs = {
            "date": dt.datetime(2016, 1, 1),
            "conf": open("test/conf/conf_dummy.ini", "r"),
            "input": [
                "test/input/rpg_hatpro/hatpro_0a_z1Imwrad-TPB_v01_20150901_000412_712.nc",
                "test/input/rpg_hatpro/hatpro_0a_z1Imwrad-TPB_v01_20150901_120108_716.nc",
                "test/input/rpg_hatpro/hatpro_0a_z1Imwrad-TPB_v01_20150930_000020_1436.nc",
            ],
            "output": os.path.abspath("test/output/dummy.nc"),
            "ancillary": [
                [
                    "test/input/rpg_hatpro/hatpro_0a_z1Imwrad-TPB_v01_20150901_000412_712.nc",
                    "test/input/rpg_hatpro/hatpro_0a_z1Imwrad-TPB_v01_20150901_120108_716.nc",
                    "test/input/rpg_hatpro/hatpro_0a_z1Imwrad-TPB_v01_20150930_000020_1436.nc",
                ]
            ],
            "log_level": "info",
            "log": "logs/raw2l1.log",
            "verbose": "info",
            "input_min_size": 0,
            "input_check_time": False,
            "input_max_age": dt.timedelta(hours=2),
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
