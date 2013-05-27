#!/bin/bash

# Bail on errors
set -e

function clean_up() {
  set +e
  kill 0
  exit
}

# Kill all child processes on script abort
trap clean_up SIGTERM SIGINT ERR

# TODO(david): Start rethinkdb, redis, etc.

echo "Starting compass watch"
compass watch --config conf/compass.rb &

echo "Starting flask server"
#FLASK_CONFIG=../config/flask_dev.py \
python web/server.py

# Only exit on terminate or interrupt signal
while true; do
  sleep 1
done
