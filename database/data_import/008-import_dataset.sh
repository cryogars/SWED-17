#!/usr/bin/env bash
#
# Import snow.nc file from iSnobal and store in the DB.
#
# Arguments:
#   -s: Path to file to import
#   -t: Table name to import data in
#   -d: Date of imported data
#   -c: Create table and import records
#   -a: Append records to table (Default)
#
# Example call for initial import:
#   import_dataset.sh -s _path_to_file_ -t table_name -c -d 20240101_
#
# Requires:
# * Configured ~/.pg_service.conf file with host, port, user, dbname

# -f = Prevent glob expansion when importing multiple files
set -ef

SCRIPT_PATH="$(dirname "$(realpath $0)")"
DB_CONNECT_OPTIONS='service=swe_db'

# Parse script options
source ${SCRIPT_PATH}/import_script_options.sh

if [[ "$IMPORT_MODE" == "$APPEND_RECORDS" ]]; then
    IMPORT_OPTIONS="-a"
elif [[ "$IMPORT_MODE" == "$CREATE_TABLE" ]]; then
    IMPORT_OPTIONS="-d -C -x -I -l 2,3"
    # Add post create table steps
    POST_STEP=$(sed "s/__tablename__/${TABLE}/g" "${SCRIPT_PATH}/008-update_db_table.sql")
fi
# Add post steps for new records
POST_STEP+=$(sed "s/__tablename__/${TABLE}/g" "${SCRIPT_PATH}/008-update_db_records.sql")

# Get the file date
[[ $DB_FILE =~ ([0-9]{8}) ]]
# Set date for post step
POST_STEP=${POST_STEP/_filedate_/"'${BASH_REMATCH[1]}'"}

# Import table into database
raster2pgsql ${IMPORT_OPTIONS} -M -Y -t 32x32 \
  ${SOURCE_FILE} ${TABLE} | \
  psql ${DB_CONNECT_OPTIONS}

# Update imported rows
psql ${DB_CONNECT_OPTIONS} -c "${POST_STEP}"

# Table maintenance after bigger import
psql ${DB_CONNECT_OPTIONS} -c "VACUUM FULL ${TABLE}"
