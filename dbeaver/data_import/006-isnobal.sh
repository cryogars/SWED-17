#/usr/bin/env bash
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
set -e

source import_script_options.sh

TABLE='isnobal'

# NOTE: This will update the $DB_FILE variable
source ./convert_to_db_tif.sh ${DB_FILE} ${SOURCE_FILE}

if [[ "$IMPORT_MODE" == "$APPEND_RECORDS" ]]; then
    POST_STEP="-p 006-update_isnobal.sql"
elif [[ "$IMPORT_MODE" == "$CREATE_TABLE" ]]; then
    POST_STEP="-p 006-update_isnobal_table.sql"
fi

./import_to_db.sh -f ${DB_FILE} -t ${TABLE} ${IMPORT_MODE} ${POST_STEP}

rm ${DB_FILE}
