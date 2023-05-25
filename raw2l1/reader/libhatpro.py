def correct_time_units(s):
    """correct the wrong format of time units of RPG into a compatible with
    CF convention and num2date and date2num netCDF4 modules
    RPG time unit format: seconds since 1.1.2001, 00:00:00
    in CF it should be seconds since 2001-01-91 00:00:00
    """

    import re

    date_fmt = "{} {} {:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}"

    unit, since, month, day, year, hours, minutes, seconds = re.split(r"[,.:\s]\s*", s)

    return date_fmt.format(
        unit,
        since,
        int(year),
        int(month),
        int(day),
        int(hours),
        int(minutes),
        int(seconds),
    )
