#!/usr/bin/env bash
#
# Import snow.nc file from iSnobal and store in the DB.
#
# Arguments:
#   -s: Path to file to import
#   -c Create table and import records
#   -a Append records to table (Default)
#   -d: Name of DB source file to create
#       Required pattern: YYYYMMDD_file_name
# Example call:
#   isnobal.sh -s NETCDF:"data/20230401_iSnobal_ERW_snow.nc":specific_mass -d db_import/20240101_isnobal

# -f = Prevent glob expansion when importing multiple files
set -ef

# DB_File not required since we are not using out-db rasters and store the data
# in the DB. The import_script_options has this as a required argument though.
DB_FILE='00000000_db_file'
source import_script_options.sh

TABLE='isnobal'

if [[ "$IMPORT_MODE" == "$APPEND_RECORDS" ]]; then
    POST_STEP="-p 006-update_isnobal_records.sql"
elif [[ "$IMPORT_MODE" == "$CREATE_TABLE" ]]; then
    POST_STEP="-p 006-update_isnobal_table.sql"
fi

./import_to_db.sh -f ${SOURCE_FILE} -t ${TABLE} ${IMPORT_MODE} ${POST_STEP}
