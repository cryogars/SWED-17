#!/usr/bin/env bash
#
# Import University of Arizona SWE data grid

raster2pgsql -I -C -e -Y -s 4269 -F -t 32x32 SWE_Mask_v01.nc swann_swe_mask_4k | \
    psql -h mujeres -U oper -d swe_data
