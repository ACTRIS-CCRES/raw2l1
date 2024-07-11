import datetime as dt

import netCDF4 as nc
import numpy as np

# brand and model of the LIDAR
BRAND = "SigmaSpace"
MODEL = "MiniMPL"

# missing value for instrument (not provided in netCDF file)
MISSING_METEO = -999.0

# missing values
MISSING_INT = -9
MISSING_FLOAT = np.nan

# constant
DEG_2_K = 273.15
KM_2_M = 1.0e3
MIN_2_SEC = 60


def get_dimension_size(list_files, logger):
    """determine size of data"""

    data = {}
    data_dims = {}
    data_dims["time"] = 0

    logger.debug("determining size of data")

    for i_file, file_ in enumerate(list_files):
        logger.debug(f"reading {file_}")
        nc_id = nc.Dataset(file_, "r")

        if i_file == 0:
            # reading dimensions size
            data_dims["range_raw"] = nc_id.dimensions["range_raw"].size
            data_dims["range_nrb"] = nc_id.dimensions["range_nrb"].size
            data_dims["range_vbp"] = nc_id.dimensions["range_vbp"].size
            data_dims["n_cld"] = nc_id.dimensions["number_of_clouds"].size
            data_dims["n_cld_out"] = nc_id.dimensions["number_of_cloud_outlines"].size

            # reading dimensions variable
            data["range_raw"] = nc_id.variables["range_raw"][:] * KM_2_M
            data["range_nrb"] = nc_id.variables["range_nrb"][:] * KM_2_M
            data["range_vbp"] = nc_id.variables["range_vbp"][:] * KM_2_M
            data["n_cld"] = nc_id.variables["number_of_clouds"][:]
            data["n_cld_out"] = np.arange(data_dims["n_cld_out"])

        data_dims["time"] += nc_id.dimensions["time"].size

        nc_id.close()

    # log size of data
    fmt = "{} : {:d}"
    for key, value in list(data_dims.items()):
        logger.debug(fmt.format(key, value))

    return data_dims, data


