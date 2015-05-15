Prerequisites
=============

Raw2L1 should be able to run under Linux, Windows and MacOS environments.
To run Raw2L1 core program you need to have Python 2.7 and the modules
listed below

* `Numpy`_
* `netCDF4`_
* `SPHINX`_ for the documentation
* `nose`_ to run the test

Some additional modules can be required by raw LIDAR data reader modules.
Modules required by reader will be listed in their own doc pages.

Installing Python (Windows, Linux, Mac)
---------------------------------------

If Python is not installed on your computer (whatever is your Operating system, the easiest way is to install the `anaconda`_ python distribution.
Anaconda is a distribution dedicated to scientific computing and comes with most commonly required calculation modules. This is the easiest solution
on windows and MAC.

The netCDF4 package is not installed by default. To install it, you have to type the command:

.. code-block:: bash

    conda install netcdf4

On linux (with admin rights)
----------------------------

Most of the time, you should have a version of python install but some
packages could be missing.

Use the package manager of your distribution to install the required
packages.

on redhat family distributions (Fedora, Centos...):

.. code-block:: bash

	sudo yum install python numpy netcdf4-python python-nose

on debian family distributions (Ubuntu, Mint...):

.. code-block:: bash

	sudo apt-get install python numpy netcdf4-python python-nose

On MAC
------

You need to first install `Macports <https://www.macports.org/>`_ which
is a package manager for MacOS. Once its done you can execute the command
below

.. code-block:: bash

	sudo port install py27-numpy py27 py27-netcdf4

Be patient, the installation can be quite long.

.. _Numpy: http://www.numpy.org/
.. _netCDF4: https://github.com/Unidata/netcdf4-python
.. _SPHINX: http://sphinx-doc.org/index.html
.. _anaconda: http://continuum.io/downloads
.. _nose: https://nose.readthedocs.org/en/latest/