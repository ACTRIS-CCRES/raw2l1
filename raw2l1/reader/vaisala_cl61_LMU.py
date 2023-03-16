"""Raw2l1 reader for VAISALA CL61 ceilometers netCDF files."""
import datetime as dt
import sys

import netCDF4 as nc
import numpy as np

# brand and model of the LIDAR
BRAND = "vaisala"
MODEL = "CL61"

# missing values
MISSING_INT = -99
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

    fw_version = nc_id.sw_version
    logger.debug("firmware version: %s", fw_version)

    # fw version can be x.x.x or x.x.x-rcx for first versions
    fl_fw_version = float(".".join(fw_version.split("-")[0].split(".")[0:2]))

    return fw_version, fl_fw_version

def convert_str_to_int(array):
    '''
    Convert status strings to integer to be compatible between fw 1.1.0 and 1.2.7
    '''
    int_array = np.zeros(len(array))
    conversion_dict = {'0' : 0, 'I': 1, 'W': 2, 'A': 3}
    for i in range(len(array)):
        int_array[i] = conversion_dict[array[i]]
        
    return int_array.astype(int)

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
    # dimensions
    # ------------------------------------------------------------------------
    data["time"] = np.ones(dims["time"], dtype=np.dtype(dt.datetime))
    data["layer"] = np.ones(dims["layer"], dtype=np.uint8)
    data["range"] = np.ones(dims["range"], dtype=np.float64)

    # time dependant variables
    # ------------------------------------------------------------------------
    data["vertical_visibility"] = np.ones((dims["time"],), dtype="f4") * MISSING_FLOAT
    data["fog_detection"] = np.ones((dims["time"],), dtype=np.int16) * MISSING_INT
    data["precipitation_detection"] = np.ones((dims["time"],), dtype=np.int16) * MISSING_INT
    data["receiver_gain"] = np.ones((dims["time"],), dtype=np.int16) * MISSING_INT
    data["beta_sum"] = np.ones((dims["time"],), dtype="f4") * MISSING_FLOAT
    data["beta_noise"] = np.ones((dims["time"],), dtype="f4") * MISSING_FLOAT
    data["lat"] = np.ones((dims["time"],), dtype="f4") * MISSING_FLOAT
    data["lon"] = np.ones((dims["time"],), dtype="f4") * MISSING_FLOAT
    data["alt"] = np.ones((dims["time"],), dtype="f4") * MISSING_FLOAT
    data["tilt_angle"] = np.ones((dims["time"],), dtype="f4") * MISSING_FLOAT
    data["tilt_angle_correction"] = np.ones((dims["time"],), dtype=np.int16) * MISSING_INT
    data["cloud_cover"] = np.ones((dims["time"]), dtype=np.int32) * MISSING_INT
    
    # range dependent variables
    # -------------------------------------------------------------------------
    data["overlap_function"] = np.ones((dims["range"],), dtype="f4") * MISSING_FLOAT

    # Time, layer dependant variables
    # -------------------------------------------------------------------------
    data["cbh"] = np.ones((dims["time"], dims["layer"]), dtype=np.float32) * MISSING_FLOAT
    data["cloud_penetration_depth"] = np.ones((dims["time"], dims["layer"]), dtype=np.int32) * MISSING_INT
    data["cloud_thickness"] = np.ones((dims["time"], dims["layer"]), dtype=np.int32) * MISSING_INT
    # starting fw 1.1.x
    data["cloud_layer_cover"] = np.ones((dims["time"], dims["layer"]), dtype=np.int32) * MISSING_INT
    data["cloud_layer_height"] = (
        np.ones((dims["time"], dims["layer"]), dtype=np.float32) * MISSING_FLOAT
    )

    # Time, range dependent variables
    # -------------------------------------------------------------------------
    data["rcs_0"] = np.ones((dims["time"], dims["range"]), dtype=np.float32) * MISSING_FLOAT
    data["rcs_1"] = np.ones((dims["time"], dims["range"]), dtype=np.float32) * MISSING_FLOAT
    data["rcs_2"] = np.ones((dims["time"], dims["range"]), dtype=np.float32) * MISSING_FLOAT
    data["beta"] = np.ones((dims["time"], dims["range"]), dtype=np.float32) * MISSING_FLOAT
    data["volume_ldr"] = np.ones((dims["time"], dims["range"]), dtype=np.float32) * MISSING_FLOAT

    # house keeping data variables
    # -------------------------------------------------------------------------
    data["hkd_rh_int"] = np.ones((dims["time"],), dtype="f4") * MISSING_FLOAT
    data["hkd_temp_int"] = np.ones((dims["time"],), dtype="f4") * MISSING_FLOAT
    data["hkd_temp_trans"] = np.ones((dims["time"],), dtype="f4") * MISSING_FLOAT
    data["hkd_pres_int"] = np.ones((dims["time"],), dtype="f4") * MISSING_FLOAT
    data["hkd_temp_laser"] = np.ones((dims["time"],), dtype="f4") * MISSING_FLOAT
    data["hkd_state_laser"] = np.ones((dims["time"],), dtype="f4") * MISSING_FLOAT
    data["hkd_state_optics"] = np.ones((dims["time"],), dtype="f4") * MISSING_FLOAT
    data["hkd_bkgd_radiance"] = np.ones((dims["time"],), dtype="f4") * MISSING_FLOAT
    data["hkd_heater_int"] = np.ones((dims["time"],), dtype=np.int16) * MISSING_INT
    data["hkd_window_blower"] = np.ones((dims["time"],), dtype=np.int16) * MISSING_INT
    data["hkd_window_blower_heater"] = np.ones((dims["time"],), dtype=np.int16) * MISSING_INT

    # Status variables (string)
    # -------------------------------------------------------------------------
    data["status_inside_heater"] = np.ones((dims["time"],), dtype=np.int16) * MISSING_INT
    data["status_window_blower_fan"] = np.ones((dims["time"],), dtype=np.int16) * MISSING_INT
    data["status_window_blower_heater"] = np.ones((dims["time"],), dtype=np.int16) * MISSING_INT
    # data["status_window_blower_temperature_sensor"] = np.ones((dims["time"],), dtype=np.int16) * MISSING_INT
    data["status_device_controller_temperature"] = np.ones((dims["time"],), dtype=np.int16) * MISSING_INT
    data["status_device_controller_electronics"] = np.ones((dims["time"],), dtype=np.int16) * MISSING_INT
    # data["status_device_controller_voltage"] = np.ones((dims["time"],), dtype=np.int16) * MISSING_INT
    data["status_device_controller_overall"] = np.ones((dims["time"],), dtype=np.int16) * MISSING_INT
    data["status_optics_unit_accelerometer"] = np.ones((dims["time"],), dtype=np.int16) * MISSING_INT
    data["status_optics_unit_electronics"] = np.ones((dims["time"],), dtype=np.int16) * MISSING_INT
    # data["status_optics_unit_environmental_sensor"] = np.ones((dims["time"],), dtype=np.int16) * MISSING_INT
    data["status_optics_unit_overall"] = np.ones((dims["time"],), dtype=np.int16) * MISSING_INT
    data["status_optics_unit_memory"] = np.ones((dims["time"],), dtype=np.int16) * MISSING_INT
    data["status_optics_unit_tilt_angle"] = np.ones((dims["time"],), dtype=np.int16) * MISSING_INT
    data["status_receiver_electronics"] = np.ones((dims["time"],), dtype=np.int16) * MISSING_INT
    data["status_receiver_overall"] = np.ones((dims["time"],), dtype=np.int16) * MISSING_INT
    data["status_receiver_memory"] = np.ones((dims["time"],), dtype=np.int16) * MISSING_INT
    data["status_receiver_solar_saturation"] = np.ones((dims["time"],), dtype=np.int16) * MISSING_INT
    data["status_receiver_sensitivity"] = np.ones((dims["time"],), dtype=np.int16) * MISSING_INT
    data["status_receiver_voltage"] = np.ones((dims["time"],), dtype=np.int16) * MISSING_INT
    data["status_window_blocking"] = np.ones((dims["time"],), dtype=np.int16) * MISSING_INT
    data["status_window_condition"] = np.ones((dims["time"],), dtype=np.int16) * MISSING_INT
    data["status_servo_drive_control"] = np.ones((dims["time"],), dtype=np.int16) * MISSING_INT
    data["status_servo_drive_electronics"] = np.ones((dims["time"],), dtype=np.int16) * MISSING_INT
    data["status_servo_drive_overall"] = np.ones((dims["time"],), dtype=np.int16) * MISSING_INT
    data["status_servo_drive_memory"] = np.ones((dims["time"],), dtype=np.int16) * MISSING_INT
    data["status_servo_drive_ready"] = np.ones((dims["time"],), dtype=np.int16) * MISSING_INT
    data["status_transmitter_electronics"] = np.ones((dims["time"],), dtype=np.int16) * MISSING_INT
    data["status_transmitter_light_source"] = np.ones((dims["time"],), dtype=np.int16) * MISSING_INT
    data["status_transmitter_light_source_power"] = np.ones((dims["time"],), dtype=np.int16) * MISSING_INT
    data["status_transmitter_light_source_safety"] = np.ones((dims["time"],), dtype=np.int16) * MISSING_INT
    data["status_transmitter_overall"] = np.ones((dims["time"],), dtype=np.int16) * MISSING_INT
    data["status_transmitter_memory"] = np.ones((dims["time"],), dtype=np.int16) * MISSING_INT
    # data["status_transmitter_voltage"] = np.ones((dims["time"],), dtype=np.int16) * MISSING_INT
    # data["status_hardware_overall"] = np.ones((dims["time"],), dtype=np.int16) * MISSING_INT
    data["status_maintenance_overall"] = np.ones((dims["time"],), dtype=np.int16) * MISSING_INT
    data["status_device_overall"] = np.ones((dims["time"],), dtype=np.int16) * MISSING_INT
    data["status_recently_started"] = np.ones((dims["time"],), dtype=np.int16) * MISSING_INT
    data["status_measurement_status"] = np.ones((dims["time"],), dtype=np.int16) * MISSING_INT
    data["status_datacom_overall"] = np.ones((dims["time"],), dtype=np.int16) * MISSING_INT
    data["status_data_generation_status"] = np.ones((dims["time"],), dtype=np.int16) * MISSING_INT
    # data["status_data_sending_status"] = np.ones((dims["time"],), dtype=np.int16) * MISSING_INT
    data["status_measurement_data_destination_not_set"] = np.ones((dims["time"],), dtype=np.int16) * MISSING_INT

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
    data["station_lat"] = nc_id.variables["latitude"][:]
    data["station_lon"] = nc_id.variables["longitude"][:]
    data["station_alt"] = nc_id.variables["elevation"][:]

    # time resolution (has to be converted from global attributes)
    if data["float_fw_version"] <= 1.1:
        data["time_resol"] = nc_id.getncattr("time between consecutive profiles in seconds")
        data["range_resol"] = np.mean(data["range"][1:] - data["range"][:-1])
    elif data["float_fw_version"] >= 1.2:
        data["time_resol"] = nc_id.profile_interval_in_seconds
        data["range_resol"] = nc_id.variables["range_resolution"][:]

    # instrument informations
    if data["float_fw_version"] <= 1.1:
        data["instrument_id"] = 'U4850794'
        data["azimuth_angle"] = MISSING_FLOAT
        data["cloud_calibration_factor"] = MISSING_FLOAT
        data["cloud_calibration_factor_user"] = MISSING_FLOAT
    elif data["float_fw_version"] >= 1.2:
        data["cloud_calibration_factor"] = nc_id.variables['cloud_calibration_factor'][:]
        data["cloud_calibration_factor_user"] = nc_id.variables['cloud_calibration_factor_user'][:]
        data["azimuth_angle"] = nc_id.variables['azimuth_angle'][:]
        data["instrument_id"] = nc_id.instrument_serial_number
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
    logger.debug("processing timesteps %s to %s", data["time"][ind_b], data["time"][ind_e - 1])

    # time dependant variables variables
    # ------------------------------------------------------------------------
    data["vertical_visibility"][ind_b:ind_e] = nc_id.variables["vertical_visibility"][:]
    if data["float_fw_version"] >= 1.2:
        data["fog_detection"][ind_b:ind_e] = nc_id.variables["fog_detection"][:]
        data["precipitation_detection"][ind_b:ind_e] = nc_id.variables["precipitation_detection"][:]
        data["receiver_gain"][ind_b:ind_e] = nc_id.variables["receiver_gain"][:]
    data["beta_sum"][ind_b:ind_e] = nc_id.variables["beta_att_sum"][:]
    data["beta_noise"][ind_b:ind_e] = nc_id.variables["beta_att_noise_level"][:]
    # data["lat"][ind_b:ind_e] = nc_id.variables["latitude"][:]
    # data["lon"][ind_b:ind_e] = nc_id.variables["longitude"][:]
    # data["alt"][ind_b:ind_e] = nc_id.variables["elevation"][:]
    if data["float_fw_version"] >= 1.1:
        data["cloud_cover"][ind_b:ind_e] = nc_id.variables["sky_condition_total_cloud_cover"][:]
        data["tilt_angle"][ind_b:ind_e] = nc_id.variables["tilt_angle"][:]
        data["tilt_angle_correction"][ind_b:ind_e] = nc_id.variables["tilt_correction"][:]

    # Time, layer dependant variables
    # -------------------------------------------------------------------------
    data["cbh"][ind_b:ind_e, :] = nc_id.variables["cloud_base_heights"][:]
    
    if data["float_fw_version"] >= 1.1:
        data["cloud_layer_cover"][ind_b:ind_e, :] = nc_id.variables[
            "sky_condition_cloud_layer_covers"
        ][:]
        data["cloud_layer_height"][ind_b:ind_e, :] = nc_id.variables[
            "sky_condition_cloud_layer_heights"
        ][:]
    if data["float_fw_version"] >= 1.2:
        data["cloud_penetration_depth"][ind_b:ind_e, :] = nc_id.variables[
            "cloud_penetration_depth"
        ][:]
        data["cloud_thickness"][ind_b:ind_e, :] = nc_id.variables[
            "cloud_thickness"
        ][:]

    # Time, range dependent variables
    # -------------------------------------------------------------------------
    data["rcs_1"][ind_b:ind_e, :] = nc_id.variables["p_pol"][:]
    data["rcs_2"][ind_b:ind_e, :] = nc_id.variables["x_pol"][:]
    data["beta"][ind_b:ind_e, :] = nc_id.variables["beta_att"][:]
    data["volume_ldr"][ind_b:ind_e, :] = nc_id.variables["linear_depol_ratio"][:]

    # house keeping data variables
    # -------------------------------------------------------------------------
    # only available for firmware >= 1.1
    logger.debug("reading house keeping data")
    if data["float_fw_version"] == 1.1:
        data["hkd_bkgd_radiance"][ind_b:ind_e] = nc_id.variables["hkd_background_radiance"][:]
        data["hkd_rh_int"][ind_b:ind_e] = nc_id.variables["hkd_internal_humidity"][:]
        data["hkd_temp_int"][ind_b:ind_e] = nc_id.variables["hkd_internal_temperature"][:]
        data["hkd_pres_int"][ind_b:ind_e] = nc_id.variables["hkd_internal_pressure"][:]
        data["hkd_temp_laser"][ind_b:ind_e] = nc_id.variables["hkd_laser_temperature"][:]
        data["hkd_state_laser"][ind_b:ind_e] = nc_id.variables["hkd_laser_power_percent"][:]
        data["hkd_state_optics"][ind_b:ind_e] = nc_id.variables["hkd_window_condition"][:]
    if data["float_fw_version"] >= 1.2:
        data["hkd_bkgd_radiance"][ind_b:ind_e] = nc_id['monitoring'].variables["background_radiance"][:]
        data["hkd_rh_int"][ind_b:ind_e] = nc_id['monitoring'].variables["internal_humidity"][:]
        data["hkd_temp_int"][ind_b:ind_e] = nc_id['monitoring'].variables["internal_temperature"][:]
        data["hkd_temp_trans"][ind_b:ind_e] = nc_id['monitoring'].variables["transmitter_enclosure_temperature"][:]
        data["hkd_pres_int"][ind_b:ind_e] = nc_id['monitoring'].variables["internal_pressure"][:]
        data["hkd_temp_laser"][ind_b:ind_e] = nc_id['monitoring'].variables["laser_temperature"][:]
        data["hkd_state_laser"][ind_b:ind_e] = nc_id['monitoring'].variables["laser_power_percent"][:]
        data["hkd_state_optics"][ind_b:ind_e] = nc_id['monitoring'].variables["window_condition"][:]
        data["hkd_heater_int"][ind_b:ind_e] = nc_id['monitoring'].variables["internal_heater"][:]
        data["hkd_window_blower"][ind_b:ind_e] = nc_id['monitoring'].variables["window_blower"][:]
        data["hkd_window_blower_heater"][ind_b:ind_e] = nc_id['monitoring'].variables["window_blower_heater"][:]

    # status code variables
    # -------------------------------------------------------------------------
    logger.debug("reading status code variables")
    if data["float_fw_version"] == 1.1:
        data["status_inside_heater"][ind_b:ind_e] = convert_str_to_int(nc_id.variables["status_inside_heater"][:])
        data["status_window_blower_fan"][ind_b:ind_e] = convert_str_to_int(nc_id.variables["status_window_blower_fan"][:])
        data["status_window_blower_heater"][ind_b:ind_e] = convert_str_to_int(nc_id.variables[
            "status_window_blower_heater"
        ][:])
        # data["status_window_blower_temperature_sensor"][ind_b:ind_e] = convert_str_to_int(nc_id.variables[
        #     "status_window_blower_temperature_sensor"
        # ][:])
        data["status_device_controller_temperature"][ind_b:ind_e] = convert_str_to_int(nc_id.variables[
            "status_device_controller_temperature"
        ][:])
        data["status_device_controller_electronics"][ind_b:ind_e] = convert_str_to_int(nc_id.variables[
            "status_device_controller_electronics"
        ][:])
        # data["status_device_controller_voltage"][ind_b:ind_e] = convert_str_to_int(nc_id.variables[
        #     "status_device_controller_voltage"
        # ][:])
        data["status_device_controller_overall"][ind_b:ind_e] = convert_str_to_int(nc_id.variables[
            "status_device_controller_overall"
        ][:])
        data["status_optics_unit_accelerometer"][ind_b:ind_e] = convert_str_to_int(nc_id.variables[
            "status_optics_unit_accelerometer"
        ][:])
        data["status_optics_unit_electronics"][ind_b:ind_e] = convert_str_to_int(nc_id.variables[
            "status_optics_unit_electronics"
        ][:])
        # data["status_optics_unit_environmental_sensor"][ind_b:ind_e] = convert_str_to_int(nc_id.variables[
        #     "status_optics_unit_environmental_sensor"
        # ][:])
        data["status_optics_unit_overall"][ind_b:ind_e] = convert_str_to_int(nc_id.variables["status_optics_unit_overall"][
            :
        ])
        data["status_optics_unit_memory"][ind_b:ind_e] = convert_str_to_int(nc_id.variables["status_optics_unit_memory"][:])
        data["status_optics_unit_tilt_angle"][ind_b:ind_e] = convert_str_to_int(nc_id.variables[
            "status_optics_unit_tilt_angle"
        ][:])
        data["status_receiver_electronics"][ind_b:ind_e] = convert_str_to_int(nc_id.variables[
            "status_receiver_electronics"
        ][:])
        data["status_receiver_overall"][ind_b:ind_e] = convert_str_to_int(nc_id.variables["status_receiver_overall"][:])
        data["status_receiver_memory"][ind_b:ind_e] = convert_str_to_int(nc_id.variables["status_receiver_memory"][:])
        data["status_receiver_solar_saturation"][ind_b:ind_e] = convert_str_to_int(nc_id.variables[
            "status_receiver_solar_saturation"
        ][:])
        data["status_receiver_voltage"][ind_b:ind_e] = convert_str_to_int(nc_id.variables["status_receiver_voltage"][:])
        data["status_window_blocking"][ind_b:ind_e] = convert_str_to_int(nc_id.variables["status_window_blocking"][:])
        data["status_window_condition"][ind_b:ind_e] = convert_str_to_int(nc_id.variables["status_window_condition"][:])
        data["status_servo_drive_control"][ind_b:ind_e] = convert_str_to_int(nc_id.variables["status_servo_drive_control"][
            :
        ])
        data["status_servo_drive_electronics"][ind_b:ind_e] = convert_str_to_int(nc_id.variables[
            "status_servo_drive_electronics"
        ][:])
        data["status_servo_drive_overall"][ind_b:ind_e] = convert_str_to_int(nc_id.variables["status_servo_drive_overall"][
            :
        ])
        data["status_servo_drive_memory"][ind_b:ind_e] = convert_str_to_int(nc_id.variables["status_servo_drive_memory"][:])
        data["status_servo_drive_ready"][ind_b:ind_e] = convert_str_to_int(nc_id.variables["status_servo_drive_ready"][:])
        data["status_transmitter_electronics"][ind_b:ind_e] = convert_str_to_int(nc_id.variables[
            "status_transmitter_electronics"
        ][:])
        data["status_transmitter_light_source"][ind_b:ind_e] = convert_str_to_int(nc_id.variables[
            "status_transmitter_light_source"
        ][:])
        data["status_transmitter_light_source_power"][ind_b:ind_e] = convert_str_to_int(nc_id.variables[
            "status_transmitter_light_source_power"
        ][:])
        data["status_transmitter_light_source_safety"][ind_b:ind_e] = convert_str_to_int(nc_id.variables[
            "status_transmitter_light_source_safety"
        ][:])
        data["status_transmitter_overall"][ind_b:ind_e] = convert_str_to_int(nc_id.variables["status_transmitter_overall"][
            :
        ])
        data["status_transmitter_memory"][ind_b:ind_e] = convert_str_to_int(nc_id.variables["status_transmitter_memory"][:])
        # data["status_transmitter_voltage"][ind_b:ind_e] = convert_str_to_int(nc_id.variables["status_transmitter_voltage"][
        #     :
        # ])
        # data["status_hardware_overall"][ind_b:ind_e] = convert_str_to_int(nc_id.variables["status_hardware_overall"][:])
        data["status_maintenance_overall"][ind_b:ind_e] = convert_str_to_int(nc_id.variables["status_maintenance_overall"][
            :
        ])
        data["status_device_overall"][ind_b:ind_e] = convert_str_to_int(nc_id.variables["status_device_overall"][:])
        data["status_recently_started"][ind_b:ind_e] = convert_str_to_int(nc_id.variables["status_recently_started"][:])
        data["status_measurement_status"][ind_b:ind_e] = convert_str_to_int(nc_id.variables["status_measurement_status"][:])
        data["status_datacom_overall"][ind_b:ind_e] = convert_str_to_int(nc_id.variables["status_datacom_overall"][:])
        data["status_data_generation_status"][ind_b:ind_e] = convert_str_to_int(nc_id.variables[
            "status_data_generation_status"
        ][:])
        # data["status_data_sending_status"][ind_b:ind_e] = convert_str_to_int(nc_id.variables["status_data_sending_status"][
        #     :
        # ])
        data["status_measurement_data_destination_not_set"][ind_b:ind_e] = convert_str_to_int(nc_id.variables[
            "status_measurement_data_destination_not_set"
        ][:])
    
    if data["float_fw_version"] >= 1.2:
        data["status_inside_heater"][ind_b:ind_e] = nc_id['status'].variables["Inside_heater"][:]
        data["status_window_blower_fan"][ind_b:ind_e] = nc_id['status'].variables["Window_blower_fan"][:]
        data["status_window_blower_heater"][ind_b:ind_e] = nc_id['status'].variables[
            "Window_blower_heater"
        ][:]
        data["status_device_controller_temperature"][ind_b:ind_e] = nc_id['status'].variables[
            "Device_controller_temperature"
        ][:]
        data["status_device_controller_electronics"][ind_b:ind_e] = nc_id['status'].variables[
            "Device_controller_electronics"
        ][:]
        data["status_device_controller_overall"][ind_b:ind_e] = nc_id['status'].variables[
            "Device_controller_overall"
        ][:]
        data["status_optics_unit_accelerometer"][ind_b:ind_e] = nc_id['status'].variables[
            "Optics_unit_accelerometer"
        ][:]
        data["status_optics_unit_electronics"][ind_b:ind_e] = nc_id['status'].variables[
            "Optics_unit_electronics"
        ][:]
        data["status_optics_unit_overall"][ind_b:ind_e] = nc_id['status'].variables["Optics_unit_overall"][
            :
        ]
        data["status_optics_unit_memory"][ind_b:ind_e] = nc_id['status'].variables["Optics_unit_memory"][:]
        data["status_optics_unit_tilt_angle"][ind_b:ind_e] = nc_id['status'].variables[
            "Optics_unit_tilt_angle"
        ][:]
        data["status_receiver_electronics"][ind_b:ind_e] = nc_id['status'].variables[
            "Receiver_electronics"
        ][:]
        data["status_receiver_overall"][ind_b:ind_e] = nc_id['status'].variables["Receiver_overall"][:]
        data["status_receiver_memory"][ind_b:ind_e] = nc_id['status'].variables["Receiver_memory"][:]
        data["status_receiver_solar_saturation"][ind_b:ind_e] = nc_id['status'].variables[
            "Receiver_solar_saturation"
        ][:]
        data["status_receiver_sensitivity"][ind_b:ind_e] = nc_id['status'].variables["Receiver_sensitivity"][:]
        data["status_receiver_voltage"][ind_b:ind_e] = nc_id['status'].variables["Receiver_voltage"][:]
        data["status_window_blocking"][ind_b:ind_e] = nc_id['status'].variables["Window_blocking"][:]
        data["status_window_condition"][ind_b:ind_e] = nc_id['status'].variables["Window_condition"][:]
        data["status_servo_drive_control"][ind_b:ind_e] = nc_id['status'].variables["Servo_drive_control"][
            :
        ]
        data["status_servo_drive_electronics"][ind_b:ind_e] = nc_id['status'].variables[
            "Servo_drive_electronics"
        ][:]
        data["status_servo_drive_overall"][ind_b:ind_e] = nc_id['status'].variables["Servo_drive_overall"][
            :
        ]
        data["status_servo_drive_memory"][ind_b:ind_e] = nc_id['status'].variables["Servo_drive_memory"][:]
        data["status_servo_drive_ready"][ind_b:ind_e] = nc_id['status'].variables["Servo_drive_ready"][:]
        data["status_transmitter_electronics"][ind_b:ind_e] = nc_id['status'].variables[
            "Transmitter_electronics"
        ][:]
        data["status_transmitter_light_source"][ind_b:ind_e] = nc_id['status'].variables[
            "Transmitter_light_source"
        ][:]
        data["status_transmitter_light_source_power"][ind_b:ind_e] = nc_id['status'].variables[
            "Transmitter_light_source_power"
        ][:]
        data["status_transmitter_light_source_safety"][ind_b:ind_e] = nc_id['status'].variables[
            "Transmitter_light_source_safety"
        ][:]
        data["status_transmitter_overall"][ind_b:ind_e] = nc_id['status'].variables["Transmitter_overall"][
            :
        ]
        data["status_transmitter_memory"][ind_b:ind_e] = nc_id['status'].variables["Transmitter_memory"][:]
        data["status_maintenance_overall"][ind_b:ind_e] = nc_id['status'].variables["Maintenance_overall"][
            :
        ]
        data["status_device_overall"][ind_b:ind_e] = nc_id['status'].variables["Device_overall"][:]
        data["status_recently_started"][ind_b:ind_e] = nc_id['status'].variables["Recently_started"][:]
        data["status_measurement_status"][ind_b:ind_e] = nc_id['status'].variables["Measurement_status"][:]
        data["status_datacom_overall"][ind_b:ind_e] = nc_id['status'].variables["Datacom_overall"][:]
        data["status_data_generation_status"][ind_b:ind_e] = nc_id['status'].variables[
            "Data_generation_status"
        ][:]
        data["status_measurement_data_destination_not_set"][ind_b:ind_e] = nc_id['status'].variables[
            "Measurement_data_destination_not_set"
        ][:]

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
            data["fw_version"], data["float_fw_version"] = get_fw_version(raw_data, logger)

            # read dimensions
            # ----------------------------------------------------------------
            logger.info("reading dimension variables")
            data = read_limited_dims(data, raw_data, logger)

            # read scalar
            # ----------------------------------------------------------------
            logger.info("reading scalar variables")
            data = read_scalar_vars(data, raw_data, logger)
            
            # overlap function
            if data["float_fw_version"] >= 1.2:
                data['overlap_function'] = raw_data.variables['overlap_function'][:]

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
            logger.critical("109 Tried to read '{}'. No file could be read".format(file_))
        sys.exit(1)

    # full backscatter
    data["rcs_0"] = data["rcs_1"] + data["rcs_2"]

    # start time of measurements
    data["start_time"] = data["time"] - dt.timedelta(seconds=int(data["time_resol"]))
      
    # # overlap function
    # data['overlap_function'] = raw_data

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
    data["hkd_temp_trans"] = np.where(
        data["hkd_temp_trans"] != MISSING_FLOAT,
        data["hkd_temp_trans"] + CELSIUS_TO_KELVIN,
        data["hkd_temp_trans"],
    )

    # force localization if defined in conf file
    if "lat" in conf:
        data["station_lat"] = float(conf["lat"])
    if "lon" in conf:
        data["station_lon"] = float(conf["lon"])
    if "alt" in conf:
        data["station_alt"] = float(conf["alt"])

    # set site location if not yet in comments attribute
    if data["site_location"] == "":
        data["site_location"] = conf["site_location"]

    # correct problem of missing values for clouds and cover variables
    cbh_filter = (data["cbh"] > 0) & (data["cbh"] < 20000)
    data["cbh"] = np.where(cbh_filter, data["cbh"], MISSING_FLOAT)
    cc_filter = data["cloud_cover"] > 0
    data["cloud_cover"] = np.where(cc_filter, data["cloud_cover"], MISSING_INT)
    cc_filter = data["cloud_layer_cover"] > 0
    data["cloud_layer_cover"] = np.where(cc_filter, data["cloud_layer_cover"], MISSING_INT)
    cc_filter = data["cloud_layer_height"] > 0
    data["cloud_layer_height"] = np.where(cc_filter, data["cloud_layer_height"], MISSING_FLOAT)

    return data
