#!/usr/bin/env bash
#
# Import CU Boulder SWE
#
# Arguments:
#   -s: Path to file to import
#   -c Create table and import records
#   -a Append records to table (Default)
#   -d: Name of DB source file to create
#       Required pattern: YYYYMMDD_file_name
# Example call
#   cu_boulder_import.sh -s data/CUB_SWE.tif -d data/20240101_SWE 
set -e

source import_script_options.sh

TABLE='cu_boulder'

# NOTE: This will update the $DB_FILE variable
source ./convert_to_db_tif.sh ${DB_FILE} ${SOURCE_FILE}

if [[ "$IMPORT_MODE" == "$APPEND_RECORDS" ]]; then
    POST_STEP="-p 003-update_cub_records.sql"
elif [[ "$IMPORT_MODE" == "$CREATE_TABLE" ]]; then
    POST_STEP="-p 003-update_cub_table.sql"
fi

./import_to_db.sh -f ${DB_FILE} -t ${TABLE} --out-db ${IMPORT_MODE} ${POST_STEP}
