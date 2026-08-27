## v4.0.1 (2026-08-27)

## v4.0.0 (2026-07-27)

### Fix

- **cl61**: fig_detection in CL61

### Refactor

- **pyproject**: remove unneeded (and unusable) gitpython dep
- use uv for tests in CI
- remove hatpro tests
- reorganize pyproject.toml
- **hatpro**: remove conf files
- fix coding style
- reorganize tests
- move ruff configuration to pyproject.toml
- management of version
- **packaging**: reorganize repo to allow packaging of the code

## v3.2.4 (2025-07-01)

## v3.2.3 (2025-07-01)

### Fix

- time error in chm15k reader
- cl61 configuration files
- **ipral**: active channel for brilliant laser
- **ipral**: remove_bckgrd option was not properly parsed
- remove "units" from uninterpretable attributes
- **ipral**: missing f-string
- **ipral**: pr2 calculation
- **ipral**: correct missing f-string

### Refactor

- **ipral**: modernize reader code

## v3.2.2 (2025-02-04)

### Fix

- **vaisala_cl**: harmonize CL61 and CL31/51

## v3.2.1 (2025-01-30)

### Feat

- configuration of cl61
- configuration of CL61

### Fix

- **miniMPL**: correct config file
- ruff errors

## v3.2.0 (2024-07-11)

### Feat

