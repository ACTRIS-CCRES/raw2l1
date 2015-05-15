Configuring Raw2L1
==================

The configuration of raw2l1 is made using a file using the INI format. This file allows you to define which:

    * data reader to use and netCDf format (NETCDF3_CLASSIC or NETCDF4)
    * to provide additional parameters to the data reader (if needed). For example a file containing the overlap function for the LUFFT CHM15K-NIMBUS reader
    * define the variables and metadata that will be saved in the netCDF file.

The *conf* directory should contains examples of configuration file for each reader.

INI format
----------

The INI format is based on sections name (marked using brackets) and attributes associated to a value.

.. code-block:: ini

    ; comments
    [section01]
    attribute01 = value01
    attribute02 = value02
    ...
    attributenn = valuenn

    [section02]
    ...


[conf] section
--------------

This section requires three attribute:

reader_dir:
    the path (relative or abolute) to the directory where raw2l1 will search for the data reader

reader:
    the name of the reader to use (without the **.py** extension)

netcdf_format:
    the format of the netCDF file. **NETCDF3_CLASSIC** or **NETCDF4**. It is recommended to use the NETCDF3_CLASSIC format for compatibility reasons. The ability to read the NETCDF4 format in not implemented in all softwares.

This section should look like this:

.. code-block:: ini

    [conf]
    reader_dir = reader
    reader = lufft_chm15k_nimbus
    netcdf_format = NETCDF3_CLASSIC

[reader_conf] section
---------------------

This section allows to provide additional parameters to the data reader. For the moment the only the reader for the CHM15K-NIMBUS use this possibility to provide
the overlap function.

Even if no attributes are defined the section name should appear in the configuration file.

.. code-block:: ini

    [reader_conf]
    overlap_file = reader/jenoptik_chm15k_overlap.txt

Defining the netCDF file
------------------------

There are 3 main parts to define a netCDF file.

    * The global variables
    * The variables which will be the **dimensions** of the other data
    * The variables containing the data

Global variables
++++++++++++++++

The global variables are used to defined parameters common to the entire data file. To respect the `netCDF-CF`_ at least six global variables should be present:

    * title
    * institution
    * source
    * history
    * references
    * comment
    * Convention (the **c** is required to be uppercase for this variable)

There is a special case for the history variable. If this attribute is present in the global section (even without a value), raw2l1 will put in it the date at which the file has been created. If you put text for the history variables, raw2l1 will write in the netCDF file the date of creation follow by the text you entered.

This section should look like the example below:

.. code-block:: ini

    [global]
    site_location = site_location
    instrument_id = instrument_id
    instrument_version_number = instrument_version_number
    principal_investigator = M. PI
    title = my ALC data
    institution = institution
    source = source
    history = history
    references = references
    comment = comment
    author = author
    conventions = CF-1.6

Dimension variables
+++++++++++++++++++

Each file should at least contains two dimensions:

    * time
    * range

.. _netCDF-CF: http://cfconventions.org/

