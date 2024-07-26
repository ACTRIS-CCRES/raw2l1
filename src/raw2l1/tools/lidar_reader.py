import datetime as dt
import sys
from importlib import import_module

import numpy as np

from raw2l1.tools import common

READER_CONF = "reader_conf"
MISSING_FLOAT_KEY = "missing_float"
MISSING_INT_KEY = "missing_int"


class RawDataReader:
    def __init__(self, conf, logger):
        self.conf = conf
        self.logger = logger
        self.data_reader = conf.get
        self.reader_mod = self.__load_reader__()
        self.reader_conf = self.__get_reader_conf__(logger)
        self.data = {}

    def __load_reader__(self):
        reader_name = self.conf.get("conf", "reader")

        self.logger.info("loading lidar data reader module: " + reader_name)
        try:
            reader_mod = import_module(
                f"raw2l1.reader.{self.conf.get("conf", "reader")}"
            )
        except ImportError as err:
            msg = "107 unable to load lidar data reader "
            self.logger.critical(msg + str(err))
            self.logger.critical("quitting raw2l1")
            sys.exit(1)

        self.logger.info("loading " + reader_name + " : success")

        self.logger.info("loading read_data function from " + reader_name)
        try:
            reader_fcn = reader_mod.read_data
        except AttributeError as err:
            msg = "107 unable find read_data function "
            self.logger.critical(msg + str(err))
            self.logger.critical("quitting raw2l1")
            sys.exit(1)
        self.logger.info("loading read_data function : success")

        return reader_fcn

    def __get_reader_conf__(self, logger):
        """
        Check is configuration contains a [reader_conf] section
        If one is found it is converted into a dictionnary
        """
        reader_conf = {}
        if self.conf.has_section(READER_CONF):
            self.logger.debug("reader_conf section found")
            for key, value in self.conf.items(READER_CONF):
                reader_conf[key] = value

        # add date to process
        reader_conf["date"] = self.conf.get("conf", "date")
        # add list of ancillary files
        reader_conf["ancillary"] = self.conf.get("conf", "ancillary")

        # define missing values if they are not define in reader_conf section
        if MISSING_INT_KEY not in reader_conf:
            logger.info(
                f"""no {MISSING_INT_KEY} option define in {READER_CONF} section.
                        Using default value : {common.MISSING_INTEGER}"""
            )
            reader_conf[MISSING_INT_KEY] = common.MISSING_INTEGER
        else:
            reader_conf[MISSING_INT_KEY] = int(
                self.conf.get(READER_CONF, MISSING_INT_KEY)
            )

        if MISSING_FLOAT_KEY not in reader_conf:
            logger.info(
                f"""no {MISSING_INT_KEY} option define in {READER_CONF} section.
                        Using default value : {common.MISSING_INTEGER}"""
            )
            reader_conf[MISSING_FLOAT_KEY] = common.MISSING_FLOAT
        else:
            reader_conf[MISSING_FLOAT_KEY] = float(
                self.conf.get(READER_CONF, MISSING_FLOAT_KEY)
            )

        return reader_conf

    def timeliness_ok(self, max_age, logger):
        """
        check if data read are not too old or in the future
        assume time variable is called time

        return True if data timeliness is ok
        """
        ERR_MSG = "104 Data timeliness Error"

        now = dt.datetime.now()

        # check if data in the future
        logger.debug("Checking if any data in the future")
        if np.any(self.data["time"] > now):
            logger.warning(ERR_MSG)
            return False

        tmp = now - self.data["time"]
        if np.any(tmp > max_age):
            logger.warning(ERR_MSG)
            return False

        return True

    def read_data(self):
        self.data = self.reader_mod(
            self.conf.get("conf", "input"), self.reader_conf, self.logger
        )
