# raw2l1 configuration sections
CONF_SECTIONS = ["conf", "reader_conf", "global"]

# netCDF special processing sections
SPEC_SECTIONS = []

# Reserved attributes
RESERV_ATTR = ["name", "dim", "value", "type", "value", "size", "_FillValue"]

STRING_ATTR = [
    "units",
    "comments",
    "long_name",
    "standard_name",
    "comment",
    "flag_values",
]

CONF_OPTIONS = ["reader_dir", "reader", "netcdf_format"]

# authorized netCDF format
ALLOW_NC_FMT = ["NETCDF3_CLASSIC", "NETCDF4"]
ALLOW_NC4_COMP = ["true", "false"]
ALLOW_NC4_COMP_LEVEL = list(range(1, 10))

# Default value for missing and _FillValue if not define in reader_conf section
MISSING_FLOAT = -999.0
MISSING_INTEGER = -9
