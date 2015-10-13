#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Compatibility with python 3
from __future__ import print_function, division, absolute_import

import os


def check_dir(dir_name):
    """
    Check if a directory exists and is writable
    """

    return os.access(dir_name, os.W_OK)


def chomp(text_list):
    """
    Implement kind of an equivalent of perl chomp function
    """
    return [x.strip() for x in text_list]
