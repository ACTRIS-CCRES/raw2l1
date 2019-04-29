#!/usr/bin/env python
# -*- encoding: utf-8 -*-


def abc(data):

    data[2] = 2
    data[3] = 3

    return data


def read_data(list_files, logger):

    logger.info("test_reader")
    logger.info(list_files)

    data = {}
    data["a"] = 0
    data["b"] = 1

    data = abc(data)

    return data
