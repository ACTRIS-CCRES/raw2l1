![main](https://github.com/ACTRIS-CCRES/raw2l1/actions/workflows/ci.yaml/badge.svg?branch=master)
[![codecov](https://codecov.io/gh/ACTRIS-CCRES/raw2l1/graph/badge.svg?token=7BVO7V5IA8)](https://codecov.io/gh/ACTRIS-CCRES/raw2l1)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

![GitHub issues](https://img.shields.io/github/issues/ACTRIS-CCRES/raw2l1)
![GitHub pull requests](https://img.shields.io/github/issues-pr/ACTRIS-CCRES/raw2l1)



# raw2l1

Code to convert raw LIDAR data into normalized netCDF files

## Get code

### Using ssh

```bash
git@github.com:ACTRIS-CCRES/raw2l1.git
```

### Using https

```bash
https://github.com/ACTRIS-CCRES/raw2l1.git
```

## Dependencies install

### Using conda

```bash
conda env create -f environements/environment.yml
```

It will create a `raw2l1` environment. Activate before using raw2l1

```bash
conda activate raw2l1
```

### Using pip

We recommand creating a virtual environment before installing the dependencies with

```bash
python -m venv path/env/raw2l1
source activate path/env/raw2l1/bin/activate
```

Then install the dependencies with

```bash
python -m pip install -r requirements/requirements.txt
```

## Instruments compatibility

### VAISALA ceilometers

You must use clview acquisition software. If you are using your own acquisition softare, you may need to make some change to the reader
- CL31
- CL51
- CL61

### JENOPTIK/LUFFT ceilometers

- CHM8k
- CHM15k

### CAMPBELL SCIENTIFIC ceilometers

- CS135

### Leosphere/vaisala doppler wind lidars

- Windcube vls7v2
- windcube wls70

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

# Realtime production

Options are available for the use of raw2l1 in near-realtime processing

- ```-file_min_size```: allow to define the minimum size of input file in bytes. Files with a smaller size will be rejected.
- ```-file_max_age```: allow to define the maximum age of data in a file in hours
- ```--check_timeliness```: check if the data read are not to old or in the future. By default it checks thats data have a maximum age of 2 hours. This value can be changed with option ```--file_max_age```

# Developments

## Get sources

You will first need to create an account on gitlab.in2p3.fr (see [here](https://doc.cc.in2p3.fr/en/Collaborative-tools/tools/gitlab.html#account-registration)).

Then you can clone the repository

```bash
git clone git@github.com:ACTRIS-CCRES/raw2l1.git
```

## Install

### Using conda

```bash
conda env create -f environements/environment-dev.yml
conda activate raw2l1-dev
```

### Using pip

We recommand creating a virtual environment before installing the dependencies with

```bash
python -m venv path/env/raw2l1-dev
source activate path/env/raw2l1-dev/bin/activate
```

Then install the dependencies with

```bash
pip install -r requirements/requirements-dev.txt
```

## Install pre-commit

```bash
pre-commit install
```

## Run the test suite

To run the tests you will need more python modules see requirements.txt file

- go to raw2l1 directory
- run

```
ce raw2l1
python -m pytest
```

## Run the linter and code formatter

raw2l1 use [ruff](https://astral.sh/ruff) for linting and code formatting.

### Check code

```bash
ruff check raw2l1
```

### Fix code

You can also try to make ruff fix some of the issues it detected.

```bash
ruff check --fix raw2l1
```

### Format code

When your `ruff check` is ok, you can user the formatter.

```bash
ruff format raw2l1
```

# Thanks

This program was developped in the scope of [TOPROF](http://www.toprof.imaa.cnr.it/) (COST ACTION ES1303).
Thanks to F.Wagner, I. Mattis, R. Leinweber for testing the software, providing example files and reporting bugs during the [CEILINEX](http://ceilinex2015.de)

# Copyright

2014-2023 CNRS/Ecole polytechnique
