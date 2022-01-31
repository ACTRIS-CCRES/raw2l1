[![pipeline status](https://gitlab.in2p3.fr/ipsl/sirta/raw2l1/badges/master/pipeline.svg)](https://gitlab.in2p3.fr/ipsl/sirta/raw2l1/commits/master) [![coverage report](https://gitlab.in2p3.fr/ipsl/sirta/raw2l1/badges/master/coverage.svg)](https://gitlab.in2p3.fr/ipsl/sirta/raw2l1/commits/master)

# raw2l1

Code to convert raw LIDAR data into normalized netCDF files

## required python modules

see requirements.txt file
conf_vaisala_cl31_eprofile.ini
## instrument compatibility

- VAISALA CL31 and CL51 using clview acquisition software. If you are using your own acquisition softare, you may need to make some change to the reader
- VAISALA CL61
- JENOPTIK/LUFFT CHM15k
- CAMPBELL SCIENTIFIC CS135

## how to run

the repository contains some example files allowing you to test the code

- go to raw2l1 directory
- modify the configuration file example to comply with your instrument/station
  - The fields to change are identified by the tag `[to_change]`
- you can get the list of input arguments using the command:

```
python raw2l1.py -h
```


- to convert a LUFFT CHM15k file

```
python '20150427' raw2l1 conf/conf_lufft_chm15k_eprofile.ini test/input/Jenoptik_chm15k/20150427_SIRTA_CHM150101_000.nc test/output/test_lufft_sirta.nc
```

- to convert a VAISALA CL31 or CL51 file

```
 python raw2l1 '20141030' conf/conf_vaisala_cl31_eprofile.ini 'test/input/vaisala_cl31/cl31_0a_z1R5mF3s_v01_20141030_*.asc' test/output/test_cl31.nc
```

# realtime production

Options are available for the use of raw2l1 in near-realtime processing

- ```-file_min_size```: allow to define the minimum size of input file in bytes. Files with a smaller size will be rejected.
- ```-file_max_age```: allow to define the maximum age of data in a file in hours
- ```--check_timeliness```: check if the data read are not to old or in the future. By default it checks thats data have a maximum age of 2 hours. This value can be changed with option ```-file_max_age```

# run the test suite

To run the tests you will need more python modules see requirements.txt file

- go to raw2l1 directory
- run

```
pytest
```

# thanks

This program was developped in the scope of [TOPROF](http://www.toprof.imaa.cnr.it/) (COST ACTION ES1303).
Thanks to F.Wagner, I. Mattis, R. Leinweber for testing the software, providing example files and reporting bugs during the [CEILINEX](http://ceilinex2015.de)

# authors

M.-A Drouin based on the first version of Y. Morille

# Copyright

2014-2022 CNRS/Ecole polytechnique
