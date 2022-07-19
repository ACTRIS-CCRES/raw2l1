"""Raw2l1 reader for VAISALA CL61 ceilometers netCDF files."""
import datetime as dt
import sys

import netCDF4 as nc
import numpy as np

# brand and model of the LIDAR
BRAND = "vaisala"
MODEL = "CL61"

# missing values
MISSING_INT = -9
MISSING_FLOAT = np.nan

# physical constants
CELSIUS_TO_KELVIN = 273.15


def get_dimension_size(list_files, logger):
    """
    Determine the size of dimensions.

    Parameters
    ----------
    list_files : list of str
        The list of files to analyze.
    logger : logging.Logger
        Logger object to log the progress.

    Returns
    -------
    dict
        Dictionary with the dimensions of the data (time, range, layer)

    """
    # get size of data to read
    logger.info("Determining size of data")
    data_dims = {}

    for i_file, file_ in enumerate(list_files):

        logger.debug("reading {}".format(file_))
        nc_id = nc.Dataset(file_, "r")

        if i_file == 0:
            data_dims["range"] = nc_id.dimensions["range"].size
            data_dims["layer"] = nc_id.dimensions["layer"].size
            try:
                data_dims["time"] = nc_id.dimensions["time"].size
            except KeyError:
                data_dims["time"] = nc_id.dimensions["profile"].size
        else:
            # unlimited dimensions
            try:
                data_dims["time"] += nc_id.dimensions["time"].size
            except KeyError:
                data_dims["time"] += nc_id.dimensions["profile"].size

        nc_id.close()

    # log size of data
    for var_name, size in data_dims.items():
        logger.debug("%s : %d", var_name, size)

    return data_dims


def get_fw_version(nc_id, logger):
    """
    Get firmware version from netCDF file.

    Parameters
    ----------
    nc_id : netCDF4.Dataset
        NetCDF file object.
    logger : logging.Logger
        Logger object to log the progress.

    Returns
    -------
    str
        Firmware version.
    float
        major firmware version for comparison

    """
    logger.debug("reading firmware version")

    fw_version = nc_id.history
    logger.debug("firmware version: %s", fw_version)

    # fw version can be x.x.x or x.x.x-rcx for first versions
    fl_fw_version = float(".".join(fw_version.split("-")[0].split(".")[0:2]))

    return fw_version, fl_fw_version


def init(data, dims, conf, logger):
    """
    Initialize data variables store in dictionary.

    Parameters
    ----------
    data : dict
        Dictionary to store the data.
    dims : dict
        Dictionary with the dimensions of the data.
    conf : dict
        Configuration dictionary from configuration file.
    logger : logging.Logger
        Logger object to log the progress.

    Returns
    -------
    dict
        Dictionary to store the data with variables initialized.

    """
    # get missing values
    missing_float = conf["missing_float"]

    # dimensions variables
    # ------------------------------------------------------------------------
    data["time"] = np.ones(dims["time"], dtype=np.dtype(dt.datetime))
    data["layer"] = np.ones(dims["layer"], dtype="i4")
    data["range"] = np.ones(dims["range"], dtype="i4")

    # time dependant variables
    # ------------------------------------------------------------------------
    data["vertical_visibility"] = np.ones((dims["time"],), dtype="f4") * missing_float
    data["beta_sum"] = np.ones((dims["time"],), dtype="f4") * missing_float
    data["beta_noise"] = np.ones((dims["time"],), dtype="f4") * missing_float
    data["lat"] = np.ones((dims["time"],), dtype="f4") * missing_float
    data["lon"] = np.ones((dims["time"],), dtype="f4") * missing_float
    data["alt"] = np.ones((dims["time"],), dtype="f4") * missing_float

    # Time, layer dependant variables
    # -------------------------------------------------------------------------
    data["cbh"] = np.ones((dims["time"], dims["layer"]), dtype=np.int32) * missing_float

    # Time, range dependent variables
    # -------------------------------------------------------------------------
    data["rcs_0"] = (
        np.ones((dims["time"], dims["range"]), dtype=np.float32) * missing_float
    )
    data["rcs_1"] = (
        np.ones((dims["time"], dims["range"]), dtype=np.float32) * missing_float
    )
    data["rcs_2"] = (
        np.ones((dims["time"], dims["range"]), dtype=np.float32) * missing_float
    )
    data["beta"] = (
        np.ones((dims["time"], dims["range"]), dtype=np.float32) * missing_float
    )
    data["linear_depol_ratio"] = (
        np.ones((dims["time"], dims["range"]), dtype=np.float32) * missing_float
    )

    # house keeping data variables
    # -------------------------------------------------------------------------
    data["rh_int"] = np.ones((dims["time"],), dtype="f4") * missing_float
    data["temp_int"] = np.ones((dims["time"],), dtype="f4") * missing_float
    data["pres_int"] = np.ones((dims["time"],), dtype="f4") * missing_float
    data["laser_temp"] = np.ones((dims["time"],), dtype="f4") * missing_float
    data["laser_energy"] = np.ones((dims["time"],), dtype="f4") * missing_float
    data["window_transmission"] = np.ones((dims["time"],), dtype="f4") * missing_float

    return data


