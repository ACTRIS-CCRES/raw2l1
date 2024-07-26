"""
Raw2l1 reader for VAISALA CL61 ceilometers netCDF files.

Notes
-----
Compatibility with firmware 1.2 based on developments of Alexander Geiss (LMU)
"""

import datetime as dt
import sys

import netCDF4 as nc
import numpy as np

# brand and model of the LIDAR
BRAND = "vaisala"
MODEL = "CL61"

# missing values
MISSING_INT = -9
MISSING_FLOAT = -999.9

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
        logger.debug("reading %s", file_)
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

    try:
        fw_version = nc_id.sw_version
    except AttributeError:
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
    # scalar variables
    # ------------------------------------------------------------------------
    data["tilt_angle_first"] = MISSING_FLOAT
    data["time_resol"] = MISSING_FLOAT
    data["range_resol"] = MISSING_FLOAT

    # dimensions variables
    # ------------------------------------------------------------------------
    data["time"] = np.ones(dims["time"], dtype=np.dtype(dt.datetime))
    data["layer"] = np.ones(dims["layer"], dtype="i4")
    data["range"] = np.ones(dims["range"], dtype="i4")

    # time dependant variables
    # ------------------------------------------------------------------------
    ones_int16 = np.ones((dims["time"],), dtype="i2") * MISSING_INT
    ones_flt32 = np.ones((dims["time"],), dtype="f4") * MISSING_FLOAT
    data["vertical_visibility"] = ones_flt32.copy()
    data["fog_detection"] = ones_int16.copy()
    data["precipitation_detection"] = ones_int16.copy()
    data["receiver_gain"] = ones_int16.copy()
    data["beta_sum"] = ones_flt32.copy()
    data["beta_noise"] = ones_flt32.copy()
    data["lat"] = ones_flt32.copy()
    data["lon"] = ones_flt32.copy()
    data["alt"] = ones_flt32.copy()
    data["tilt_angle"] = ones_flt32.copy()
    data["tilt_angle_correction"] = ones_int16.copy()
    data["cloud_cover"] = ones_flt32.copy()

    # range dependent variables
    # -------------------------------------------------------------------------
    data["overlap_function"] = np.ones((dims["range"],), dtype="f4") * MISSING_FLOAT

    # Time, layer dependant variables
    # -------------------------------------------------------------------------
    ones_int32 = np.ones((dims["time"], dims["layer"]), dtype="i4") * MISSING_INT
    ones_flt32 = np.ones((dims["time"], dims["layer"]), dtype="f4") * MISSING_FLOAT
    data["cbh"] = ones_flt32.copy()
    data["cloud_penetration_depth"] = ones_int32.copy()
    data["cloud_thickness"] = ones_int32.copy()
    # starting fw 1.1.x
    data["cloud_cover"] = np.ones((dims["time"]), dtype=np.int32) * MISSING_INT
    data["cloud_layer_cover"] = ones_int32.copy()
    data["cloud_layer_height"] = ones_flt32.copy()

    # Time, range dependent variables
    # -------------------------------------------------------------------------
    ones_flt32 = np.ones((dims["time"], dims["range"]), dtype="f4")
    data["rcs_0"] = ones_flt32.copy()
    data["rcs_1"] = ones_flt32.copy()
    data["rcs_2"] = ones_flt32.copy()
    data["beta"] = ones_flt32.copy()
    data["linear_depol_ratio"] = ones_flt32.copy()

    # house keeping data variables
    # -------------------------------------------------------------------------
    ones_flt32 = np.ones((dims["time"],), dtype="f4") * MISSING_FLOAT
    ones_int16 = np.ones((dims["time"],), dtype="i2") * MISSING_INT
    data["hkd_rh_int"] = ones_flt32.copy()
    data["hkd_temp_int"] = ones_flt32.copy()
    data["hkd_temp_trans"] = ones_flt32.copy()
    data["hkd_pres_int"] = ones_flt32.copy()
    data["hkd_temp_laser"] = ones_flt32.copy()
    data["hkd_state_laser"] = ones_flt32.copy()
    data["hkd_state_optics"] = ones_flt32.copy()
    data["hkd_bkgd_radiance"] = ones_flt32.copy()
    data["hkd_heater_int"] = ones_int16.copy()
    data["hkd_window_blower"] = ones_int16.copy()
    data["hkd_window_blower_heater"] = ones_int16.copy()

    # Status variables (string)
    # -------------------------------------------------------------------------
    ones_int16 = np.ones((dims["time"],), dtype="i2") * MISSING_INT
    # device
    data["status_device_controller_temperature"] = ones_int16.copy()
    data["status_device_controller_electronics"] = ones_int16.copy()
    data["status_device_controller_overall"] = ones_int16.copy()
    # optics
    data["status_optics_unit_accelerometer"] = ones_int16.copy()
    data["status_optics_unit_electronics"] = ones_int16.copy()
    data["status_optics_unit_overall"] = ones_int16.copy()
    data["status_optics_unit_memory"] = ones_int16.copy()
    data["status_optics_unit_tilt_angle"] = ones_int16.copy()
    # receiver
    data["status_receiver_electronics"] = ones_int16.copy()
    data["status_receiver_overall"] = ones_int16.copy()
    data["status_receiver_memory"] = ones_int16.copy()
    data["status_receiver_voltage"] = ones_int16.copy()
    data["status_receiver_solar_saturation"] = ones_int16.copy()
    data["status_receiver_sensitivity"] = ones_int16.copy()
    # window
    data["status_window_blocking"] = ones_int16.copy()
    data["status_window_condition"] = ones_int16.copy()
    data["status_window_blower_fan"] = ones_int16.copy()
    data["status_window_blower_heater"] = ones_int16.copy()
    # servo
    data["status_servo_drive_electronics"] = ones_int16.copy()
    data["status_servo_drive_overall"] = ones_int16.copy()
    data["status_servo_drive_memory"] = ones_int16.copy()
    data["status_servo_drive_control"] = ones_int16.copy()
    data["status_servo_drive_ready"] = ones_int16.copy()
    # transmitter
    data["status_transmitter_electronics"] = ones_int16.copy()
    data["status_transmitter_light_source"] = ones_int16.copy()
    data["status_transmitter_light_source_power"] = ones_int16.copy()
    data["status_transmitter_overall"] = ones_int16.copy()
    data["status_transmitter_light_source_safety"] = ones_int16.copy()
    data["status_transmitter_memory"] = ones_int16.copy()
    # others
    data["status_maintenance_overall"] = ones_int16.copy()
    data["status_device_overall"] = ones_int16.copy()
    data["status_recently_started"] = ones_int16.copy()
    data["status_measurement_status"] = ones_int16.copy()
    data["status_datacom_overall"] = ones_int16.copy()
    data["status_measurement_data_destination_not_set"] = ones_int16.copy()
    data["status_inside_heater"] = ones_int16.copy()
    data["status_data_generation_status"] = ones_int16.copy()

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

    # suppose that instrument doesn't move
    data["station_lat"] = nc_id.variables["latitude"][0]
    data["station_lon"] = nc_id.variables["longitude"][0]
    data["station_alt"] = nc_id.variables["elevation"][0]

    # tilt angle (if no change)
    if data["float_fw_version"] >= 1.1:
        data["tilt_angle_first"] = nc_id.variables["tilt_angle"][0]

    # time resolution
    # fmt:off
    if data["float_fw_version"] <= 1.1:
        # time resolution (has to be converted from global attributes)
        data["time_resol"] = nc_id.getncattr("time between consecutive profiles in seconds")  # noqa
        data["range_resol"] = np.mean(data["range"][1:] - data["range"][:-1])
    elif data["float_fw_version"] >= 1.2:
        data["time_resol"] = nc_id.profile_interval_in_seconds
        data["range_resol"] = nc_id.variables["range_resolution"][:]

    # instrument informations
    if data["float_fw_version"] <= 1.1:
        data["instrument_id"] = nc_id.title.split(",")[0]
        data["azimuth_angle"] = MISSING_FLOAT
        data["cloud_calibration_factor"] = MISSING_FLOAT
        data["cloud_calibration_factor_user"] = MISSING_FLOAT
    elif data["float_fw_version"] >= 1.2:
        data["cloud_calibration_factor"] = nc_id.variables["cloud_calibration_factor"][:]  # noqa
        data["cloud_calibration_factor_user"] = nc_id.variables["cloud_calibration_factor_user"][:]  # noqa
        data["azimuth_angle"] = nc_id.variables["azimuth_angle"][:]
        data["instrument_id"] = nc_id.instrument_serial_number
    # fmt: on

    data["software_id"] = nc_id.history
    data["site_location"] = nc_id.comment

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
    # fmt: off
    data["vertical_visibility"][ind_b:ind_e] = nc_id.variables["vertical_visibility"][:]
    if data["float_fw_version"] >= 1.2:
        data["fog_detection"][ind_b:ind_e] = nc_id.variables["fog_detection"][:]
        data["precipitation_detection"][ind_b:ind_e] = nc_id.variables["precipitation_detection"][:]  # noqa
        data["receiver_gain"][ind_b:ind_e] = nc_id.variables["receiver_gain"][:]
    data["beta_sum"][ind_b:ind_e] = nc_id.variables["beta_att_sum"][:]
    data["beta_noise"][ind_b:ind_e] = nc_id.variables["beta_att_noise_level"][:]
    data["lat"][ind_b:ind_e] = nc_id.variables["latitude"][:]
    data["lon"][ind_b:ind_e] = nc_id.variables["longitude"][:]
    data["alt"][ind_b:ind_e] = nc_id.variables["elevation"][:]
    if data["float_fw_version"] >= 1.1:
        data["cloud_cover"][ind_b:ind_e] = nc_id.variables["sky_condition_total_cloud_cover"][:]  # noqa
        data["tilt_angle"][ind_b:ind_e] = nc_id.variables["tilt_angle"][:]
        data["tilt_angle_correction"][ind_b:ind_e] = nc_id.variables["tilt_correction"][:]  # noqa
    # fmt: on

    # Time, layer dependant variables
    # -------------------------------------------------------------------------
    # fmt: off
    data["cbh"][ind_b:ind_e, :] = nc_id.variables["cloud_base_heights"][:]
    # starting fw 1.1.x
    if data["float_fw_version"] >= 1.1:
        data["cloud_cover"][ind_b:ind_e] = nc_id.variables["sky_condition_total_cloud_cover"][:]  # noqa
        data["cloud_layer_cover"][ind_b:ind_e, :] = nc_id.variables["sky_condition_cloud_layer_covers"][:]  # noqa
        data["cloud_layer_height"][ind_b:ind_e, :] = nc_id.variables["sky_condition_cloud_layer_heights"][:]  # noqa
    if data["float_fw_version"] >= 1.2:
        data["cloud_penetration_depth"][ind_b:ind_e, :] = nc_id.variables["cloud_penetration_depth"][:]  # noqa
        data["cloud_thickness"][ind_b:ind_e, :] = nc_id.variables["cloud_thickness"][:]
    # fmt: off

    # Time, range dependent variables
    # -------------------------------------------------------------------------
    # fmt: off
    data["rcs_1"][ind_b:ind_e, :] = nc_id.variables["p_pol"][:]
    data["rcs_2"][ind_b:ind_e, :] = nc_id.variables["x_pol"][:]
    data["beta"][ind_b:ind_e, :] = nc_id.variables["beta_att"][:]
    data["linear_depol_ratio"][ind_b:ind_e, :] = nc_id.variables["linear_depol_ratio"][:]  # noqa
    # fmt: on

    # house keeping data variables
    # -------------------------------------------------------------------------
    # only available for firmware >= 1.1
    logger.debug("reading house keeping data")

    if data["float_fw_version"] >= 1.1:
        mon = nc_id["monitoring"]

    # fw v1.1 HKD are attributes of the monitoring group
    if data["float_fw_version"] == 1.1:
        data["hkd_bkgd_radiance"][ind_b:ind_e] = mon.background_radiance
        data["hkd_rh_int"][ind_b:ind_e] = mon.internal_humidity
        data["hkd_temp_int"][ind_b:ind_e] = mon.internal_temperature
        data["hkd_pres_int"][ind_b:ind_e] = mon.internal_pressure
        data["hkd_temp_laser"][ind_b:ind_e] = mon.laser_temperature
        data["hkd_state_laser"][ind_b:ind_e] = mon.laser_power_percent
        data["hkd_state_optics"][ind_b:ind_e] = mon.window_condition

    # fw v1.2 HKD are variables of the monitoring group
    if data["float_fw_version"] >= 1.2:
        # fmt: off
        data["hkd_bkgd_radiance"][ind_b:ind_e] = mon.variables["background_radiance"][:]
        data["hkd_rh_int"][ind_b:ind_e] = mon.variables["internal_humidity"][:]
        data["hkd_temp_int"][ind_b:ind_e] = mon.variables["internal_temperature"][:]
        data["hkd_temp_trans"][ind_b:ind_e] = mon.variables["transmitter_enclosure_temperature"][:]  # noqa
        data["hkd_pres_int"][ind_b:ind_e] = mon.variables["internal_pressure"][:]
        data["hkd_temp_laser"][ind_b:ind_e] = mon.variables["laser_temperature"][:]
        data["hkd_state_laser"][ind_b:ind_e] = mon.variables["laser_power_percent"][:]
        data["hkd_state_optics"][ind_b:ind_e] = mon.variables["window_condition"][:]
        data["hkd_heater_int"][ind_b:ind_e] = mon.variables["internal_heater"][:]
        data["hkd_window_blower"][ind_b:ind_e] = mon.variables["window_blower"][:]
        data["hkd_window_blower_heater"][ind_b:ind_e] = mon.variables["window_blower_heater"][:]  # noqa
        # fmt: on

    # status code variables
    # -------------------------------------------------------------------------
    logger.debug("reading status code variables")
    if data["float_fw_version"] >= 1.2:
        status = nc_id["status"]
        # fmt: off
        data["status_device_controller_temperature"][ind_b:ind_e] = status.variables["Device_controller_temperature"][:]  # noqa
        data["status_device_controller_electronics"][ind_b:ind_e] = status.variables["Device_controller_electronics"][:]  # noqa
        data["status_device_controller_overall"][ind_b:ind_e] = status.variables["Device_controller_overall"][:]  # noqa
        data["status_optics_unit_accelerometer"][ind_b:ind_e] = status.variables["Optics_unit_accelerometer"][:]  # noqa
        data["status_optics_unit_electronics"][ind_b:ind_e] = status.variables["Optics_unit_electronics"][:]  # noqa
        data["status_optics_unit_overall"][ind_b:ind_e] = status.variables["Optics_unit_overall"][:]  # noqa
        data["status_optics_unit_memory"][ind_b:ind_e] = status.variables["Optics_unit_memory"][:]  # noqa
        data["status_optics_unit_tilt_angle"][ind_b:ind_e] = status.variables["Optics_unit_tilt_angle"][:]  # noqa
        data["status_receiver_electronics"][ind_b:ind_e] = status.variables["Receiver_electronics"][:]  # noqa
        data["status_receiver_overall"][ind_b:ind_e] = status.variables["Receiver_overall"][:]  # noqa
        data["status_receiver_memory"][ind_b:ind_e] = status.variables["Receiver_memory"][:]  # noqa
        data["status_receiver_voltage"][ind_b:ind_e] = status.variables["Receiver_voltage"][:]  # noqa
        data["status_receiver_solar_saturation"][ind_b:ind_e] = status.variables["Receiver_solar_saturation"][:]  # noqa
        data["status_receiver_sensitivity"][ind_b:ind_e] = status.variables["Receiver_sensitivity"][:]  # noqa
        data["status_window_blocking"][ind_b:ind_e] = status.variables["Window_condition"][:]  # noqa
        data["status_window_condition"][ind_b:ind_e] = status.variables["Window_condition"][:]  # noqa
        data["status_window_blower_fan"][ind_b:ind_e] = status.variables["Window_blower_fan"][:]  # noqa
        data["status_window_blower_heater"][ind_b:ind_e] = status.variables["Window_blower_heater"][:]  # noqa
        data["status_servo_drive_electronics"][ind_b:ind_e] = status.variables["Servo_drive_electronics"][:]  # noqa
        data["status_servo_drive_overall"][ind_b:ind_e] = status.variables["Servo_drive_overall"][:]  # noqa
        data["status_servo_drive_memory"][ind_b:ind_e] = status.variables["Servo_drive_memory"][:]  # noqa
        data["status_servo_drive_control"][ind_b:ind_e] = status.variables["Servo_drive_control"][:]  # noqa
        data["status_servo_drive_ready"][ind_b:ind_e] = status.variables["Servo_drive_ready"][:]  # noqa
        data["status_transmitter_electronics"][ind_b:ind_e] = status.variables["Transmitter_electronics"][:]  # noqa
        data["status_transmitter_light_source"][ind_b:ind_e] = status.variables["Transmitter_light_source"][:]  # noqa
        data["status_transmitter_light_source_power"][ind_b:ind_e] = status.variables["Transmitter_light_source_power"][:]  # noqa
        data["status_transmitter_overall"][ind_b:ind_e] = status.variables["Transmitter_overall"][:]  # noqa
        data["status_transmitter_light_source_safety"][ind_b:ind_e] = status.variables["Transmitter_light_source_safety"][:]  # noqa
        data["status_transmitter_memory"][ind_b:ind_e] = status.variables["Transmitter_memory"][:]  # noqa
        data["status_maintenance_overall"][ind_b:ind_e] = status.variables["Maintenance_overall"][:]  # noqa
        data["status_device_overall"][ind_b:ind_e] = status.variables["Device_overall"][:]  # noqa
        data["status_recently_started"][ind_b:ind_e] = status.variables["Recently_started"][:]  # noqa
        data["status_measurement_status"][ind_b:ind_e] = status.variables["Measurement_status"][:]  # noqa
        data["status_datacom_overall"][ind_b:ind_e] = status.variables["Datacom_overall"][:]  # noqa
        data["status_measurement_data_destination_not_set"][ind_b:ind_e] = status.variables["Measurement_data_destination_not_set"][:]  # noqa
        data["status_inside_heater"][ind_b:ind_e] = status.variables["Inside_heater"][:]
        data["status_data_generation_status"][ind_b:ind_e] = status.variables["Data_generation_status"][:]  # noqa

        # fmt: on

    return time_size, data


