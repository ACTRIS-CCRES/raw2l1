import configparser
import datetime as dt
import io
import logging


def add(conf, input_args, version, logger):
    """Allow to add parameters in conf section of conf object."""
    # Warning: for configuration file, we do not use the filename but the
    # filehandler
    #   to access filename use, conf_file.name
    for key, value in list(input_args.items()):
        logger.debug("adding %s : %s to conf", key, value)
        conf.set("conf", key, value)

    # add version in conf
    conf.set("conf", "version", version)

    return conf


def init(
    date: dt.datetime,
    conf_file: io.TextIOWrapper,
    input_files: list[str],
    output_file: str,
    ancillary: list[str],
    file_min_size: int,
    check_timeliness: bool,
    file_max_age: int,
    filter_day: bool,
    log_file: str,
    log_file_level: str,
    verbose: str,
    version: str,
    logger: logging.Logger,
):
    """Load and check the INI configuration file."""
    conf = configparser.RawConfigParser()
    conf.optionxform = str
    conf.read(conf_file.name)

    # TODO: Add a function to check available values once format is fixed

    # add user input arguments to conf object
    logger.debug("adding user entered options to configuration")
    conf.set("conf", "date", date)
    conf.set("conf", "conf", conf_file)
    conf.set("conf", "input", input_files)
    conf.set("conf", "output", output_file)
    conf.set("conf", "ancillary", ancillary)
    conf.set("conf", "input_min_size", file_min_size)
    conf.set("conf", "input_check_time", check_timeliness)
    conf.set("conf", "input_max_age", file_max_age)
    conf.set("conf", "filter_day", filter_day)
    conf.set("conf", "log", log_file)
    conf.set("conf", "log_level", log_file_level)
    conf.set("conf", "verbose", verbose)
    conf.set("conf", "version", version)

    # if in debug mode log all configuration
    if logger.getEffectiveLevel() == logging.DEBUG:
        logger.debug("raw2l1 configuration")
        for section in conf.sections():
            for key, value in conf.items(section):
                logger.debug("[%s] %s : %s", section, key, repr(value))
        logger.debug("end of configuration")

    return conf
