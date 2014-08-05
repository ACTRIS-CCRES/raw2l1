##!/bin/env python
# lidar2netcdf.py allows to write your own NetCDF file
# lidar2netcdf.py can be dynamically done from http://www.lmd.polytechnique.fr/~strat/raw2l1.php
#
# Input:
#  conf:          ParserConfig object containing data of config.ini file
#  year:          Year of the date to be processed
#  month:         Month
#  day:           Day
#  time:          Decimal hour since midnight      : size N*1
#  range:         Distance from instrument in [m]  : size M*1
#  rcs_910:                Range corrected signal : size M*N
#  bckgrd_rcs_910:         Background noise for the corresponding RCS : size N*1
#  cbh:                     Cloud Base Height [m]: size N*1
#  overlap:                 overlap function :  size N*1
#  netcdffilename:          Output filename
#  dt_out:                  Time  resolution for output NetCDF file in seconds
#  dr_out:                  Range resolution for output NetCDF file in meters
#
#
#
# This file is part of Raw2L1.
#
#    Raw2L1 is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    any later version.
#
#    Raw2L1 is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Raw2L1.  If not, see http://www.gnu.org/licenses/.
#
# Copyright : Morille Yohann, Haeffelin Martial 2007-2012
# Contact : strat@lmd.polytechnique.fr
# See: http://www.lmd.polytechnique.fr/~strat/raw2l1.php
#
import netCDF4
import numpy as np
import glob


