#!/usr/bin/env bash
# Import the Upper/Lower CRB and GSL zone shapefiles

DB_CONNECT_OPTIONS='service=swe_db'

shp2pgsql -c -s 4269 -i -I CBRFC_Zones_UC.shp CBRFC_Zones_UC | \
    psql ${DB_CONNECT_OPTIONS}
shp2pgsql -c -s 4269 -i -I CBRFC_Zones_LC.shp CBRFC_Zones_LC | \
    psql ${DB_CONNECT_OPTIONS}
shp2pgsql -c -s 4269 -i -I CBRFC_Zones_GSL.shp CBRFC_Zones_GSL | \
    psql ${DB_CONNECT_OPTIONS}