def read_limited_dims(data, nc_id, logger):
    """
    Read limited dimensions from netCDF file.

    Parameters
    ----------
    data : dict
        Dictionary to store the data.
    nc_id : netCDF4.Dataset
        NetCDF file object.
    logger : logging.Logger
        Logger object to log the progress.

    Returns
    -------
    dict
        Dictionary with the data read.

    """
    logger.debug("reading range and layer dimensions")
    data["range"] = nc_id.variables["range"][:]
    data["layer"] = nc_id.variables["layer"][:]

    return data


def read_scalar_vars(data, nc_id, logger):
    """
    Read scalar variables from netCDF file.

    Parameters
    ----------
    data : dict
        Dictionary to store the data.
    nc_id : netCDF4.Dataset
        NetCDF file object.
    logger : logging.Logger
        Logger object to log the progress.

    Returns
    -------
    dict
        Dictionary with the data read.

    """
    logger.debug("reading localization of the instrument")
    data["station_lat"] = nc_id.variables["latitude"][0]
    data["station_lon"] = nc_id.variables["longitude"][0]
    data["station_alt"] = nc_id.variables["elevation"][0]

    # time resolution (has to be converted from global attributes)
    data["time_resol"] = nc_id.getncattr("time between consecutive profiles in seconds")
    data["range_resol"] = np.mean(data["range"][1:] - data["range"][:-1])

    # instrument informations
    data["instrument_id"] = nc_id.title.split(",")[0]
    data["software_id"] = nc_id.history

    return data


def read_timedep_vars(data, nc_id, time_ind, logger):
    """
    Read 1d and 2d time dependant variables from netCDF file.

    Parameters
    ----------
    data : dict
        Dictionary to store the data.
    nc_id : netCDF4.Dataset
        NetCDF file object.
    time_ind : int
        Index of the time to read.
    logger : logging.Logger
        Logger object to log the progress.

    Returns
    -------
    int
        The size of data read.
    dict
        Dictionary with the data read.

    """
    # dimensions variables
    # ------------------------------------------------------------------------
    time = nc.num2date(nc_id.variables["time"][:], units=nc_id.variables["time"].units)
    time_size = time.size

    # index size
    ind_b = time_ind
    ind_e = time_ind + time_size

    data["time"][ind_b:ind_e] = time
    logger.debug(
        "processing timesteps %s to %s", data["time"][ind_b], data["time"][ind_e - 1]
    )

    # time dependant variables variables
    # ------------------------------------------------------------------------
    data["vertical_visibility"][ind_b:ind_e] = nc_id.variables["vertical_visibility"][:]
    data["beta_sum"][ind_b:ind_e] = nc_id.variables["beta_att_sum"][:]
    data["beta_noise"][ind_b:ind_e] = nc_id.variables["beta_att_noise_level"][:]
    data["lat"][ind_b:ind_e] = nc_id.variables["latitude"][:]
    data["lon"][ind_b:ind_e] = nc_id.variables["longitude"][:]
    data["alt"][ind_b:ind_e] = nc_id.variables["elevation"][:]

    # Time, layer dependant variables
    # -------------------------------------------------------------------------
    data["cbh"][ind_b:ind_e, :] = nc_id.variables["cloud_base_heights"][:]

    # Time, range dependent variables
    # -------------------------------------------------------------------------
    data["rcs_1"][ind_b:ind_e, :] = nc_id.variables["p_pol"][:]
    data["rcs_2"][ind_b:ind_e, :] = nc_id.variables["x_pol"][:]
    data["beta"][ind_b:ind_e, :] = nc_id.variables["beta_att"][:]
    data["linear_depol_ratio"][ind_b:ind_e, :] = nc_id.variables["linear_depol_ratio"][
        :
    ]

    # house keeping data variables
    # -------------------------------------------------------------------------
    # only available for firmware >= 1.1
    if data["float_fw_version"] >= 1.1:
        logger.debug("reading house keeping data")
        data["rh_int"][ind_b:ind_e] = nc_id["monitoring"].internal_humidity
        data["temp_int"][ind_b:ind_e] = nc_id["monitoring"].internal_temperature
        data["pres_int"][ind_b:ind_e] = nc_id["monitoring"].internal_pressure
        data["laser_temp"][ind_b:ind_e] = nc_id["monitoring"].laser_temperature
        data["laser_energy"][ind_b:ind_e] = nc_id["monitoring"].laser_power_percent
        data["window_transmission"][ind_b:ind_e] = nc_id["monitoring"].window_condition

    return time_size, data


