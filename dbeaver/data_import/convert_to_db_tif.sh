#!/usr/bin/env bash
# 
# Convert a file to a tiled GTiff
#
# Script to prepare importing a SWE data into the database. It will create a 
# tiled COG file with the _db.tif suffix to indicate that this file is used in 
# the database.
#
# Arguments:
#   1: Path and file name to use for new file
#   2: Path to file to convert
#   3: OPTIONAL: convert to given SRID
#
# Example:
#   convert_to_db_tif.sh data/202040101_SWE data/2024_SWE.tif

set -e

if [[ $# -lt 2 ]]; then
    echo "Missing required number of arguments" >&2
    echo "  Usage: convert_to_db_tif.sh <output_file_name> <input_file>" >&2
    exit 1
fi

WARP=""
if [[ ! -z ${3} ]]; then
    WARP="-t_srs ${3}"
fi

DB_FILE="${1}_db.tif"

gdalwarp -overwrite -multi \
    ${WARP} \
    -co TILED=YES \
    -co COMPRESS=ZSTD \
    -co PREDICTOR=2 \
    -co NUM_THREADS=ALL_CPUS \
    ${2} ${DB_FILE}