def lidar2netcdf(conf,year,month,day,time,range,rcs_910,bckgrd_rcs_910,cbh,laser_temp,overlap,netcdffilename,dt_out,dr_out):

    # Get metadata contains in configuration file
    title     = conf.get('global', 'title')
    loc       = conf.get('global', 'location')
    instit    = conf.get('global', 'institution')
    system    = conf.get('global', 'system')
    inst_id   = conf.get('global', 'instrument_id')
    altitude  = float(conf.get('global', 'instrument_altitude'))
    latitude  = float(conf.get('global', 'instrument_latitude'))
    longitude = float(conf.get('global', 'instrument_longitude'))
    zangle    = float(conf.get('global', 'zenith_angle'))
    l_lambda  = float(conf.get('global', 'laser_wavelength'))
    l_polar   = conf.get('global', 'laser_polarization')
    l_diver   = float(conf.get('global', 'laser_divergence'))
    l_prf     = float(conf.get('global', 'laser_prf'))
    l_lw      = float(conf.get('global', 'laser_linewidth'))
    t_fov     = float(conf.get('global', 'telescope_fov'))
    t_diam    = float(conf.get('global', 'telescope_diameter'))
    t_optaxes = conf.get('global', 'telescope_opticalaxes')
    detect    = conf.get('global', 'detection_mode')
    diffusion = conf.get('global', 'diffusion')
    over_bool = conf.get('global', 'overlap')

    # Get longname of rcs and background
    rcs_lname = conf.get('rcs', 'long_name')
    bck_lname = conf.get('background_rcs', 'long_name')
    bck_comm  = conf.get('background_rcs', 'comments')

    is_over_f = False
    if over_bool == 'true':
        is_over_f = True

    nc = netCDF4.Dataset(netcdffilename, 'w', format='NETCDF3_CLASSIC')


    nc.createDimension('time', None)
    nc.createDimension('range', len(range))

    
    nctime = nc.createVariable('time', 'f', ('time',))
    nctime[:] = time
    nctime.long_name = 'Decimal hours since midnight UTC' 
    nctime.standard_name = 'time' 
    nctime.units  = 'hours since '+'%04d'%year+'-'+'%02d'%month+'-'+'%02d'%day+' 00:00:00'
    nctime.axis = 'T' 
    nctime.calendar = 'none' 

    ncrange = nc.createVariable('range', 'f', ('range',))
    ncrange[:] = range
    ncrange.units = 'm' 
    ncrange.long_name = 'Range from Telescope to each range gate' 
    ncrange.axis = 'z' 

    
    ncrcs_910    = nc.createVariable('rcs_910', 'd', ('time','range'))
    ncrcs_910[:] = rcs_910.T
    ncrcs_910.units = '-' 
    ncrcs_910.long_name = rcs_lname
    ncrcs_910.missing_value = -999. 
    ncrcs_910.laser = 'laser0 -see global attributs for more details' ;
    ncrcs_910.telescope = 'telescope0 -see global attributs for more details' ;
    
    ncbckgrd_rcs_910    = nc.createVariable('bckgrd_rcs_910', 'd', ('time',))
    ncbckgrd_rcs_910[:] = bckgrd_rcs_910.T
    ncbckgrd_rcs_910.units = '-' 
    ncbckgrd_rcs_910.long_name = bck_lname
    ncbckgrd_rcs_910.missing_value = -999. 
    ncbckgrd_rcs_910.comment = bck_comm
    
    nccbh    = nc.createVariable('cbh', 'f', ('time',))
    nccbh[:] = cbh
    nccbh.units = 'm' 
    nccbh.long_name = 'Cloud base height AGL [m]' 
    nccbh.missing_value = -999.

    ncltemp   = nc.createVariable('temp_laser', 'f', ('time',))
    ncltemp[:] = laser_temp
    ncltemp.units = 'Celsius ' 
    ncltemp.long_name = 'Laser temperature' 
    ncltemp.missing_value = -999.

    # Add overlap function if available
    if is_over_f:
        ncover = nc.createVariable('overlap', 'f', ('range',))
        ncover[:] = overlap['overlap']
        ncover.units = '-'
        ncover.long_name = 'overlap function'
        ncover.missing_value = -999.
    
    ncrange_resol    = nc.createVariable('range_resol', 'f')
    ncrange_resol.assignValue(dr_out)
    ncrange_resol.units = 'm' 
    ncrange_resol.long_name = 'Range resolution' 
    
    nctime_resol    = nc.createVariable('time_resol', 'f')
    nctime_resol.assignValue(dt_out)
    nctime_resol.units = 's' 
    nctime_resol.long_name = 'Time resolution' 
    
    nczenith_angle    = nc.createVariable('zenith_angle', 'f')
    nczenith_angle.assignValue(zangle)
    nczenith_angle.units = 'degree' 
    nczenith_angle.long_name = 'Zenith/tilt angle' 
    
    ncaltitude    = nc.createVariable('altitude', 'f')
    ncaltitude.assignValue(altitude)
    ncaltitude.units = 'm' 
    ncaltitude.long_name = 'Altitude above mean sea level' 
    
    nclatitude    = nc.createVariable('latitude', 'f')
    nclatitude.assignValue(latitude)
    nclatitude.units = 'degree_north' 
    nclatitude.valid_min = -90. 
    nclatitude.valid_max = 90. 
    
    nclongitude    = nc.createVariable('longitude', 'f')
    nclongitude.assignValue(longitude)
    nclongitude.units = 'degree_east' 
    nclongitude.valid_min = -180. 
    nclongitude.valid_max = 180. 


    nc.location = loc
    nc.system = system
    nc.instrument_id = inst_id
    nc.title = title
    nc.institution = instit
    nc.altitude = str(altitude)+' m' 
    nc.latitude = str(latitude)+' deg N' 
    nc.longitude = str(longitude)+' deg E' 
    nc.zenith_angle = str(zangle)+' deg'
    nc_laser0_wavelength = str(l_lambda)+' nm'
    nc.laser0_polarization = l_polar
    nc.laser0_divergence = str(l_diver)+' rad'
    nc.laser0_prf = str(l_prf)+' kHz' ;
    nc_laser0_linewidth = str(l_lw)+' nm'
    nc.telesc0_fov = str(t_fov)+' rad' ;
    nc.telesc0_diameter = str(t_diam)+' m'
    nc.telesc0_optical_axes = t_optaxes
    nc.detection_mode = detect
    nc.diffusion = diffusion
    nc.overlap = over_bool
    nc.range_resol = str(dr_out)+' m' 
    nc.time_resol = str(dt_out)+' s' 
    nc.year = year 
    nc.month = month 
    nc.day = day 
    nc.history = 'created with Raw2L1 http://www.lmd.polytechnique.fr/~strat/downloadraw2l1.php'

    nc.close()
