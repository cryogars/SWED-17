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
# Produce extent with:
# gdal raster mosaic --resolution lowest *.tif ASO_SWE.vrt
#
# Flights in 13N extent
#   -te 231453.000 4129449.190 446853.435 4530200.000 \
#
# Flights in 12N extent
#   -te 464450.000 4147198.657 776700.631 4811700.000 \
#

set -e

SCRIPT_PATH="$(dirname "$(realpath $0)")"
source ${SCRIPT_PATH}/import_script_options.sh

TABLE='aso'

DB_FILE="${DB_FILE}_db.tif"

gdalwarp \
    -overwrite -multi \
    -te 231453.000 4129449.190 446853.435 4530200.000 \
    -dstnodata -9999 \
    -co TILED=YES \
    -co COMPRESS=ZSTD \
    -co PREDICTOR=2 \
    -co NUM_THREADS=ALL_CPUS \
    ${SOURCE_FILE} ${DB_FILE}


if [[ "$IMPORT_MODE" == "$APPEND_RECORDS" ]]; then
    POST_STEP="005-update_aso_records.sql"
elif [[ "$IMPORT_MODE" == "$CREATE_TABLE" ]]; then
    POST_STEP="005-update_aso_table.sql"
fi

${SCRIPT_PATH}/import_to_db.sh \
  -f ${DB_FILE} -t ${TABLE} ${IMPORT_MODE} -p ${SCRIPT_PATH}/${POST_STEP}
