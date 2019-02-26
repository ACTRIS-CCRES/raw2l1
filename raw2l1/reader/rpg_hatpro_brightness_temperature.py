# -*- coding: utf8 -*-


import numpy as np
import datetime as dt
import netCDF4 as nc

from .libhatpro import correct_time_units

# brand and model of the LIDAR
BRAND = "RPG"
MODEL = "HATPRO boundary layer temperature"

TIME_DIM = "time"
TIME_VAR = "time"


FLT_MISSING_VALUE = -999.0
INT_MISSING_VALUE = -9


def get_data_size(list_files, logger):
    """based on all files to read determine the size of the data"""

    dim = {}
    dim["time"] = 0
    for i, f in enumerate(list_files):

        nc_id = nc.Dataset(f, "r")

        dim["time"] += len(nc_id.dimensions[TIME_DIM])

        nc_id.close()

    logger.debug("time size = {}".format(dim["time"]))

    return dim


def init_data(vars_dim, logger):
    """initialize data dictionary"""

    data = {}

    data["time"] = np.empty((vars_dim["time"],), dtype=np.dtype(dt.datetime))
    data["time_bnds"] = np.empty((vars_dim["time"], 2), dtype=np.dtype(dt.datetime))
    data["freq_sb"] = (
        np.ones((vars_dim["n_freq"],), dtype=np.float32) * FLT_MISSING_VALUE
    )
    data["azi"] = np.ones((vars_dim["time"],), dtype=np.float32) * FLT_MISSING_VALUE
    data["ele"] = np.ones((vars_dim["time"],), dtype=np.float32) * FLT_MISSING_VALUE
    data["tb"] = (
        np.ones((vars_dim["time"], vars_dim["n_freq"]), dtype=np.float32)
        * FLT_MISSING_VALUE
    )
    data["offset_tb"] = (
        np.ones((vars_dim["time"], vars_dim["n_freq"]), dtype=np.float32)
        * FLT_MISSING_VALUE
    )
    data["freq_shift"] = (
        np.ones((vars_dim["n_freq"],), dtype=np.float32) * FLT_MISSING_VALUE
    )
    data["tb_bias"] = (
        np.ones((vars_dim["n_freq"],), dtype=np.float32) * FLT_MISSING_VALUE
    )
    data["tb_cov"] = (
        np.ones((vars_dim["n_freq"], vars_dim["n_freq2"]), dtype=np.float32)
        * FLT_MISSING_VALUE
    )
    data["wl_irp"] = (
        np.ones((vars_dim["n_wl_irp"]), dtype=np.float32) * FLT_MISSING_VALUE
    )
    data["tb_irp"] = (
        np.ones((vars_dim["time"], vars_dim["n_wl_irp"]), dtype=np.float32)
        * FLT_MISSING_VALUE
    )
    data["ele_irp"] = np.ones((vars_dim["time"],), dtype=np.float32) * FLT_MISSING_VALUE
    data["ta"] = np.ones((vars_dim["time"],), dtype=np.float32) * FLT_MISSING_VALUE
    data["pa"] = np.ones((vars_dim["time"],), dtype=np.float32) * FLT_MISSING_VALUE
    data["hur"] = np.ones((vars_dim["time"],), dtype=np.float32) * FLT_MISSING_VALUE
    data["flag"] = np.zeros((vars_dim["time"],), dtype=np.int16)
    data["rain_flag"] = np.zeros((vars_dim["time"],), dtype=np.int16)

    return data


def init_meteo_data(vars_dim, logger):
    """initialize dict of meteo data"""

    meteo_data = {}

    meteo_data["time"] = np.empty((vars_dim["time"],), dtype=np.dtype(dt.datetime))
    meteo_data["ta"] = (
        np.ones((vars_dim["time"],), dtype=np.float32) * FLT_MISSING_VALUE
    )
    meteo_data["pa"] = (
        np.ones((vars_dim["time"],), dtype=np.float32) * FLT_MISSING_VALUE
    )
    meteo_data["hur"] = (
        np.ones((vars_dim["time"],), dtype=np.float32) * FLT_MISSING_VALUE
    )

    return meteo_data


def read_time(nc_id, logger):
    """read time variable"""

    time = nc_id.variables[TIME_VAR][:]
    units = correct_time_units(nc_id.variables[TIME_VAR].units)

    time = nc.num2date(time, units=units)

    return len(time), time


