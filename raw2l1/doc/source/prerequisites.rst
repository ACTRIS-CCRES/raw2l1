Prerequisites
=============

Raw2L1 should be able to run under Linux, Windows and MacOS environments.
To run Raw2L1 core program you need to have at least Python 3.7 and the modules
listed below

* `Numpy`_
* `netCDF4`_

Some additional modules can be required by raw LIDAR data reader modules.
Modules required by reader will be listed in their own doc pages.

Installing with conda
---------------------

If Python is not installed on your computer (whatever is your Operating system, the easiest way is to install the `anaconda`_ python distribution.
Anaconda is a distribution dedicated to scientific computing and comes with most commonly required calculation modules. This is the easiest solution
on windows and MAC.

The netCDF4 package is not installed by default. To install it, you have to type the command:

.. code-block:: bash

    conda env create -f environments/environment.yml

Installing with pip
-------------------

.. code-block:: bash

    pip install -r requirements/requirements.txt



.. _Numpy: http://www.numpy.org/
.. _netCDF4: https://github.com/Unidata/netcdf4-python
.. _SPHINX: http://sphinx-doc.org/index.html
.. _anaconda: http://continuum.io/downloads
.. _nose: https://nose.readthedocs.org/en/latest/