- add option to filter output filter dates
- CHM15k : add 'scaling' factor to L1 files #59
- update dependencies (#61)

### Fix

- ruff detected errors
- ruff toml configuration file
- tests for new arg --filter-day
- unused tests in chm15k
- #63

## v3.1.4 (2022-07-21)

## v3.1.3 (2022-07-19)

- LEOSHERE WLS70
  - improve management of localization of intrument in header
  - default values for lat and lon are now required in conf file
- VAISALA CL61
  - add compatibility with firmware 1.1.x
  - read HouseKeeping Data from `monitoring` group
  - add option in conf file to force localization of instrument

## v3.1.2 (2022-02-22)

- VAISALA CL
  - remove debug print in reader

## v3.1.1 (2022-02-02)

- VAISALA CL
  - make the reader compatible with CL31 from belgium

## v3.1.0 (2022-01-31)

- Update all example configuration files.
- VAISALA CL
  - Correct bug for reading of visibility data
- VAISALA CL61
  - Add reader. Only preliminary version as the file format will change.
- SIGMASPACE MiniMPL
  - Correct total backscatter calculation
- Lufft CHM15k
  - update decoding of warning error message depending on the firmware version
  - Add capacity to read backscatter from `beta_att` variables

## v3.0.5 (2020-09-01)

- VAISALA CL
  - remove unneeded debugging print
- LEOSPHERE WLS70 10s
  - wiper count variable is not read the right way

## v3.0.4 (2020-09-01)

- VAISALA CL
  - correct bug when message line start with `/` (ligne was ignored)
  - try to improve handling of incomplete message

## v3.0.3 (2020-08-10)

- update requirements.txt with more precise packages version
- VAISALA CL
  - improve handling of incomplete messages. The reader won't crash now and skip the message.

## v3.0.2 (2020-06-29)

- hatpro reader
  - improve syncing of brightness and meteo data
- WLS70 10 min reader
  - correct bug when localization is not well formatted

## v3.0.1 (2019-06-11)

- correct a bug converting `units = 1` into an integer attribute. Units are now always interpreted as string.

## v3.0.0 (2019-04-29)

- make raw2l1 compatible with python 3.6 and 3.7
- drop compatibility with python2
- uniformize source code format using black
- correct bugs with readers
- move repository on IN2P3s gitlab
- add continuous integration

## v2.1.19 (2017-08-11)

- SIGMASPACE miniMPL reader
  - correct bug with `laser_energy`. 273.15 was added to the variable by mistake

## v2.1.18 (2017-07-19)

- LUFFT CHM15k readers
  - correct bug when parsing software version for firmware greater equal to 0.747 and add tests

## v2.1.17 (2017-06-27)

- VAISALA CL31 & CL31 readers (swiss airport included)
  - add reading of vertical visibility variable accessible through `vertical_visibility` keyword
- CAMPBELL SCIENTIFIC CS135 reader
  - add reading of vertical visibility variable accessible through `vertical_visibility` keyword
  - add reading of highest signal received variable accessible through `highest_signal_received` keyword

## v2.1.16 (2017-03-27)

- LUFFT CHM15k readers
  - correct calculation of RCS. Doesn't substract background anymore.

## v2.1.15 (2017-03-22)

- leosphere WLS readers
  - readers were not able to concatenate several input files. Only the last one was used.

## v2.1.14 (2017-03-22)

- leosphere WLS70 reader 10s
  - correct bug with `u`, `v`, `x_wind` and `y_wind`
  - same name was used for `u`, `x_wind` and `v`, `y_wind`

## v2.1.13 (2017-03-21)

- netCDF creation module
  - correct bug preventing creation of multidimensional time variables
  - it is now possible to create time_bnds variables require by CF convention when time dependant processing is done on variables
    - for this kind of variable is it still necessary to provide units (which make the file not fully CF compliant)
- leosphere WLS reader
  - add calculation of u and v for each reader from wind_speed and wind_direction
  - update examples of configuration files
  - update tests to check with multiples version of raw data


## v2.1.12 (2017-03-02)

- leosphere WLS reader
  - WLS70 10 min reader correct bug with missing values for cnr_min, cnr_max, ws_min and ws_max

## v2.1.11 (2017-03-01)

- leosphere WLS reader
  - update variables read names for WLS70 10s to make them more readable

## v2.1.10 (2017-03-01)

- leosphere WLS reader
  - add reader for WLS7 1s data and WLS70 10s data
  - update examples of configuration files

## v2.1.9 (2017-01-05)

- netCDF creation module
  - correct bug when creating time variable and calendar attribute is missing
  - correct bug with string in netCDF3_CLASSIC format
- add first version of sigmaspace MiniMPL reader
- add first version of leosphere WLS7v2 and WLS70 reader (wind LIDAR)
  - examples of configuration files are not yet available
- CHM15k reader
  - add possibility to add the path to the overlap TUB*.cfg file in the reader_conf section

## v2.1.8 (2016-11-15)

- chm15k reader
  - add test to check that cho (cloud base offset) is substracted from cbh if available
- cl31 reader
  - correct bug with CBH and CLH. Instead of converting data in feet to meters, coefficient was applied to data in meters
  - add test to check the conversion of data is working
  - the bug was already corrected in reader for swiss airport data

## v2.1.7 (2016-10-25)

- create a reader specifically for CHM15k data from UK metoffice
- correct errors in E-PROFILE configuration files examples

## v2.1.6 (2016-10-24)

- improve managing of time variable in the creation of netCDF file
  - a new type has been added: `$time$`
  - section about time variable are required to have `units` and `calendar` options (compatible with netCDF-CF convention)
  - update all configuration files examples with the new `$time$` type for time variables
- chm15k reader
  - add variable `start_time`
- cl31 reader
  - add variable `start_time`
  - an option `time_resolution` (in seconds) is now required in `[reader_conf]` section
- update E-PROFILE example conf file with the requirements describe in `Raw2L1-L1L2-issues_and_developments` documents

## v2.1.5 (2016-08-12)

- add a new argument `-anc` which allows to give the reader another type of file
- vaisala reader
  - correct bugs detected by MetOffice and add tests
  - change how instruments messages are printed. Instead of doing it for each time step a summary is done at the end of the reading
- chm15k-nimbus reader
  - correct bugs detected by Metoffice and add tests
  - change how instruments messages are printed. Instead of doing it for each time step a summary is done at the end of the reading
  - it is now possible to give to pass the overlap using TUB*.cfg from lufft with -anc command line options. It allows a better checking of the size and could be used during the reading
- RPG hatpro (experimental)
      - add reader for every type of files required by TOPROF

## v2.1.4 (2016-04-12)

- correct minor bug in test

## v3.1.3

- correct minor bugs in vaisala reader
  - problem reading CBH when full obscuration is determine
  - problem reading files when message type change in a file
  - problem reading file when an error occure during conversion of hexadecimal string to integers

## v2.1.0 (2016-03-03)

- change logger message to make them compatible with eprofile
- create conf file for eprofile. Compare to TOPROF version, only the global variable are changed
- allow user to chose the value of missing value in the reader configuration file. It needs to be taken into account in the data reader
- add options to check size and timeliness of input files and data
- add possibility to give several input files or pattern as argument in the command line
- a value from the reader can now be put in a netCDf attribute
- correct the bug making it impossible to have a different level of logs in the console and in the file
- correct minor bugs creating the logging of warnings
- vaisala reader
  - add a modified version of the reader to process swiss airports files
  - add decoding of instrument message. They are printed in the log during processing in any found
  - if instruments is set in feets value in converted into meters automatically
  - check scale value. data without a scale of 100% will be logged
  - correct a bug making the the tilt angle a scalar value instead of a time depending variable
- chm15k-nimbus
  - make the reader compatible with macehead data (They seem to have a really old version. Some variables are filled with missing values).
  - instruments messages/alerts available in the file are logged with their meaning
  - correct a bug concerning the reading of p_calc value
- RPG hatpro (experimental)
    - add reader to convert data into TOPROF format. All HATPRO output files are not taken into account

## v2.0.7 (2015-10-18)

- add CHANGELOG, LICENSE, requirements.txt files
- update README
- add example input files into the repository
- correct bug in case vaisala raw file contains newline caracter at the start of the line
- first stable version after intensive testing during ceilinex campaign

## v2.0.6b (2015-10-15)

- correct bug in campbell reader creating an infinite loop when the timestamp is not just the line after the first message

## v2.0.5b (2015-07-10)

- add option to use compression with netCDF4 file format
- correct bug in one lufft CHM15k test preventing it from being run
- first test with CS135 to integrate string variables. Only works with netCDF4 files

## v2.0.4b (2015-07-09)

- improve reader robustness of header reading for vaisala and cambell scientific readers

## v2.0.2b (2015-07-09)

- correct problem when chosing a different log file than the default one
- add TOPROF configuration files for lufft CHM15K-NIMBUS and vaisala CL31 and CL51
  - add reader for Campbell Scientific CS135
  - correct problem with vaisala and campbell HEXA profile decoding


