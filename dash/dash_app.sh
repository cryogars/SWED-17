#!/usr/bin/env bash

set -e

APP_HOME="/nvm9/data/dash_app"
ERROR_LOG="${APP_HOME}/logs/dash_error.log"
PID_FILE="${APP_HOME}/gunicorn.pid"

start() {
  micromamba run -n dash \
    gunicorn \
      --workers=1 --threads=8 \
      --error-logfile ${ERROR_LOG} \
      --capture-output \
      --daemon \
      --pid ${PID_FILE} \
      --chdir ${APP_HOME} \
      --bind 0.0.0.0:8050 Snow17_vs_iSnobal:server &

  sleep 3

  tail ${ERROR_LOG}
}

stop() {
  if [ -s "${PID_FILE}" ]; then
    kill $(cat ${PID_FILE})
  fi
}

restart() {
  stop
  sleep 2
  start
}

# Option parser
LONG_OPTIONS=start,stop,restart
HELP_TEXT="Usage: $0 [--start | --stop | --restart]"
ARGUMENTS=$(getopt -o '' --longoptions=${LONG_OPTIONS} --name $0 -- "$@") || exit 1
eval set -- "$ARGUMENTS"

while true; do
    case "$1" in
        --start)
            start
            shift
            ;;
        --stop)
            stop
            shift
            ;;
        --restart)
            restart
            shift
            ;;
        --)
            shift
            break
            ;;
        *)
            echo "${HELP_TEXT}"
            exit 1
            ;;
    esac
done

if [ "$#" -eq 0 ] && [ -z "$ARGUMENTS" ]; then
    echo "No options provided."
    echo "${HELP_TEXT}"
fi
