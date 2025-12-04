#!/usr/bin/env bash
#
# Import National Water Model SWE
#
# Arguments:
#   -s: Path to file to import
#   -c Create table and import records
#   -a Append records to table (Default)
#   -d: Name of DB source file to create
#       Required pattern: YYYYMMDD_file_name
# Example call
#   nwm_import.sh -s NETCDF="data/NWM.nc":SNEQV -d "db_import/20240101_NWM_SWE" 

set -e

source import_script_options.sh

TABLE='nwm'

# NOTE: This will update the $DB_FILE variable
source ./convert_to_db_tif.sh ${DB_FILE} ${SOURCE_FILE} EPSG:4326

if [[ "$IMPORT_MODE" == "$APPEND_RECORDS" ]]; then
    POST_STEP="-p 007-update_nwm_records.sql"
elif [[ "$IMPORT_MODE" == "$CREATE_TABLE" ]]; then
    POST_STEP="-p 007-change_nwm_table.sql"
fi

./import_to_db.sh -f ${DB_FILE} -t ${TABLE} --out-db ${IMPORT_MODE} ${POST_STEP}
