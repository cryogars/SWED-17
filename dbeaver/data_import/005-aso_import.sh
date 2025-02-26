#!/usr/bin/env bash
#
# Import ASO SWE tifs
#
# Arguments:
#   -s: Path to file to import
#   -c Create table and import records
#   -a Append records to table (Default)
#   -d: Name of DB source file to use as temporary staging file
#       Required pattern: YYYYMMDD_file_name
# Example call
#   aso_import.sh -s data/ASO_SWE.tif -d data/20240101_SWE
#
# ASO UC extent for all flights in EPSG:32613
#   -te 231453.000 4530200.00 446853.203 4129449.623
# Converted with: cs2cs --only-best -f "%.8f" EPSG:32613 EPSG:4269
#   -te -108.18706066 40.87885627 -105.59976043 37.31016729

set -e

source import_script_options.sh

TABLE='aso'

DB_FILE="${DB_FILE}_db.tif"

gdalwarp \
    -overwrite -multi \
    -te 231453.000 4530200.00 446853.203 4129449.623 \
    -co TILED=YES \
    -co COMPRESS=ZSTD \
    -co PREDICTOR=2 \
    -co NUM_THREADS=ALL_CPUS \
    ${SOURCE_FILE} ${DB_FILE}


if [[ "$IMPORT_MODE" == "$APPEND_RECORDS" ]]; then
    POST_STEP="-p 005-update_aso_records.sql"
elif [[ "$IMPORT_MODE" == "$CREATE_TABLE" ]]; then
    POST_STEP="-p 005-update_aso_table.sql"
fi

./import_to_db.sh \
  -f ${DB_FILE} -t ${TABLE} \
  ${IMPORT_MODE} ${POST_STEP}
