#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Compatibility with python 3


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


def to_bool(s):
    """
    try to convert a string to a boolean if it didn't succeed raise VAlueError
    adaptation of method getboolean of python ConfigParser module
    """

    if s in ("1", "y", "yes", "t", "true", "on"):
        return True
    elif s in ("0", "n", "no", "f", "false", "off"):
        return False
    raise ValueError("Could not convert %s a boolean (use true/false)" % s)