def read_data(list_files, conf, logger):
    """
    Raw2L1 plugin to read data of the vaisala CL61.

    Parameters
    ----------
    list_files : list of str
        List of files to read.
    conf : dict
        Configuration dictionary from configuration file.
    logger : logging.Logger
        Logger object to log the progress.

    Returns
    -------
    dict
        Dictionary with the following keys:

    """
    logger.debug("Start reading of data using reader for " + BRAND + " " + MODEL)

    # update missing values
    if "missing_int" in conf:
        MISSING_INT = conf["missing_int"]
    if "missing_float" in conf:
        MISSING_FLOAT = conf["missing_float"]

    # dictionary to store the data
    # ------------------------------------------------------------------------
    data = {}

    # get size of data to read and init variables
    # ------------------------------------------------------------------------
    logger.info("Determining size of data")
    data_dims = get_dimension_size(list_files, logger)
    logger.info("initializing data output array")
    data = init(data, data_dims, conf, logger)

    nb_files = 0
    nb_files_read = 0
    time_ind = 0
    # Loop over the list of files
    for ifile in list_files:

        # Opening file
        try:
            raw_data = nc.Dataset(ifile, "r")
            nb_files_read += 1
        except (RuntimeError, IOError):
            logger.error("109 unable to load " + ifile + " trying next one")

        nb_files += 1
        logger.debug("reading %02d: " % (nb_files) + ifile)

        # Data which only need to be read in one file
        if nb_files_read == 1:

            # reading firmware version
            # ----------------------------------------------------------------
            data["fw_version"], data["float_fw_version"] = get_fw_version(
                raw_data, logger
            )

            # read dimensions
            # ----------------------------------------------------------------
            logger.info("reading dimension variables")
            data = read_limited_dims(data, raw_data, logger)

            # read scalar
            # ----------------------------------------------------------------
            logger.info("reading scalar variables")
            data = read_scalar_vars(data, raw_data, logger)

        if nb_files_read >= 1:
            # Time dependant variables
            logger.info("reading time dependant variables for file %02d", nb_files_read)
            time_size, data = read_timedep_vars(data, raw_data, time_ind, logger)

            # increment indexes
            time_ind += time_size

        # Close NetCDF file
        # --------------------------------------------------------------------
        raw_data.close()

    if nb_files_read == 0:
        for file_ in list_files:
            logger.critical(
                "109 Tried to read '{}'. No file could be read".format(file_)
            )
        sys.exit(1)

    # full backscatter
    data["rcs_0"] = data["rcs_1"] + data["rcs_2"]

    # start time of measurements
    data["start_time"] = data["time"] - dt.timedelta(seconds=int(data["time_resol"]))

    # change of units
    data["temp_int"] += CELSIUS_TO_KELVIN
    data["laser_temp"] += CELSIUS_TO_KELVIN

    # force localization if defined in conf file
    if "lat" in conf:
        data["station_lat"] = float(conf["lat"])
    if "lon" in conf:
        data["station_lon"] = float(conf["lon"])
    if "alt" in conf:
        data["station_alt"] = float(conf["alt"])

    return data