def init(data, dims, conf, logger):
    """Init data dict with size of data"""

    logger.debug("init data variable")

    # scalar values
    data["serial_number"] = "missing"
    data["instrument_type"] = "missing"
    data["range_resol"] = MISSING_INT
    data["time_resol"] = MISSING_INT
    data["site"] = "missing"
    data["station_latitude"] = MISSING_FLOAT
    data["station_longitude"] = MISSING_FLOAT
    data["station_altitude"] = MISSING_FLOAT
    data["first_elevation_angle"] = MISSING_FLOAT
    data["first_azimuth_angle"] = MISSING_FLOAT

    # 1d values
    data["time"] = np.ones((dims["time"],), dtype=np.dtype(dt.datetime))
    data["temp_in"] = np.ones((dims["time"],), dtype="f4") * MISSING_FLOAT
    data["temp_out"] = np.ones((dims["time"],), dtype="f4") * MISSING_FLOAT
    data["rh_in"] = np.ones((dims["time"],), dtype="f4") * MISSING_FLOAT
    data["rh_out"] = np.ones((dims["time"],), dtype="f4") * MISSING_FLOAT
    data["ws_out"] = np.ones((dims["time"],), dtype="f4") * MISSING_FLOAT
    data["wd_out"] = np.ones((dims["time"],), dtype="f4") * MISSING_FLOAT
    data["pres_out"] = np.ones((dims["time"],), dtype="f4") * MISSING_FLOAT
    data["dew_point_out"] = np.ones((dims["time"],), dtype="f4") * MISSING_FLOAT
    data["rain_rate_out"] = np.ones((dims["time"],), dtype="f4") * MISSING_FLOAT
    data["elevation_angle"] = np.ones((dims["time"],), dtype="f4") * MISSING_FLOAT
    data["azimuth_angle"] = np.ones((dims["time"],), dtype="f4") * MISSING_FLOAT
    data["telescope_temp"] = np.ones((dims["time"],), dtype="f4") * MISSING_FLOAT
    data["detector_temp"] = np.ones((dims["time"],), dtype="f4") * MISSING_FLOAT
    data["laser_temp"] = np.ones((dims["time"],), dtype="f4") * MISSING_FLOAT
    data["latitude"] = np.ones((dims["time"],), dtype="f4") * MISSING_FLOAT
    data["longitude"] = np.ones((dims["time"],), dtype="f4") * MISSING_FLOAT
    data["altitude"] = np.ones((dims["time"],), dtype="f4") * MISSING_FLOAT
    data["laser_energy"] = np.ones((dims["time"],), dtype="f4") * MISSING_FLOAT
    data["syncpulse"] = np.ones((dims["time"],), dtype="f4") * MISSING_FLOAT
    data["lidar_ratio"] = np.ones((dims["time"],), dtype="f8") * MISSING_FLOAT
    data["aod"] = np.ones((dims["time"],), dtype="f8") * MISSING_FLOAT
    data["aod_age"] = np.ones((dims["time"],), dtype="i4") * MISSING_INT
    data["bckgrd_total"] = np.ones((dims["time"],), dtype="f4") * MISSING_FLOAT
    data["bckgrd_copol"] = np.ones((dims["time"],), dtype="f4") * MISSING_FLOAT
    data["bckgrd_crosspol"] = np.ones((dims["time"],), dtype="f4") * MISSING_FLOAT

    data["number_of_clouds"] = np.ones((dims["n_cld"],), dtype="i4") * MISSING_INT

    # 2d values
    data["copol_raw"] = (
        np.ones((dims["time"], dims["range_raw"]), dtype="f4") * MISSING_FLOAT
    )
    data["crosspol_raw"] = (
        np.ones((dims["time"], dims["range_raw"]), dtype="f4") * MISSING_FLOAT
    )
    data["copol_snr"] = (
        np.ones((dims["time"], dims["range_raw"]), dtype="f4") * MISSING_FLOAT
    )
    data["crosspol_snr"] = (
        np.ones((dims["time"], dims["range_raw"]), dtype="f4") * MISSING_FLOAT
    )
    data["depol_ratio"] = (
        np.ones((dims["time"], dims["range_nrb"]), dtype="f4") * MISSING_FLOAT
    )
    data["total_nrb"] = (
        np.ones((dims["time"], dims["range_nrb"]), dtype="f4") * MISSING_FLOAT
    )
    data["copol_nrb"] = (
        np.ones((dims["time"], dims["range_nrb"]), dtype="f4") * MISSING_FLOAT
    )
    data["crosspol_nrb"] = (
        np.ones((dims["time"], dims["range_nrb"]), dtype="f4") * MISSING_FLOAT
    )

    data["extinc_coeff"] = (
        np.ones((dims["time"], dims["range_vbp"]), dtype="f4") * MISSING_FLOAT
    )
    data["mass_concentration"] = (
        np.ones((dims["time"], dims["range_vbp"]), dtype="f4") * MISSING_FLOAT
    )
    data["vert_bck_coeff"] = (
        np.ones((dims["time"], dims["range_vbp"]), dtype="f4") * MISSING_FLOAT
    )
    data["particle_type"] = (
        np.ones((dims["time"], dims["range_nrb"]), dtype="f4") * MISSING_FLOAT
    )

    data["pbls"] = np.ones((dims["time"], dims["n_cld"]), dtype="f4")

    # 3d values
    data["clouds"] = (
        np.ones((dims["time"], dims["n_cld"], dims["n_cld_out"]), dtype="f8")
        * MISSING_FLOAT
    )

    return data


def read_scalar_values(data, nc_id, logger):
    """read scalar values from file. These values need to be read only one time"""

    logger.debug("reading serial number")
    data["serial_number"] = nc_id.device_serial_number
    logger.debug("reading instrument type")
    data["instrument_type"] = nc_id.card_type
    logger.debug("site name")
    data["site"] = nc_id.lidar_site
    logger.debug("reading time resolution")
    data["time_resol"] = int(nc_id.temporal_resolution.split()[0]) * MIN_2_SEC
    logger.debug("reading range resolution")
    data["range_resol"] = int(nc_id.range_bin_resolution.split()[0])
    logger.debug("reading station localization")
    data["station_latitude"] = nc_id.variables["latitude"][0]
    data["station_longitude"] = nc_id.variables["longitude"][0]
    data["station_altitude"] = nc_id.variables["altitude"][0]
    logger.debug("reading instrument angle")
    data["first_elevation_angle"] = nc_id.variables["elevation_angle"][0]
    data["first_azimuth_angle"] = nc_id.variables["azimuth_angle"][0]

    return data


