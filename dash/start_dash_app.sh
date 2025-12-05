#!/usr/bin/env bash

cd /nvm9/data/dash_app

micromamba run -n dash\
  gunicorn \
    --workers=1 --threads=8 \
    --error-logfile logs/dash_error.log \
    --capture-output \
    --daemon \
    --bind 0.0.0.0:8050 Snow17_vs_iSnobal:server &
