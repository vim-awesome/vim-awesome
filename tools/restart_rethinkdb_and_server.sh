#!/usr/bin/env bash

HOST="https://vimawesome.com"

echo "Restarting RethinkDB"
sudo service rethinkdb restart

echo "Gracefully reloading server"
kill -HUP $(cat $HOME/.gunicorn.pid)

echo "Warming up caches"
for i in {1..5}; do
  curl -s "$HOST" > /dev/null
  curl -s "$HOST/api/plugins?page=[1-10]" > /dev/null
done
