#!/usr/bin/env bash
#
# Import SNODAS SWE data
#
# Arguments:
#   -s: Path to file to import
#   -c Create table and import records
#   -a Append records to table (Default)
#   -d: Name of DB source file to create
#       Required pattern: YYYYMMDD_file_name
# Example call
#   snodas_import.sh -s data/snodas_SWE.dat -d db_data/20240102_SWE

set -e

TABLE='snodas'

source import_script_options.sh

TMP_FILE=${SOURCE_FILE/.dat/.vrt}

## Convert from .dat to a GeoTIFF VRT
gdal_translate \
  -of GTiff \
  -a_srs EPSG:4326 \
  -a_ullr -124.73333333333333 52.87500000000000 -66.94166666666667 24.95000000000000 \
  -a_nodata -9999 \
  ${SOURCE_FILE} ${TMP_FILE}

## NetCDF
# gdal_translate \
#   -of NetCDF \
#   -a_srs EPSG:4326 \
#   -a_ullr -124.73333333333333 52.87500000000000 -66.94166666666667 24.95000000000000 \
#   -a_nodata -9999 \
#   -co FORMAT=NC4C \
#   -co COMPRESS=DEFLATE \
#   ${1} ${2}

# NOTE: This will update the $DB_FILE variable
source ./convert_to_db_tif.sh ${DB_FILE} ${TMP_FILE}

# Cleanup tmp file
rm ${TMP_FILE}

if [[ "$IMPORT_MODE" == "$APPEND_RECORDS" ]]; then
    POST_STEP="-p 004-update_snodas_records.sql"
elif [[ "$IMPORT_MODE" == "$CREATE_TABLE" ]]; then
    POST_STEP="-p 004-update_snodas_table.sql"
fi

./import_to_db.sh -f ${DB_FILE} -t ${TABLE} --out-db ${IMPORT_MODE} ${POST_STEP}
