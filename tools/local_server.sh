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

echo "Starting rethinkdb"
[ -d db/rethinkdb_data ] || rethinkdb create -d db/rethinkdb_data
rethinkdb serve -d db/rethinkdb_data &

echo "Starting compass watch"
compass watch --config conf/compass.rb &

echo "Starting flask server"
FLASK_CONFIG=../conf/flask_dev.py python web/server.py

# Only exit on terminate or interrupt signal
while true; do
  sleep 1
done
