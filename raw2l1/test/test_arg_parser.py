#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import argparse
import datetime as dt
import tools.arg_parser as ag


class TestArgParser(unittest.TestCase):

    def test_date_error(self):

        self.assertRaises(
            argparse.ArgumentTypeError,
            ag.check_date_format,
            "20150100"
        )

    def test_date_format(self):

        self.assertRaises(
            argparse.ArgumentTypeError,
            ag.check_date_format,
            "2015-01-01"
        )

    def test_date_20150301(self):

        self.assertEqual(
            ag.check_date_format("20150301"),
            dt.datetime(2015, 3, 1)
        )

if __name__ == '__main__':
    unittest.main()
