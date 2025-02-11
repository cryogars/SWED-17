#!/usr/bin/env bash
#
# Import University of Arizona SWE 1km SWE
#
# Arguments:
#   -s: Path to file to import
#   -c Create table and import records
#   -a Append records to table (Default)
#   -d: Name of DB source file to create
#       Required pattern: YYYYMMDD_file_name
# Example call
#   ua_swe_import.sh -s NETCDF="data/UA_SWE.nc":SWE -d db_data/20240101_SWE
# Stream straight from website
#  ua_swe_import.sh -s NETCDF:"/vsicurl/https://climate.arizona.edu/data/UA_SWE/DailyData_800m/WY2024/UA_SWE_Depth_800m_v1_20240430_stable.nc":SWE -d db_data/20240430_SWE

set -e

source import_script_options.sh

UA_TABLE='ua_1km'

# NOTE: This will update the $DB_FILE variable
source ./convert_to_db_tif.sh ${DB_FILE} ${SOURCE_FILE}

if [[ "$IMPORT_MODE" == "$APPEND_RECORDS" ]]; then
    POST_STEP="-p 002-update_ua_records.sql"
elif [[ "$IMPORT_MODE" == "$CREATE_TABLE" ]]; then
    POST_STEP="-p 002-change_ua_table.sql"
fi

./import_to_db.sh -f ${DB_FILE} -t ${UA_TABLE} --out-db ${IMPORT_MODE} ${POST_STEP}
