#!/usr/bin/env bash

set -e

APP_HOME="/nvm9/data/dash_app"
ERROR_LOG="${APP_HOME}/logs/dash_error.log"

micromamba run -n dash \
  gunicorn \
    --workers=1 --threads=8 \
    --error-logfile ${ERROR_LOG} \
    --capture-output \
    --daemon \
    --pid "${APP_HOME}/gunicorn.pid" \
    --chdir ${APP_HOME} \
    --bind 0.0.0.0:8050 Snow17_vs_iSnobal:server &

sleep 3

tail ${ERROR_LOG}