def print_status_message(data, logger):
    """
    Count and print status message with values set to 1.

    Parameters
    ----------
    data : dict
        Dictionary with the data.
    logger : logging.Logger
        Logger object to use to print the messages.

    """
    msg_format = "%s : %d message(s)"

    # loop over keys in data and search the one starting with `status_`
    for var_name in data.keys():
        if var_name.startswith("status_"):
            # count number of values set to 1
            n_status = (data[var_name] == 1).astype(bool).sum()

            if n_status > 0:
                status_name = var_name.replace("status_", "")
                logger.info(msg_format, status_name, n_status)


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
        except (RuntimeError, OSError):
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
            logger.critical("109 Tried to read '%s'. No file could be read", file_)
        sys.exit(1)

    # full backscatter
    data["rcs_0"] = data["rcs_1"] + data["rcs_2"]

    # start time of measurements
    data["start_time"] = data["time"] - dt.timedelta(seconds=int(data["time_resol"]))

    # change of units
    data["hkd_temp_int"] = np.where(
        data["hkd_temp_int"] != MISSING_FLOAT,
        data["hkd_temp_int"] + CELSIUS_TO_KELVIN,
        data["hkd_temp_int"],
    )
    data["hkd_temp_laser"] = np.where(
        data["hkd_temp_laser"] != MISSING_FLOAT,
        data["hkd_temp_laser"] + CELSIUS_TO_KELVIN,
        data["hkd_temp_laser"],
    )

    # force localization if defined in conf file
    if "lat" in conf:
        data["station_lat"] = float(conf["lat"])
    if "lon" in conf:
        data["station_lon"] = float(conf["lon"])
    if "alt" in conf:
        data["station_alt"] = float(conf["alt"])

    # correct problem of missing values for clouds and cover variables
    cbh_filter = (data["cbh"] > 0) & (data["cbh"] < 20000)
    data["cbh"] = np.where(cbh_filter, data["cbh"], MISSING_FLOAT)
    cc_filter = data["cloud_cover"] > 0
    data["cloud_cover"] = np.where(cc_filter, data["cloud_cover"], MISSING_INT)
    cc_filter = data["cloud_layer_cover"] > 0
    data["cloud_layer_cover"] = np.where(
        cc_filter, data["cloud_layer_cover"], MISSING_INT
    )
    cc_filter = data["cloud_layer_height"] > 0
    data["cloud_layer_height"] = np.where(
        cc_filter, data["cloud_layer_height"], MISSING_FLOAT
    )

    # print status (only for fw >= 1.2)
    print_status_message(data, logger)

    return data
