import datetime as dt

import netCDF4 as nc
import numpy as np

from .libhatpro import correct_time_units

# brand and model of the LIDAR
BRAND = "RPG"
MODEL = "HATPRO boundary layer temperature"

TIME_DIM = "time"
TIME_VAR = "time"


FLT_MISSING_VALUE = -999.0
INT_MISSING_VALUE = -9

C2K = 273.15


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


def init_irt_data(vars_dim, logger):
    """initialize dict of irt data"""

    irt_data = {}

    irt_data["time"] = np.empty((vars_dim["time"],), dtype=np.dtype(dt.datetime))
    irt_data["wl_irp"] = (
        np.ones((vars_dim["n_wl_irp"]), dtype=np.float32) * FLT_MISSING_VALUE
    )
    irt_data["tb_irp"] = (
        np.ones((vars_dim["time"], vars_dim["n_wl_irp"]), dtype=np.float32)
        * FLT_MISSING_VALUE
    )
    irt_data["ele_irp"] = (
        np.ones((vars_dim["time"],), dtype=np.float32) * FLT_MISSING_VALUE
    )

    return irt_data


def read_time(nc_id, logger):
    """read time variable"""

    time = nc_id.variables[TIME_VAR][:]
    units = correct_time_units(nc_id.variables[TIME_VAR].units)

    time = nc.num2date(time, units=units)

    return len(time), time


def sync_meteo(data, meteo_data, logger):
    """find in meteo data timestep corresponding to brightness data time"""

    common_time, time_filter, meteo_time_filter = np.intersect1d(
        data["time"][:], meteo_data["time"][:], return_indices=True
    )

    logger.debug("common timesteps found for meteo : {:d}".format(common_time.size))

    data["ta"][time_filter] = meteo_data["ta"][meteo_time_filter]
    data["pa"][time_filter] = meteo_data["pa"][meteo_time_filter]
    data["hur"][time_filter] = meteo_data["hur"][meteo_time_filter]

    return data


def sync_irt(data, irt_data, logger):
    """find in irt data timestep corresponding to brightness data time"""

    common_time, time_filter, irt_time_filter = np.intersect1d(
        data["time"][:], irt_data["time"][:], return_indices=True
    )

    data["ele_irp"][time_filter] = irt_data["ele_irp"][irt_time_filter]
    data["tb_irp"][time_filter, :] = irt_data["tb_irp"][irt_time_filter, :]

    return data


def read_data(list_files, conf, logger):
    """raw2l1 plugin to read raw data of RPG hatpro
    bloundary layer temperature"""

    logger.debug("start reading data using reader for " + BRAND + " " + MODEL)
    for f in list_files:
        logger.debug("files to read : {}".format(f))

    meteo_avail = False

    # modif PM fourni par Marc-Antoine le 27/11/2019
    if "ancillary" in conf and conf["ancillary"][0]:
        meteo_avail = True
        meteo_files = conf["ancillary"][0]
        logger.info("meteo data available")
        for f in meteo_files:
            logger.debug("files to read : {}".format(f))

    # IRT files
    irt_avail = False
    try:
        irt_files = conf["ancillary"][1]
        irt_avail = True
        logger.info("irt data available")
    except IndexError:
        pass

    # get variables size
    vars_dim = get_data_size(list_files, logger)
    vars_dim["n_freq"] = int(conf["n_freq"])
    vars_dim["n_freq2"] = int(conf["n_freq2"])
    vars_dim["n_wl_irp"] = int(conf["n_wl_irp"])
    if meteo_avail:
        meteo_vars_dim = get_data_size(meteo_files, logger)
    if irt_avail:
        irt_vars_dim = get_data_size(irt_files, logger)
        irt_vars_dim["n_wl_irp"] = vars_dim["n_wl_irp"]

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

    # irt data
    if irt_avail:
        irt_data = init_irt_data(irt_vars_dim, logger)

        time_ind = 0
        for i, f in enumerate(irt_files):
            nc_id = nc.Dataset(f, "r")

            time_size, time = read_time(nc_id, logger)

            # determining index of data
            ind_s = time_ind
            ind_e = time_ind + time_size

            irt_data["time"][ind_s:ind_e] = time
            if i == 0:
                data["wl_irp"] = nc_id.variables["frequencies"][:]
            irt_data["tb_irp"][ind_s:ind_e, :] = nc_id.variables["IRR_data"][:] + C2K
            irt_data["ele_irp"][ind_s:ind_e] = nc_id.variables["elevation_angle"][:]

            nc_id.close()

            time_ind += time_size
        # synchronize meteo data from to brightness data
        data = sync_irt(data, irt_data, logger)

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