def read_time(nc_id):
    """convert time format of file into datetime object"""

    year = nc_id.variables["year"][:]
    month = nc_id.variables["month"][:]
    day = nc_id.variables["day"][:]
    hour = nc_id.variables["hour"][:]
    minute = nc_id.variables["minute"][:]
    second = nc_id.variables["second"][:]

    tmp = []
    for y, m, d, hh, mm, ss in zip(year, month, day, hour, minute, second):
        tmp.append(dt.datetime(int(y), int(m), int(d), int(hh), int(mm), int(ss)))

    return np.array(tmp)


def read_nd_values(data, nc_id, time_ind, logger):
    """function to read n dimensions variables"""

    # determining size of data
    time_size = nc_id.dimensions["time"].size

    ind_b = time_ind
    ind_e = time_ind + time_size

    # reading data
    logger.debug("reading time dependant variables")
    data["time"][ind_b:ind_e] = read_time(nc_id)
    data["temp_in"][ind_b:ind_e] = nc_id.variables["weather_inside_temperature"][:]
    data["temp_out"][ind_b:ind_e] = nc_id.variables["weather_outside_temperature"][:]
    data["rh_in"][ind_b:ind_e] = nc_id.variables["weather_inside_humidity"][:]
    data["rh_out"][ind_b:ind_e] = nc_id.variables["weather_outside_humidity"][:]
    data["ws_out"][ind_b:ind_e] = nc_id.variables["weather_wind_speed"][:]
    data["wd_out"][ind_b:ind_e] = nc_id.variables["weather_wind_direction"][:]
    data["pres_out"][ind_b:ind_e] = nc_id.variables["weather_barometric_pressure"][:]
    data["dew_point_out"][ind_b:ind_e] = nc_id.variables["weather_dew_point"][:]
    data["rain_rate_out"][ind_b:ind_e] = nc_id.variables["weather_rain_rate"][:]
    data["elevation_angle"][ind_b:ind_e] = nc_id.variables["elevation_angle"][:]
    data["azimuth_angle"][ind_b:ind_e] = nc_id.variables["azimuth_angle"][:]
    data["telescope_temp"][ind_b:ind_e] = nc_id.variables["telescope_temperature"][:]
    data["detector_temp"][ind_b:ind_e] = nc_id.variables["detector_temperature"][:]
    data["laser_temp"][ind_b:ind_e] = nc_id.variables["laser_temperature"][:]
    data["latitude"][ind_b:ind_e] = nc_id.variables["latitude"][:]
    data["longitude"][ind_b:ind_e] = nc_id.variables["longitude"][:]
    data["altitude"][ind_b:ind_e] = nc_id.variables["altitude"][:]
    data["laser_energy"][ind_b:ind_e] = nc_id.variables["laser_energy"][:]
    data["syncpulse"][ind_b:ind_e] = nc_id.variables["syncpulse"][:]
    data["lidar_ratio"][ind_b:ind_e] = nc_id.variables["lidar_ratio"][:]
    data["aod"][ind_b:ind_e] = nc_id.variables["aod"][:]
    data["aod_age"][ind_b:ind_e] = nc_id.variables["aod_age_secs"][:]
    data["bckgrd_copol"][ind_b:ind_e] = nc_id.variables["copol_background"][:]
    data["bckgrd_crosspol"][ind_b:ind_e] = nc_id.variables["crosspol_background"][:]

    # 2d values
    data["copol_raw"][ind_b:ind_e, :] = nc_id.variables["copol_raw"][:]
    data["crosspol_raw"][ind_b:ind_e, :] = nc_id.variables["crosspol_raw"][:]
    data["copol_snr"][ind_b:ind_e, :] = nc_id.variables["copol_snr"][:]
    data["crosspol_snr"][ind_b:ind_e, :] = nc_id.variables["crosspol_snr"][:]
    data["depol_ratio"][ind_b:ind_e, :] = nc_id.variables["depolarization_ratio"][:]
    data["copol_nrb"][ind_b:ind_e, :] = nc_id.variables["copol_nrb"][:]
    data["crosspol_nrb"][ind_b:ind_e, :] = nc_id.variables["crosspol_nrb"][:]
    data["pbls"][ind_b:ind_e, :] = nc_id.variables["pbls"][:] * KM_2_M

    data["extinc_coeff"][ind_b:ind_e, :] = nc_id.variables["extinction_coefficient"][:]
    data["mass_concentration"][ind_b:ind_e, :] = nc_id.variables["mass_concentration"][
        :
    ]
    data["vert_bck_coeff"][ind_b:ind_e, :] = nc_id.variables["VBP"][:]
    data["particle_type"][ind_b:ind_e, :] = nc_id.variables["particle_type"][:]

    # 3d values
    data["clouds"][ind_b:ind_e, :, :] = nc_id.variables["clouds"][:] * KM_2_M

    return data, time_size


