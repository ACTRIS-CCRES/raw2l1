![main](https://github.com/ACTRIS-CCRES/raw2l1/actions/workflows/ci.yaml/badge.svg)
[![codecov](https://codecov.io/gh/ACTRIS-CCRES/raw2l1/graph/badge.svg?token=7BVO7V5IA8)](https://codecov.io/gh/ACTRIS-CCRES/raw2l1)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

![GitHub issues](https://img.shields.io/github/issues/ACTRIS-CCRES/raw2l1)
![GitHub pull requests](https://img.shields.io/github/issues-pr/ACTRIS-CCRES/raw2l1)



# raw2l1

Code to convert raw LIDAR data into normalized netCDF files

## Dependencies install

### Install package using pip

```bash
pip install raw2l1
```

This installs the `raw2l1` command.

## Instruments compatibility

Example of configuration files for instruments are provided in the [raw2l1-config](https://github.com/ACTRIS-CCRES/raw2l1-config) repository.

### VAISALA ceilometers

You must use clview acquisition software. If you are using your own acquisition software, you may need to make some change to the reader
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
raw2l1 --help
```


- to convert a LUFFT CHM15k file

```
raw2l1 '20150427' conf/conf_lufft_chm15k_eprofile.ini test/input/Jenoptik_chm15k/20150427_SIRTA_CHM150101_000.nc test/output/test_lufft_sirta.nc
```

- to convert a VAISALA CL31 or CL51 file

```
raw2l1 '20141030' conf/conf_vaisala_cl31_eprofile.ini 'test/input/vaisala_cl31/cl31_0a_z1R5mF3s_v01_20141030_*.asc' test/output/test_cl31.nc
```

### Filtering data

You can filter data to only keep data of date provided as arguments using `--filter-day` option.

# Realtime production

Options are available for the use of raw2l1 in near-realtime processing

- ```-file_min_size```: allow to define the minimum size of input file in bytes. Files with a smaller size will be rejected.
- ```-file_max_age```: allow to define the maximum age of data in a file in hours
- ```--check_timeliness```: check if the data read are not to old or in the future. By default it checks thats data have a maximum age of 2 hours. This value can be changed with option ```--file_max_age```

# Developments

## Get sources

Clone the repository

```bash
git clone git@github.com:ACTRIS-CCRES/raw2l1.git
```

## Install

### Using uv (recommended)

Install [uv](https://docs.astral.sh/uv/getting-started/installation/)

```bash
uv sync --all-groups
```

### Using conda or pixie

```bash
conda create -n raw2l1 python=3.13 pip
conda activate raw2l1
pip install . --group dev
```

### Using venv

```bash
python -m venv path/env/raw2l1-dev
source activate path/env/raw2l1-dev/bin/activate
```

Then install the dependencies with

```bash
pip install . --group dev
```

## Install pre-commit

Pre-commit is used to check code before commit. It is recommended to install it in your development environment.

```bash
uv run pre-commit install
uv run pre-commit install --hook-type commit-msg
```

or with conda, pixie or venv

```bash
pre-commit install
pre-commit install --hook-type commit-msg
```

## Run the test suite

```bash
uv run pytest
```

or with conda, pixie or venv

```bash
python -m  pytest
```

# Thanks

This program was developped in the scope of [TOPROF](http://www.toprof.imaa.cnr.it/) (COST ACTION ES1303).
Thanks to F.Wagner, I. Mattis, R. Leinweber for testing the software, providing example files and reporting bugs during the [CEILINEX](http://ceilinex2015.de)

# Copyright

2014-2026 CNRS/Ecole polytechnique
