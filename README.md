# raw2l1

Code to convert raw LIDAR data into normalized netCDF files

## required python modules

see requirements.txt file

## instrument compatibility

- VAISALA CL31 and CL51 using clview acquisition software. If you are using your own acquisition softare, you may need to make some change to the reader
- JENOPTIK/LUFFT CHM15k
- CAMPBELL SCIENTIFIC CS135

## how to run

the repository contains some example files allowing you to test the code

- go to raw2l1 directory 
- you can get the list of input arguments using the command:

```
python raw2l1.py -h
```


- to convert a LUFFT CHM15k file 

```
python raw2l1 conf/conf_lufft_chm15k-nimbus_toprof_netcdf4.ini test/input/Jenoptik_chm15k/20150427_SIRTA_CHM150101_000.nc test/output/test_lufft_sirta.nc
```

- to convert a VAISALA CL31 or CL51 file

```
 python raw2l1 conf/conf_vaisala_cl31_toprof.ini 'test/input/vaisala_cl31/cl31_0a_z1R5mF3s_v01_20141030_*.asc' test/output/test_cl31.nc
```

```
python raw2l1 conf/conf_vaisala_cl51_toprof_netcdf4.ini 'test/input/vaisala_cl51/h4090100.dat' test/output/test_cl51.nc
```

# run the test suite

To run the tests you will need more python modules see requirements.txt file

- go to raw2l1 directory
- run

```
nosetests
```

# thanks

This program was developped in the scope of [TOPROF](http://www.toprof.imaa.cnr.it/) (COST ACTION ES1303).
Thanks to F.Wagner, I. Mattis, R. Leinweber for testing the software, providing example files and reporting bugs during the [CEILINEX](http://ceilinex2015.de)

# authors

M.-A Drouin based on the first version of Y. Morille

# Copyright

2014-2015 CNRS/Ecole polytechnique