def read_data(list_files, conf, logger):
    """
    Raw2L1 plugin to read raw data of SigmaSpace MiniMPL
    """

    logger.debug("Start reading of data using reader for " + BRAND + " " + MODEL)

    # update missing values
    if "missing_int" in conf:
        MISSING_INT = conf["missing_int"]
    if "missing_float" in conf:
        MISSING_FLOAT = conf["missing_float"]

    # get size of data to read
    # ------------------------------------------------------------------------
    logger.info("Determining size of data")
    data_dims, data = get_dimension_size(list_files, logger)

    # initialize data arrays
    # ------------------------------------------------------------------------
    data = init(data, data_dims, conf, logger)

    # read data
    # ------------------------------------------------------------------------
    time_ind = 0
    for i_file, file_ in enumerate(list_files):
        nc_id = nc.Dataset(file_, "r")
        nc_id.set_auto_mask(False)

        # read scalar values
        if i_file == 0:
            data = read_scalar_values(data, nc_id, logger)

        data, time_size = read_nd_values(data, nc_id, time_ind, logger)

        nc_id.close()

        time_ind += time_size

    # add complementary variables and correct missing values
    # ------------------------------------------------------------------------

    # total rcs and background
    data["total_nrb"] = data["copol_nrb"] + 2.0 * data["crosspol_nrb"]
    data["bckgrd_total"] = data["bckgrd_copol"] + 2.0 * data["bckgrd_crosspol"]

    # start time
    data["start_time"] = data["time"] - dt.timedelta(seconds=data["time_resol"])

    # clouds and pbls replace missing values
    data["clouds"][np.isnan(data["clouds"])] = MISSING_FLOAT
    data["pbls"][np.isnan(data["pbls"])] = MISSING_FLOAT

    # meteo data in case instruments are missing
    vars_to_correct = [
        ("temp_in", MISSING_METEO),
        ("temp_out", MISSING_METEO),
        ("rh_in", MISSING_METEO),
        ("rh_out", MISSING_METEO),
        ("ws_out", MISSING_METEO),
        ("wd_out", MISSING_METEO),
        ("pres_out", MISSING_METEO),
        ("dew_point_out", MISSING_METEO),
        ("rain_rate_out", MISSING_METEO),
        ("laser_energy", MISSING_METEO),
        ("aod_age", -1),
    ]

    for var in vars_to_correct:
        if data[var[0]].dtype.kind == "i":
            missing = MISSING_INT
        else:
            missing = MISSING_FLOAT

        data[var[0]][data[var[0]] == var[1]] = missing

    # split cloud variables into 3 variables
    data["cbh"] = data["clouds"][:, :, 0]
    data["cloud_max_intensity"] = data["clouds"][:, :, 1]
    data["cloud_highest"] = data["clouds"][:, :, 2]

    # convert temperature to kelvins
    vars_to_convert = [
        "temp_in",
        "temp_out",
        "dew_point_out",
        "telescope_temp",
        "detector_temp",
        "laser_temp",
    ]

    for var in vars_to_convert:
        data[var][data[var] != MISSING_FLOAT] = (
            data[var][data[var] != MISSING_FLOAT] + DEG_2_K
        )

    # laser energy to joule
    data["laser_energy"][data["laser_energy"] != MISSING_FLOAT] = (
        data["laser_energy"][data["laser_energy"] != MISSING_FLOAT] * 1.0e-6
    )

    # add date in separate variables
    data["year"] = np.array([d.year for d in data["time"]])
    data["month"] = np.array([d.month for d in data["time"]])
    data["day"] = np.array([d.day for d in data["time"]])
    data["hour"] = np.array([d.hour for d in data["time"]])
    data["minute"] = np.array([d.minute for d in data["time"]])
    data["second"] = np.array([d.second for d in data["time"]])

    return data
