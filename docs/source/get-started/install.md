# Installation

Raw2L1 should be able to run under Linux, Windows and MacOS
environments. To run Raw2L1 core program you need to have at least
Python 3.7 and the modules listed below

-   [Numpy](http://www.numpy.org/)
-   [netCDF4](https://github.com/Unidata/netcdf4-python)

Some additional modules can be required by raw LIDAR data reader
modules. Modules required by reader will be listed in their own doc
pages.

## With conda

If Python is not installed on your computer (whatever is your Operating
system, the easiest way is to install the
[anaconda](https://www.anaconda.com/) python distribution. Anaconda
is a distribution dedicated to scientific computing and comes with most
commonly required calculation modules. This is the easiest solution on
windows and MAC.


``` bash
conda env create -f environments/environment.yml
```

It will create a `raw2l1` environment with all the require modules. Than activate it.

``` bash
conda activate raw2l1
```

## With pip

``` bash
python -m venv raw2l1_env
source raw2l1_env/bin/activate
pip install -r requirements/requirements.txt
```
