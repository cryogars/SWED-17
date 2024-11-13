#!/usr/bin/env bash
#
# General purpose script to import data to the database
#
# Arguments:
#   -f File to import
#   -t DB Table to use
#   -c Create table and import records
#   -a Append records to table (Default)
#   -p Post import script to run (Optional)
#   --out-db: Import file as out-db raster

set -e

DB_CONNECT_OPTIONS='-h mujeres -U oper -d swe_data'
# Treat files as out-db or import the actual data
OUT_DB_RASTER=""

# Default import mode is to append
# Values are raster2pgsql Options
APPEND_RECORDS="-a"
CREATE_TABLE="-d -C -x -I"
IMPORT_MODE=$APPEND_RECORDS

# Script argument options
LONG_OPTIONS=file:,table:,create,out-db,append,post-import:
SHORT_OPTIONS=f:t:cap:

# Parse and set variables
ARGUMENTS=$(getopt --options=${SHORT_OPTIONS} --longoptions=${LONG_OPTIONS} --name $0 -- "$@") || exit 1
eval set -- "$ARGUMENTS"

while true; do
    case "$1" in
        -a|--append)
            IMPORT_MODE=$APPEND_RECORDS
            shift
            ;;
        -c|--create)
            IMPORT_MODE=$CREATE_TABLE
            shift
            ;;
        -f|--file)
            FILE="$2"
            shift 2
            ;;
        -t|--table)
            TABLE="$2"
            shift 2
            ;;
        -p|--post-import)
            POST_IMPORT="$2"
            shift 2
            ;;
        --out-db)
            OUT_DB_RASTER="-R"
            shift
            ;;
        --)
            shift
            break
            ;;
        *)
            echo "Error parsing options"
            exit 1
            ;;
    esac
done

# Set absolute file path for out-db rasters
if [[ ! -z ${OUT_DB_RASTER} ]]; then
    FILE=$(realpath ${FILE})
fi

# Import metadata to database
raster2pgsql ${IMPORT_MODE} -M -F ${OUT_DB_RASTER} -Y -l 2,3 -t 32x32 \
    ${FILE} ${TABLE} | \
    psql ${DB_CONNECT_OPTIONS}

# Process post import script
if [[ ! -z $POST_IMPORT ]]; then
    psql ${DB_CONNECT_OPTIONS} -f ${POST_IMPORT}
fi
