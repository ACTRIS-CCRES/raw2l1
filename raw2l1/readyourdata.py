##!/bin/env python
# readyourdata.py reads your data files and return good variables
# readyourdata.py can be dynamically done from http://www.lmd.polytechnique.fr/~strat/raw2l1.php
#
# Input:
#  year:          Year of the date to be processed
#  month:         Month
#  day:           Day
#  maskin:        Your raw data files ('/home/data/mydata_20110102_mydata.yourextension'
#                 or '/home/data/mydata_20110102_*.yourextension' for multiple files)
#  dt_raw:  Time  resolution of raw data in seconds
#  dr_raw: Range resolution of raw data in meters
#  dt_out:  Time  resolution for output NetCDF file in seconds
#  dr_out: Range resolution for output NetCDF file in meters
#
# Output:
#  time:          Decimal hour since midnight      : size N*1
#  range:         Distance from instrument in [m]  : size M*1
#  rcs_910:                Range corrected signal : size M*N
#  bckgrd_rcs_910:         Background noise for the corresponding RCS : size N*1
#  cbh:                     Cloud Base Height [m]: size N*1
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
import __builtin__
import glob
import datetime
import sys


def readyourdata(year,month,day,maskin,dt_raw,dr_raw,dt_out,dr_out):




    range=[]
    time=[]
    rcs_910=[]
    bckgrd_rcs_910=[]
    cbh=[]

    if dr_out%dr_raw != 0:
        print 'Error: Output range resolution must be a multiple of raw resolution'
        sys.exit()

    if ((dt_out!=dt_raw) & (dt_out/dt_raw<2)):
        print 'Error: Output time resolution must at least twice the raw resolution or equal'
        sys.exit()
    

    
    filelist=sorted(glob.glob(maskin))
    if len(filelist)==0:
        print 'ERROR NO FILE:'+maskin
        sys.exit()
    
    
    nbofprof   = -1;
    maxnbofprof= 86400./dt_raw; # one profile each 2 second

    time   = np.nan*np.ones((maxnbofprof,));
    cbh    = np.nan*np.ones((maxnbofprof,3));
    scalefac        = np.nan*np.ones((maxnbofprof,));
    nrjfac          = np.nan*np.ones((maxnbofprof,));
    laser_temp      = np.nan*np.ones((maxnbofprof,));
    bckgrd_rcs_910  = np.nan*np.ones((maxnbofprof,));

    datetag='-%04d-%02d-%02d'%(year,month,day) #tag to be recognized 
    nboffile=0
    for currfile in filelist:
        print "Reading: ", currfile
        #######################################################
        ### HERE YOU HAVE TO IMPLEMENT YOUR OWN CODE
        ### YOU CAN:
        ###    -LOAD EACH ONE OF YOUR FILES
        ###    -REMOVE THE PRETRIG IF NOT DONE BEFORE
        ###    -APPLY AVERAGING IF NOT DONE BEFORE
        ###    -CONCATENATE EACH VARIBLES FOR HAVING THE WHOLE DAY
        ###    -CALCULATE A TIME BETWEEN 0 AND 24 IF NOT DONE BEFORE
        ###    -CALCULATE RANGE IN METER IF NOT DONE BEFORE
        ###    -APPLY YOUR BACKGROUND CORRECTION IF NOT DONE BEFORE
        ###    -APPLY YOUR OVERLAP CORRECTION IF NOT DONE BEFORE
        ###    -APPLY YOUR RANGE*RANGE CORRECTION IF NOT DONE BEFORE
        ###    -APPLY YOUR ....
        #######################################################
        
        fd = open(currfile, 'r')
        rawline = fd.readline() 
        while rawline:
            if ((len(rawline)>=11) & (rawline[0:11]==datetag)):
                nbofprof=nbofprof+1
                tab=rawline.split()
                subtab=tab[1].split(':')
                time[nbofprof]=float(subtab[0])+float(subtab[1])/60.+float(subtab[2])/3600.
            
                rawline = fd.readline()  # unused
                
                rawline = fd.readline()  # CBH
                tab=rawline.split()
                if tab[1]!='/////':
                     cbh[nbofprof,0]=int(tab[1])
                if tab[2]!='/////':
                     cbh[nbofprof,1]=int(tab[2])
                if tab[3]!='/////':
                     cbh[nbofprof,2]=int(tab[3])
                
                # find resol and number of points only for first profile (hope it is the same for the whole day)
                rawline = fd.readline()
                rawline = fd.readline()
                tab=rawline.split()
                
                scalefac[nbofprof]=float(tab[0]) 
                resolz=float(tab[1]) 
                lengthofprof=float(tab[2]) 
                nrjfac[nbofprof]=float(tab[3])
                laser_temp[nbofprof]=float(tab[4])
                bckgrd_rcs_910[nbofprof]=float(tab[7])
                
                if nbofprof==0:
                    range=np.arange(0,lengthofprof)*resolz+resolz/2.
                    rcs_910    = np.zeros( ( maxnbofprof, lengthofprof ) )
                
                rawline = fd.readline() 
                rcs_910[nbofprof,:]=[int(rawline[s*5:s*5+5], 16) for s in __builtin__.range(0,int(lengthofprof))]
                indneg = rcs_910[nbofprof,:]>=(16**5)/2
                rcs_910[nbofprof,indneg]=rcs_910[nbofprof,indneg]-(16**5)
            rawline = fd.readline() 

    if nbofprof<0:
        print 'ERROR : no profiles for this date'
        sys.exit()

    # keep only used profiles
    time=time[0:nbofprof+1]
    cbh =cbh[0:nbofprof+1,:]
    
    # to prevent warning we check if there is NAN
    cbh_nan = np.isnan(cbh)
    if np.all(cbh_nan):
        cbh = -999.*np.ones((cbh.shape[0]))
    elif np.any(cbh_nan):
        cbh = np.nanmin(cbh,1)
        cbh[np.isnan(cbh)] = -999.
    else:
        cbh = np.amin(cbh,1)
    
    rcs_910         = rcs_910[0:nbofprof+1,:].T
    scalefac        = scalefac[0:nbofprof+1]
    nrjfac          = nrjfac[0:nbofprof+1]
    laser_temp      = laser_temp[0:nbofprof+1]
    bckgrd_rcs_910  = bckgrd_rcs_910[0:nbofprof+1]


    ## Temporal averaging 
    if dt_out!=dt_raw:
        time_meant = np.arange(0,24,dt_out/3600)
        #######################################################
        ### IF USED, HERE YOU HAVE TO IMPLEMENT YOUR OWN CODE
        ### TO A APPLY TEMPORAL AVERAGING
        #######################################################
        #######################################################
        ### Here is an example
        #######################################################
        
        time_old         = time.copy()
        rcs_910_old     = rcs_910.copy()
        bckgrd_rcs_910_old     = bckgrd_rcs_910.copy()
        laser_temp_old  = laser_temp.copy()
        cbh_old     = cbh.copy()
        
        time              = -999.*np.ones((len(time_meant),))
        cbh               = -999.*np.ones((len(time_meant),))
        rcs_910          = np.nan*np.ones((np.shape(rcs_910_old)[0],len(time_meant)))
        bckgrd_rcs_910   = np.nan*np.ones((len(time_meant),))
        laser_temp       = np.nan*np.ones((len(time_meant),))
        
        currind = -1;
        for ii in __builtin__.range(len(time_meant)-1):
            indOK=np.where(((time_old>=time_meant[ii]) & (time_old<time_meant[ii+1])))[0]
            
            if len(indOK)>0:
                currind=currind+1
                time[currind]               = np.mean(time_meant[ii:ii+2])
                rcs_910[:,currind]         = np.mean(rcs_910_old[:,indOK],1)
                bckgrd_rcs_910[currind]    = np.mean(bckgrd_rcs_910_old[indOK])
                laser_temp[currind]        = np.mean(laser_temp_old[indOK])
                tempcbh = cbh_old[indOK]
                indcbhOK=np.where((tempcbh>0))[0]
                if indcbhOK!=[]:
                    cbh[currind]=np.min(tempcbh[indcbhOK])

        ## keep only used profiles
        time=time[0:currind+1]
        cbh=cbh[0:currind+1]
        laser_temp=laser_temp[0:currind+1]
        rcs_910 =rcs_910[:,0:currind+1]
        bckgrd_rcs_910 =bckgrd_rcs_910[0:currind+1]

    ## Vertical averaging 
    if dr_out!=dr_raw:
        nbofpt4mean = np.round(dr_out/dr_raw)

        #######################################################
        ### IF USED, HERE YOU HAVE TO IMPLEMENT YOUR OWN CODE
        ### TO A APPLY VERTICAL AVERAGING
        #######################################################
        #######################################################
        ### Here is an example
        #######################################################
        range_old = range.copy()
        rcs_910_old  = rcs_910.copy()

        range   = np.nan*np.ones((np.floor(len(range_old)/float(nbofpt4mean)),1))
        rcs_910  = np.nan*np.ones((np.floor(len(range_old)/float(nbofpt4mean)),np.shape(rcs_910_old)[1]))

        currind=-1;
        for ii in __builtin__.range(0,int(np.floor(len(range_old)/float(nbofpt4mean))*nbofpt4mean),int(nbofpt4mean)):
            currind=currind+1
            range[currind]   = np.mean(range_old[ii:ii+nbofpt4mean])

            rcs_910[currind,:]=np.mean(rcs_910_old[ii:ii+nbofpt4mean,:],0).T
    
    
    return time,range,rcs_910,bckgrd_rcs_910,cbh,laser_temp