def sync_meteo(data, meteo_data, logger):
    """find in meteo data timestep corresponding to brightness data time"""

    common_time = np.intersect1d(
        data["time"][:], meteo_data["time"][:], assume_unique=True
    )

    logger.debug("common timesteps found : {:d}".format(common_time.size))

    time_filter = np.array(
        [True if t in common_time else False for t in data["time"][:]]
    )
    print("time elts :", np.count_nonzero(time_filter))
    meteo_time_filter = np.array(
        [True if t in common_time else False for t in meteo_data["time"][:]]
    )
    print("meteo elts :", np.count_nonzero(meteo_time_filter))

    data["ta"][time_filter] = meteo_data["ta"][meteo_time_filter]
    data["pa"][time_filter] = meteo_data["pa"][meteo_time_filter]
    data["hur"][time_filter] = meteo_data["hur"][meteo_time_filter]

    return data


def read_data(list_files, conf, logger):
    """raw2l1 plugin to read raw data of RPG hatpro
    bloundary layer temperature"""

    logger.debug("start reading data using reader for " + BRAND + " " + MODEL)
    for f in list_files:
        logger.debug("files to read : {}".format(f))

    meteo_avail = False
    # check if meteo data available
    if "ancillary" in conf and len(conf["ancillary"]) != 0:
        meteo_avail = True
        meteo_files = conf["ancillary"]
        logger.info("meteo data available")
        for f in meteo_files:
            logger.debug("files to read : {}".format(f))

    # get variables size
    vars_dim = get_data_size(list_files, logger)
    vars_dim["n_freq"] = int(conf["n_freq"])
    vars_dim["n_freq2"] = int(conf["n_freq2"])
    vars_dim["n_wl_irp"] = int(conf["n_wl_irp"])
    if meteo_avail:
        meteo_vars_dim = get_data_size(meteo_files, logger)

    # Initialize data
    data = init_data(vars_dim, logger)

    # read data
    time_ind = 0
    for i, f in enumerate(list_files):

        nc_id = nc.Dataset(f, "r")

        time_size, time = read_time(nc_id, logger)

        # determining index of data
        ind_s = time_ind
        ind_e = time_ind + time_size

        data["time"][ind_s:ind_e] = time
        data["ele"][ind_s:ind_e] = nc_id.variables["elevation_angle"][:]
        data["azi"][ind_s:ind_e] = nc_id.variables["azimuth_angle"][:]
        data["tb"][ind_s:ind_e, :] = nc_id.variables["TBs"][:]
        data["rain_flag"][ind_s:ind_e] = nc_id.variables["rain_flag"][:]

        if i == 0:
            data["freq_sb"] = nc_id.variables["frequencies"][:]

        nc_id.close()

        time_ind += time_size

    # read meteo_data
    if meteo_avail:

        meteo_data = init_meteo_data(meteo_vars_dim, logger)

        time_ind = 0
        for i, f in enumerate(meteo_files):

            nc_id = nc.Dataset(f, "r")

            time_size, time = read_time(nc_id, logger)

            # determining index of data
            ind_s = time_ind
            ind_e = time_ind + time_size

            meteo_data["time"][ind_s:ind_e] = time
            meteo_data["ta"][ind_s:ind_e] = nc_id.variables["env_temperature"][:]
            meteo_data["pa"][ind_s:ind_e] = nc_id.variables["env_pressure"][:] * 100.0
            meteo_data["hur"][ind_s:ind_e] = (
                nc_id.variables["env_relative_humidity"][:] / 100.0
            )

            nc_id.close()

            time_ind += time_size

        # synchronize meteo data from to brightness data
        data = sync_meteo(data, meteo_data, logger)

    # produce time_bounds variable
    time_units = conf["time_units"]
    integ_time = conf["integration_time"]
    data["time_bnds"][:, 0] = nc.date2num(data["time"], units=time_units)
    tmp = data["time"] + dt.timedelta(seconds=float(integ_time))
    data["time_bnds"][:, 1] = nc.date2num(tmp, units=time_units)

    # quality flags
    rain_filter = data["rain_flag"] == 1
    data["flag"][rain_filter] = 8

    return data
