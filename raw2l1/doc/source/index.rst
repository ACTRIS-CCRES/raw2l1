.. Raw2L1 documentation master file, created by
   sphinx-quickstart on Thu Nov 13 16:29:33 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Raw2L1's documentation
=================================

Raw2L1 is a free and open source sofware developped in python at `SIRTA`_/`IPSL`_.

Raw2L1 has been designed to ease the conversion of raw LIDAR data file into `netCDF`_ file and add you own variables and attributes. It
uses a configuration file in `INI`_ format to define the structure of the netCDf file and a dedicated reader for each type of manufacter/model of LIDAR.

At the moment Raw2L1 is able to process raw data of the model below

* Jenoptik CHM15K nimbus
* Vaisala CL31
* Vaisala CL51

Raw2L1 disposes of a dedicated interface allowing anyone to add a new LIDAR data reader fallowing only a few rules.

.. toctree::
   :maxdepth: 2

   Prerequisites <prerequisites>
   Running <running>
   Readers <readers>






.. _SIRTA: http://www.sirta.fr
.. _netCDF: http://www.unidata.ucar.edu/software/netcdf/
.. _INI: https://en.wikipedia.org/wiki/INI_file
.. _IPSL: https://www.ipsl.fr/
