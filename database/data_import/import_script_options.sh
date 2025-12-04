#!/usr/bin/env bash
#
# General script that supplies default options to all import scripts
#
# Provides the following options:
#   -a|--append: Add records to DB
#   -c|--create: Create table and import records to DB
#   -s|--source: Source file that holds the data
#   -d|--db-file: Converted source file as out-db file.

set -e

APPEND_RECORDS="-a"
CREATE_TABLE="-c"
# Default mode
IMPORT_MODE=$APPEND_RECORDS

# Required DB file name
DB_FILE_PATTERN="^([0-9]{8}_).*"

# Script argument options
LONG_OPTIONS=source:db-file:table:create,append
SHORT_OPTIONS=s:d:t:ca

# Parse arguments and set variables
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
        -s|--source)
            SOURCE_FILE="$2"
            shift 2
            ;;
        -d|--db-file)
            DB_FILE="$2"
            shift 2
            ;;
        -t|--table)
            TABLE="$2"
            shift 2
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

if [[ -z $SOURCE_FILE ]] || [[ -z $DB_FILE ]]; then
    echo "Missing required inputs of source and destination file" >&2
    exit 1
fi

FILE_CHECK=$(basename $DB_FILE)

if [[ ! "$FILE_CHECK" =~ $DB_FILE_PATTERN ]]; then
    echo "Destination file does not match required pattern YYYYMMDD_"
    echo "  Given: ${DB_FILE}"
    echo "  Needed: YYYYMMDD_"
    exit 1
fi
